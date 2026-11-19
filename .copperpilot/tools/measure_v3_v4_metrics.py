#!/usr/bin/env python3
"""
Measure exact baseline/after metrics from KiCad 10 PCB filled_polygon rasterization
and pad/via geometry on bldc_motor_cntroller_v3 / _v4.
"""
import sys, math
import numpy as np
from pathlib import Path
from matplotlib.path import Path as MplPath
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
import pcbnew

# 1 oz copper at 20 C: rho_20C = 1.7241e-8 Ohm*m, t_1oz = 0.035 mm => 0.4926 mOhm/sq
# 2 oz copper at 20 C: t_2oz = 0.070 mm => 0.2463 mOhm/sq
R_SHEET_1OZ_MOHM = 1.7241e-2 / 0.035
R_SHEET_2OZ_MOHM = 1.7241e-2 / 0.070


def extract_filled_polygons_from_board(board, target_nets):
    layer_map = {
        "F.Cu": pcbnew.F_Cu,
        "B.Cu": pcbnew.B_Cu,
    }
    zones_data = []
    for z in board.Zones():
        net_name = z.GetNetname()
        if net_name not in target_nets:
            continue
        for lname, lid in layer_map.items():
            if not z.IsOnLayer(lid):
                continue
            pset = z.GetFilledPolysList(lid)
            for oi in range(pset.OutlineCount()):
                outline = pset.Outline(oi)
                opts = [(pcbnew.ToMM(outline.CPoint(k).x), pcbnew.ToMM(outline.CPoint(k).y)) for k in range(outline.PointCount())]
                holes = []
                for hi in range(pset.HoleCount(oi)):
                    hole = pset.Hole(oi, hi)
                    hpts = [(pcbnew.ToMM(hole.CPoint(k).x), pcbnew.ToMM(hole.CPoint(k).y)) for k in range(hole.PointCount())]
                    holes.append(hpts)
                if opts:
                    zones_data.append((net_name, lname, opts, holes))
    return zones_data


def rasterize_polygons(poly_tuples, x0, x1, y0, y1, dx=0.05):
    xs = np.arange(x0 + dx / 2, x1, dx)
    ys = np.arange(y0 + dx / 2, y1, dx)
    gx, gy = np.meshgrid(xs, ys)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    mask = np.zeros(len(pts), dtype=bool)
    for opts, holes in poly_tuples:
        arr = np.asarray(opts)
        if arr[:, 0].max() < x0 or arr[:, 0].min() > x1 or arr[:, 1].max() < y0 or arr[:, 1].min() > y1:
            continue
        sub = MplPath(opts).contains_points(pts)
        for hpts in holes:
            ha = np.asarray(hpts)
            if ha[:, 0].max() < x0 or ha[:, 0].min() > x1 or ha[:, 1].max() < y0 or ha[:, 1].min() > y1:
                continue
            sub &= ~MplPath(hpts).contains_points(pts)
        mask |= sub
    return xs, ys, mask.reshape(len(ys), len(xs))


def solve_resistance_squares(mask, src_mask, sink_mask):
    """Solve 2D Laplace equation on boolean grid `mask` between `src_mask` (V=1) and `sink_mask` (V=0)."""
    ny, nx = mask.shape
    active = mask.copy()
    src = src_mask & active
    snk = sink_mask & active
    if not src.any() or not snk.any():
        return float("inf")

    idx_map = -np.ones((ny, nx), dtype=np.int32)
    active_coords = np.argwhere(active)
    n_nodes = len(active_coords)
    idx_map[active_coords[:, 0], active_coords[:, 1]] = np.arange(n_nodes, dtype=np.int32)

    is_src = src[active_coords[:, 0], active_coords[:, 1]]
    is_snk = snk[active_coords[:, 0], active_coords[:, 1]]
    is_dir = is_src | is_snk

    int_ids = np.where(~is_dir)[0]
    int_r = active_coords[int_ids, 0]
    int_c = active_coords[int_ids, 1]

    rows, cols, vals = [], [], []
    diag = np.zeros(len(int_ids), dtype=np.float64)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = int_r + dr
        nc = int_c + dc
        valid = (nr >= 0) & (nr < ny) & (nc >= 0) & (nc < nx)
        v_idx = np.where(valid)[0]
        n_id = idx_map[nr[v_idx], nc[v_idx]]
        conn = n_id >= 0
        v_idx = v_idx[conn]
        n_id = n_id[conn]
        diag[v_idx] += 1.0
        rows.append(int_ids[v_idx])
        cols.append(n_id)
        vals.append(-np.ones(len(v_idx), dtype=np.float64))

    diag[diag == 0] = 1.0
    rows.append(int_ids)
    cols.append(int_ids)
    vals.append(diag)

    dir_ids = np.where(is_dir)[0]
    rows.append(dir_ids)
    cols.append(dir_ids)
    vals.append(np.ones(len(dir_ids), dtype=np.float64))

    rhs = np.zeros(n_nodes, dtype=np.float64)
    rhs[np.where(is_src)[0]] = 1.0

    A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n_nodes, n_nodes)).tocsr()
    V = spsolve(A, rhs)

    I_total = 0.0
    src_ids = np.where(is_src)[0]
    sr = active_coords[src_ids, 0]
    sc = active_coords[src_ids, 1]
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = sr + dr, sc + dc
        valid = (nr >= 0) & (nr < ny) & (nc >= 0) & (nc < nx)
        nid = idx_map[nr[valid], nc[valid]]
        ok = (nid >= 0)
        nid = nid[ok]
        not_s = ~is_src[nid]
        I_total += np.sum(1.0 - V[nid[not_s]])
    if I_total <= 1e-12:
        return float("inf")
    return 1.0 / I_total


def solve_multilayer_sh_resistance(mask_f, mask_b, src_f, sink_fb, via_centers, xs, ys, r_sheet_mohm, r_via_mohm=1.2):
    """Solve coupled 2-layer (F.Cu + B.Cu) sheet network with discrete stitching vias of resistance r_via_mohm."""
    ny, nx = mask_f.shape
    dx = xs[1] - xs[0]
    g_sheet = 1.0 / r_sheet_mohm  # mS per square

    idx_f = -np.ones((ny, nx), dtype=np.int32)
    idx_b = -np.ones((ny, nx), dtype=np.int32)
    cf = np.argwhere(mask_f)
    cb = np.argwhere(mask_b)
    nf = len(cf)
    nb = len(cb)
    n_tot = nf + nb
    idx_f[cf[:, 0], cf[:, 1]] = np.arange(nf, dtype=np.int32)
    idx_b[cb[:, 0], cb[:, 1]] = nf + np.arange(nb, dtype=np.int32)

    is_src = np.zeros(n_tot, dtype=bool)
    is_snk = np.zeros(n_tot, dtype=bool)
    is_src[:nf] = src_f[cf[:, 0], cf[:, 1]]
    is_snk[:nf] = sink_fb[cf[:, 0], cf[:, 1]]
    if nb > 0:
        is_snk[nf:] = sink_fb[cb[:, 0], cb[:, 1]]
    is_dir = is_src | is_snk

    rows, cols, vals = [], [], []
    diag = np.zeros(n_tot, dtype=np.float64)

    def add_layer_edges(coords, base_ids, idx_grid):
        ir = coords[:, 0]
        ic = coords[:, 1]
        not_d = ~is_dir[base_ids]
        sub_ids = base_ids[not_d]
        sr = ir[not_d]
        sc = ic[not_d]
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = sr + dr, sc + dc
            valid = (nr >= 0) & (nr < ny) & (nc >= 0) & (nc < nx)
            v_i = np.where(valid)[0]
            nid = idx_grid[nr[v_i], nc[v_i]]
            conn = nid >= 0
            v_i = v_i[conn]
            nid = nid[conn]
            np.add.at(diag, sub_ids[v_i], g_sheet)
            rows.append(sub_ids[v_i])
            cols.append(nid)
            vals.append(-g_sheet * np.ones(len(v_i), dtype=np.float64))

    add_layer_edges(cf, np.arange(nf, dtype=np.int32), idx_f)
    if nb > 0:
        add_layer_edges(cb, nf + np.arange(nb, dtype=np.int32), idx_b)
        gx, gy = np.meshgrid(xs, ys)
        for (vx, vy, vdrill) in via_centers:
            # couple barrel cells within r = vdrill/2 + 0.15 mm
            rv = max(vdrill / 2.0, 0.20)
            vm = ((gx - vx) ** 2 + (gy - vy) ** 2) <= rv ** 2
            vr, vc = np.where(vm & mask_f & mask_b)
            if len(vr) == 0:
                continue
            g_per_cell = (1.0 / r_via_mohm) / len(vr)
            for r0, c0 in zip(vr, vc):
                idf = idx_f[r0, c0]
                idb = idx_b[r0, c0]
                if not is_dir[idf]:
                    diag[idf] += g_per_cell
                    rows.append(np.array([idf], dtype=np.int32))
                    cols.append(np.array([idb], dtype=np.int32))
                    vals.append(np.array([-g_per_cell]))
                if not is_dir[idb]:
                    diag[idb] += g_per_cell
                    rows.append(np.array([idb], dtype=np.int32))
                    cols.append(np.array([idf], dtype=np.int32))
                    vals.append(np.array([-g_per_cell]))

    int_ids = np.where(~is_dir)[0]
    diag_int = diag[int_ids]
    diag_int[diag_int == 0] = 1.0
    rows.append(int_ids)
    cols.append(int_ids)
    vals.append(diag_int)

    dir_ids = np.where(is_dir)[0]
    rows.append(dir_ids)
    cols.append(dir_ids)
    vals.append(np.ones(len(dir_ids), dtype=np.float64))

    rhs = np.zeros(n_tot, dtype=np.float64)
    rhs[np.where(is_src)[0]] = 1.0

    A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n_tot, n_tot)).tocsr()
    V = spsolve(A, rhs)

    I_mA_per_V = 0.0  # since g_sheet is in 1/mOhm = S*1000 => V=1V gives current in kA! Wait: R = 1 / I_total where G in 1/mOhm -> R in mOhm!
    src_ids = np.where(is_src)[0]
    sr = cf[src_ids, 0]
    sc = cf[src_ids, 1]
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = sr + dr, sc + dc
        valid = (nr >= 0) & (nr < ny) & (nc >= 0) & (nc < nx)
        nid = idx_f[nr[valid], nc[valid]]
        nid = nid[nid >= 0]
        nid = nid[~is_src[nid]]
        I_mA_per_V += g_sheet * np.sum(1.0 - V[nid])
    if I_mA_per_V <= 1e-12:
        return float("inf")
    return 1.0 / I_mA_per_V


def pad_rect_mask(xs, ys, pads_info):
    gx, gy = np.meshgrid(xs, ys)
    m = np.zeros_like(gx, dtype=bool)
    for (px, py, sx, sy, shape_circle) in pads_info:
        if shape_circle:
            r = min(sx, sy) / 2.0
            m |= ((gx - px) ** 2 + (gy - py) ** 2) <= r ** 2
        else:
            m |= (np.abs(gx - px) <= sx / 2.0) & (np.abs(gy - py) <= sy / 2.0)
    return m


def main(pcb_path):
    board = pcbnew.LoadBoard(pcb_path)
    target_nets = {
        "/Motor Driver/SH_A", "/Motor Driver/SH_B", "/Motor Driver/SH_C",
        "/Motor_Driver2/SH_A", "/Motor_Driver2/SH_B", "/Motor_Driver2/SH_C",
        "VDC",
    }
    fpolys = extract_filled_polygons_from_board(board, target_nets)
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    vias = []
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            vias.append((t.GetNetname(), pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), pcbnew.ToMM(t.GetDrillValue())))

    def get_pads(ref, pad_names=None, net_filter=None):
        fp = fps[ref]
        out = []
        rot = fp.GetOrientationDegrees()
        for pad in fp.Pads():
            nm = pad.GetName()
            if nm == "":
                continue
            if pad_names is not None and nm not in pad_names:
                continue
            if net_filter is not None and pad.GetNetname() != net_filter:
                continue
            p = pad.GetPosition()
            sz = pad.GetSize()
            sx, sy = pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y)
            if abs(rot) in (90.0, 270.0):
                sx, sy = sy, sx
            is_circ = pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE
            out.append((pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), sx, sy, is_circ))
        return out

    print(f"=== METRICS FOR {pcb_path} ===")
    print(f"R_sheet(1oz, 20C) = {R_SHEET_1OZ_MOHM:.4f} mOhm/sq | R_sheet(2oz, 20C) = {R_SHEET_2OZ_MOHM:.4f} mOhm/sq")

    for bank, sh_cases in [
        ("M0 (Right)", [
            ("A", "/Motor Driver/SH_A", "Q1", "Q2", "J1", "1", 110, 136, 85, 112),
            ("B", "/Motor Driver/SH_B", "Q3", "Q4", "J1", "2", 101, 120, 85, 112),
            ("C", "/Motor Driver/SH_C", "Q5", "Q6", "J1", "3", 86, 110, 85, 112),
        ]),
        ("M1 (Left)", [
            ("A", "/Motor_Driver2/SH_A", "Q7", "Q8", "J2", "1", 40, 66, 85, 112),
            ("B", "/Motor_Driver2/SH_B", "Q9", "Q10", "J2", "2", 31, 50, 85, 112),
            ("C", "/Motor_Driver2/SH_C", "Q11", "Q12", "J2", "3", 16, 40, 85, 112),
        ]),
    ]:
        print(f"\n--- {bank} Phase Pours ---")
        for ph, net, q_hs, q_ls, j_ref, j_pad, x0, x1, y0, y1 in sh_cases:
            polys_f = [(opts, holes) for (n, l, opts, holes) in fpolys if n == net and l == "F.Cu"]
            polys_b = [(opts, holes) for (n, l, opts, holes) in fpolys if n == net and l == "B.Cu"]
            xs, ys, mask_f = rasterize_polygons(polys_f, x0, x1, y0, y1, dx=0.05)
            hs_src = pad_rect_mask(xs, ys, get_pads(q_hs, ["3", "4", "5", "6", "8"]))
            ls_drn = pad_rect_mask(xs, ys, get_pads(q_ls, ["1", "2", "9", "10"]))
            j_pads = get_pads(j_ref, [j_pad])
            j_msk = pad_rect_mask(xs, ys, j_pads)
            # PTH pad copper bridges where filled_polygon stops at pad/hole edge:
            # Wait: test BOTH pure filled_polygon AND filled_polygon | j_pad annular ring!
            j_hole_r = 3.30 / 2.0
            gx, gy = np.meshgrid(xs, ys)
            j_drill = ((gx - j_pads[0][0]) ** 2 + (gy - j_pads[0][1]) ** 2) <= j_hole_r ** 2
            mask_f_eff = (mask_f | j_msk) & (~j_drill)
            j_ring = j_msk & (~j_drill)

            sq_src = solve_resistance_squares(mask_f_eff, hs_src, j_ring)
            sq_drn = solve_resistance_squares(mask_f_eff, ls_drn, j_ring)
            r1_src = sq_src * R_SHEET_1OZ_MOHM
            r1_drn = sq_drn * R_SHEET_1OZ_MOHM

            _, _, mask_b = rasterize_polygons(polys_b, x0, x1, y0, y1, dx=0.05) if polys_b else (xs, ys, np.zeros_like(mask_f))
            mask_b_eff = (mask_b | j_msk) & (~j_drill) if polys_b else np.zeros_like(mask_f)
            sh_vias = [(vx, vy, vd) for (vn, vx, vy, vd) in vias if vn == net]
            r2_src = solve_multilayer_sh_resistance(mask_f_eff, mask_b_eff, hs_src, j_ring, sh_vias, xs, ys, R_SHEET_2OZ_MOHM)
            r2_drn = solve_multilayer_sh_resistance(mask_f_eff, mask_b_eff, ls_drn, j_ring, sh_vias, xs, ys, R_SHEET_2OZ_MOHM)

            print(
                f"  SH_{ph}: [1oz F.Cu only] src->J={sq_src:.2f} sq ({r1_src:.3f} mOhm), drn->J={sq_drn:.2f} sq ({r1_drn:.3f} mOhm)"
                f" | [2oz F+B+{len(sh_vias)}vias] src->J={r2_src:.3f} mOhm (I2R@40A={1600*r2_src*1e-3:.2f}W), drn->J={r2_drn:.3f} mOhm (I2R@40A={1600*r2_drn*1e-3:.2f}W)"
            )
            if bank.startswith("M0") and ph == "B":
                sub = mask_f[(ys >= 104.5) & (ys <= 109.0), :]
                w = sub.sum(axis=1) * 0.05
                print(f"    SH_B neck (y=104.5..109): min={w.min():.2f} mm, mean={w.mean():.2f} mm")
            if bank.startswith("M0") and ph == "C":
                sub = mask_f[(ys >= 98.0) & (ys <= 103.0), :]
                w = sub.sum(axis=1) * 0.05
                print(f"    SH_C neck (y=98..103):    min={w.min():.2f} mm, mean={w.mean():.2f} mm")

    # Min copper-to-copper gap among SH_A, SH_B, SH_C on F.Cu and B.Cu
    for lname in ["F.Cu", "B.Cu"]:
        pa = [(o, h) for (n, l, o, h) in fpolys if n == "/Motor Driver/SH_A" and l == lname]
        pb = [(o, h) for (n, l, o, h) in fpolys if n == "/Motor Driver/SH_B" and l == lname]
        pc = [(o, h) for (n, l, o, h) in fpolys if n == "/Motor Driver/SH_C" and l == lname]
        if pa and pb and pc:
            from scipy.ndimage import binary_erosion
            xg, yg, ma = rasterize_polygons(pa, 88, 134, 86, 111, dx=0.04)
            _, _, mb = rasterize_polygons(pb, 88, 134, 86, 111, dx=0.04)
            _, _, mc = rasterize_polygons(pc, 88, 134, 86, 111, dx=0.04)
            gx, gy = np.meshgrid(xg, yg)
            ba = ma & ~binary_erosion(ma)
            bb = mb & ~binary_erosion(mb)
            bc = mc & ~binary_erosion(mc)
            pts_a = np.column_stack([gx[ba], gy[ba]])
            pts_b = np.column_stack([gx[bb], gy[bb]])
            pts_c = np.column_stack([gx[bc], gy[bc]])
            g_bc = cKDTree(pts_b).query(pts_c, k=1)[0].min()
            g_ab = cKDTree(pts_a).query(pts_b, k=1)[0].min()
            print(f"\n{lname} SH gaps (M0): SH_B-to-SH_C = {g_bc:.3f} mm | SH_A-to-SH_B = {g_ab:.3f} mm")

    # 2. HS drain feed squares for all 6 HS FETs (Q1, Q3, Q5, Q7, Q9, Q11)
    print("\n--- HS Drain Feed (F.Cu VDC finger to VDC vias) ---")
    polys_vdc = [(o, h) for (n, l, o, h) in fpolys if n == "VDC" and l == "F.Cu"]
    for qref in ["Q1", "Q3", "Q5", "Q7", "Q9", "Q11"]:
        qx = pcbnew.ToMM(fps[qref].GetPosition().x)
        xv, yv, mvdc = rasterize_polygons(polys_vdc, qx - 7.0, qx + 4.5, 82.0, 95.5, dx=0.05)
        vv = [(vx, vy, 0.8, 0.8, True) for (vn, vx, vy, _) in vias if vn == "VDC" and (qx - 7.0) <= vx <= (qx + 4.5) and 82.0 <= vy <= 95.5]
        snk = pad_rect_mask(xv, yv, vv)
        p12 = pad_rect_mask(xv, yv, get_pads(qref, ["1", "2"]))
        p910 = pad_rect_mask(xv, yv, get_pads(qref, ["9", "10"]))
        sq12 = solve_resistance_squares(mvdc, p12, snk)
        sq910 = solve_resistance_squares(mvdc, p910, snk)
        # Finger width between y=88.5..91.5 on west side of FET
        sub = mvdc[(yv >= 88.5) & (yv <= 91.5), :][:, (xv >= qx - 6.0) & (xv <= qx - 1.0)]
        fw = sub.sum(axis=1) * 0.05
        # Vias beside pads 1,2 (y >= 91.5, within 4.5 mm of pads 1,2)
        p12_pts = get_pads(qref, ["1", "2"])
        near_v12 = [(vx, vy) for (vx, vy, _, _, _) in vv if vy >= 91.0 and min(math.hypot(vx - px, vy - py) for (px, py, _, _, _) in p12_pts) <= 4.5]
        print(f"  {qref} (x={qx:6.2f}): pads 1,2 = {sq12:.2f} sq, pads 9,10 = {sq910:.2f} sq | finger w(y=88.5..91.5)={fw.mean():.2f} mm | vias beside pads 1,2: {len(near_v12)}")

    # 3. Hot loops: LS source to nearest GND via, nearest bulk cap to HS drain
    print("\n--- Hot Loops & Bulk/HF Decoupling ---")
    gnd_vias = [(vx, vy) for (vn, vx, vy, _) in vias if vn == "GND"]
    for qref in ["Q2", "Q4", "Q6", "Q8", "Q10", "Q12"]:
        spads = get_pads(qref, ["3", "4", "5", "6", "8"])
        cx = sum(p[0] for p in spads) / len(spads)
        cy = sum(p[1] for p in spads) / len(spads)
        min_cent = min(math.hypot(cx - vx, cy - vy) for (vx, vy) in gnd_vias)
        min_pad = min(math.hypot(px - vx, py - vy) for (px, py, _, _, _) in spads for (vx, vy) in gnd_vias)
        print(f"  {qref} LS source -> nearest GND via: centroid={min_cent:.2f} mm, nearest_pad={min_pad:.2f} mm")

    bulk_refs = [r for r in fps if r.startswith("C") and "1206" in fps[r].GetFPID().GetUniStringLibId() and any(p.GetNetname() == "VDC" for p in fps[r].Pads())]
    bulk_vdc_pads = [(br, p[0], p[1]) for br in bulk_refs for p in get_pads(br, net_filter="VDC")]
    for qref in ["Q1", "Q3", "Q5", "Q7", "Q9", "Q11"]:
        dpads = get_pads(qref, ["1", "2", "9", "10"])
        # pad edge or center distance
        best_c = min((math.hypot(px - bx, py - by), br) for (px, py, _, _, _) in dpads for (br, bx, by) in bulk_vdc_pads)
        best_e = min((max(0.0, abs(px - bx) - sx / 2 - 0.625) ** 2 + max(0.0, abs(py - by) - sy / 2 - 0.875) ** 2, br) for (px, py, sx, sy, _) in dpads for (br, bx, by) in bulk_vdc_pads)
        print(f"  {qref} HS drain -> nearest 1206 VDC cap: center={best_c[0]:.2f} mm ({best_c[1]}), pad-edge={math.sqrt(best_e[0]):.2f} mm ({best_e[1]})")

    # 4. Aux half-bridge Q13/Q14
    print("\n--- Aux Half-Bridge (Q13/Q14) ---")
    for n, l, opts, holes in fpolys:
        if n == "VDC" and l == "F.Cu":
            arr = np.asarray(opts)
            if arr[:, 1].max() < 75:
                def p_area(p):
                    xa, ya = np.asarray(p)[:, 0], np.asarray(p)[:, 1]
                    return 0.5 * abs(np.dot(xa, np.roll(ya, 1)) - np.dot(ya, np.roll(xa, 1)))
                area = p_area(opts) - sum(p_area(h) for h in holes)
                v_in = [(vx, vy) for (vn, vx, vy, _) in vias if vn == "VDC" and MplPath(opts).contains_point((vx, vy))]
                print(f"  Q13 VDC F.Cu island area = {area:.2f} mm^2, VDC vias = {len(v_in)}: {v_in}")
    q14_src = get_pads("Q14", ["1", "2", "3"])
    c48_gnd = get_pads("C48", ["2"])
    near_q14 = [(vx, vy, round(min(math.hypot(vx - px, vy - py) for (px, py, _, _, _) in q14_src), 2)) for (vx, vy) in gnd_vias if min(math.hypot(vx - px, vy - py) for (px, py, _, _, _) in q14_src) <= 5.0]
    near_c48 = [(vx, vy, round(min(math.hypot(vx - px, vy - py) for (px, py, _, _, _) in c48_gnd), 2)) for (vx, vy) in gnd_vias if min(math.hypot(vx - px, vy - py) for (px, py, _, _, _) in c48_gnd) <= 5.0]
    print(f"  GND vias within 5 mm of Q14 source: {len(near_q14)} -> {near_q14}")
    print(f"  GND vias within 5 mm of C48 GND pad: {len(near_c48)} -> {near_c48}")

    # 5. Gate lengths (U1 -> Q1..Q6 and U2 -> Q7..Q12)
    print("\n--- Straight-Line Gate Lengths ---")
    for drv, fmap in [
        ("U1", [("Q1", "47"), ("Q2", "45"), ("Q3", "42"), ("Q4", "40"), ("Q5", "37"), ("Q6", "35")]),
        ("U2", [("Q7", "47"), ("Q8", "45"), ("Q9", "42"), ("Q10", "40"), ("Q11", "37"), ("Q12", "35")]),
    ]:
        u_pos = fps[drv].GetPosition()
        print(f"  {drv} at ({pcbnew.ToMM(u_pos.x):.2f}, {pcbnew.ToMM(u_pos.y):.2f}):")
        lens = {}
        for qref, upin in fmap:
            up = get_pads(drv, [upin])[0]
            qp = get_pads(qref, ["7"])[0]
            d = math.hypot(up[0] - qp[0], up[1] - qp[1])
            lens[qref] = d
            print(f"    {drv}.{upin} -> {qref}.7: {d:.2f} mm")
        pairs = list(fmap)
        for i in range(0, 6, 2):
            qhs, qls = pairs[i][0], pairs[i + 1][0]
            print(f"    Leg {qhs}/{qls} HS/LS mismatch: |{lens[qhs]:.2f} - {lens[qls]:.2f}| = {abs(lens[qhs] - lens[qls]):.2f} mm")


if __name__ == "__main__":
    main(sys.argv[1])
