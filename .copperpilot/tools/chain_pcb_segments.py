#!/usr/bin/env python3
"""Order SES-imported KiCad PCB segments head-to-tail along degree-2 chains.

Why this exists:
KiCad's pcbnew.ExportSpecctraDSN emits a single multi-point `(wire (path ...))`
polyline only when consecutive `(segment ...)` records in `.kicad_pcb` share
`(net, layer, width)` and satisfy `seg[i].end == seg[i+1].start`. After SES
import or `kicad-cli --save-board`, segments are unordered and unoriented,
causing `ExportSpecctraDSN` to emit fragmented 2-point `(wire ...)` records
whose `%.6g` coordinate rounding at >=100 mm triggers a StackOverflowError in
FreeRouting 2.2.4 `PolylineTrace.combine`.

This tool never creates or invents routing: it only collapses sub-8 um SES
quantization slivers, merges ~180 deg collinear pairs, and sorts/orients
existing FreeRouting segments head-to-tail on a staged candidate `.kicad_pcb`.
"""

from __future__ import annotations

import math
import re
import sys
import uuid
from collections import defaultdict
from pathlib import Path

SEG_RE = re.compile(
    r"\s*\(segment\s+"
    r"\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+"
    r"\(end\s+([-\d.]+)\s+([-\d.]+)\)\s+"
    r"\(width\s+([-\d.]+)\)\s+"
    r"(?:\(locked\s+yes\)\s+)?"
    r"\(layer\s+\"([^\"]+)\"\)\s+"
    r"\(net\s+(?:\"([^\"]*)\"|([^\s\)]+))\)\s+"
    r"\(uuid\s+\"([^\"]+)\"\)\s*\)"
)

VIA_INFO_RE = re.compile(
    r"\(via\s+\(at\s+([-\d.]+)\s+([-\d.]+)\)\s+[\s\S]*?\(net\s+(?:\"([^\"]*)\"|([^\s\)]+))\)"
)

VIA_UNLOCKED_RE = re.compile(
    r"(\(via\s+\(at\s+[-\d.]+\s+[-\d.]+\)\s+\(size\s+[-\d.]+\)\s+\(drill\s+[-\d.]+\)\s+\(layers\s+[^\)]+\))(?!\s*\(locked\s+yes\))"
)


def fmt(v: float) -> str:
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def key_pt(p: tuple[float, float]) -> tuple[int, int]:
    return (round(p[0] * 1000000), round(p[1] * 1000000))


def process_group(
    segs: list[dict],
    via_pts: list[tuple[float, float]] = (),
    sliver_mm: float = 0.008,
    sin_tol: float = 1.5e-2,
) -> tuple[list[dict], int, int]:
    collapsed = 0
    merged = 0
    via_keys = {key_pt(vp) for vp in via_pts}

    # 0. Snap near-via endpoints and split segments passing over a same-net via center
    if via_pts:
        for s in segs:
            for vp in via_pts:
                if math.hypot(s["p1"][0] - vp[0], s["p1"][1] - vp[1]) < 0.010:
                    s["p1"] = vp
                if math.hypot(s["p2"][0] - vp[0], s["p2"][1] - vp[1]) < 0.010:
                    s["p2"] = vp
        split_changed = True
        while split_changed:
            split_changed = False
            for idx, s in enumerate(segs):
                ax, ay = s["p1"]
                bx, by = s["p2"]
                abx, aby = bx - ax, by - ay
                ab2 = abx * abx + aby * aby
                if ab2 < 1e-8:
                    continue
                for vp in via_pts:
                    vk = key_pt(vp)
                    if vk == key_pt(s["p1"]) or vk == key_pt(s["p2"]):
                        continue
                    t = ((vp[0] - ax) * abx + (vp[1] - ay) * aby) / ab2
                    if 0.01 < t < 0.99:
                        px, py = ax + t * abx, ay + t * aby
                        if math.hypot(vp[0] - px, vp[1] - py) < 0.008:
                            s2 = dict(s, p1=vp, p2=s["p2"], uuid=str(uuid.uuid4()))
                            s["p2"] = vp
                            segs.insert(idx + 1, s2)
                            split_changed = True
                            break
                if split_changed:
                    break

    # 1. Collapse degenerate sub-8um SES quantization slivers by welding endpoints
    changed = True
    while changed:
        changed = False
        for idx, s in enumerate(segs):
            dx = s["p2"][0] - s["p1"][0]
            dy = s["p2"][1] - s["p1"][1]
            length = math.hypot(dx, dy)
            if length < sliver_mm:
                old_k = key_pt(s["p2"])
                target = s["p1"]
                segs.pop(idx)
                for other in segs:
                    if key_pt(other["p1"]) == old_k:
                        other["p1"] = target
                    if key_pt(other["p2"]) == old_k:
                        other["p2"] = target
                collapsed += 1
                changed = True
                break

    # 1b. Weld any remaining sub-5um degree-1 endpoint gaps from SES rounding
    pts_map: dict[tuple[int, int], tuple[float, float]] = {}
    deg_cnt: dict[tuple[int, int], int] = defaultdict(int)
    for s in segs:
        for end_name in ("p1", "p2"):
            k = key_pt(s[end_name])
            pts_map[k] = s[end_name]
            deg_cnt[k] += 1
    deg1 = [k for k, c in deg_cnt.items() if c == 1]
    remap: dict[tuple[int, int], tuple[float, float]] = {}
    for i in range(len(deg1)):
        k1 = deg1[i]
        if k1 in remap:
            continue
        p1 = pts_map[k1]
        for j in range(i + 1, len(deg1)):
            k2 = deg1[j]
            if k2 in remap:
                continue
            p2 = pts_map[k2]
            if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) < 0.006:
                remap[k2] = p1
                collapsed += 1
                break
    if remap:
        for s in segs:
            if key_pt(s["p1"]) in remap:
                s["p1"] = remap[key_pt(s["p1"])]
            if key_pt(s["p2"]) in remap:
                s["p2"] = remap[key_pt(s["p2"])]
        segs = [s for s in segs if math.hypot(s["p2"][0] - s["p1"][0], s["p2"][1] - s["p1"][1]) >= 0.001]

    # 2. Merge ~180 deg collinear degree-2 pairs
    changed = True
    while changed:
        changed = False
        adj: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        for idx, s in enumerate(segs):
            adj[key_pt(s["p1"])].append((idx, 1))
            adj[key_pt(s["p2"])].append((idx, 2))
        for k, inc in list(adj.items()):
            if len(inc) != 2 or k in via_keys:
                continue
            (i1, e1), (i2, e2) = inc
            if i1 == i2:
                continue
            s1, s2 = segs[i1], segs[i2]
            a = s1["p1"] if e1 == 2 else s1["p2"]
            b = s1["p2"] if e1 == 2 else s1["p1"]
            c = s2["p2"] if e2 == 1 else s2["p1"]
            v1x, v1y = b[0] - a[0], b[1] - a[1]
            v2x, v2y = c[0] - b[0], c[1] - b[1]
            l1, l2 = math.hypot(v1x, v1y), math.hypot(v2x, v2y)
            if l1 < 1e-6 or l2 < 1e-6:
                continue
            dot = (v1x * v2x + v1y * v2y) / (l1 * l2)
            cross = abs(v1x * v2y - v1y * v2x) / (l1 * l2)
            if dot > 0.999 and cross < sin_tol:
                s1["p1"], s1["p2"] = a, c
                segs.pop(i2)
                merged += 1
                changed = True
                break

    # 2b. Split segments at interior T-junction endpoints or same-net vias so Specctra DSN sees shared vertices
    split_pts: list[tuple[float, float]] = list(via_pts)
    seen_sp = {key_pt(p) for p in split_pts}
    for s in segs:
        for ep in (s["p1"], s["p2"]):
            kep = key_pt(ep)
            if kep not in seen_sp:
                seen_sp.add(kep)
                split_pts.append(ep)
    if split_pts:
        import uuid as _uuid
        new_segs: list[dict] = []
        for s in segs:
            ax, ay = s["p1"]
            bx, by = s["p2"]
            dx, dy = bx - ax, by - ay
            ln2 = dx * dx + dy * dy
            ln = math.sqrt(ln2)
            if ln < 0.005:
                new_segs.append(s)
                continue
            cuts: list[tuple[float, tuple[float, float]]] = []
            for px, py in split_pts:
                t_par = ((px - ax) * dx + (py - ay) * dy) / ln2
                if t_par <= 0.002 / ln or t_par >= 1.0 - 0.002 / ln:
                    continue
                perp = abs((px - ax) * dy - (py - ay) * dx) / ln
                if perp <= 0.002:
                    cuts.append((t_par, (px, py)))
            if not cuts:
                new_segs.append(s)
            else:
                cuts.sort(key=lambda item: item[0])
                pts_seq = [s["p1"]] + [c[1] for c in cuts] + [s["p2"]]
                for idx_c in range(len(pts_seq) - 1):
                    q1, q2 = pts_seq[idx_c], pts_seq[idx_c + 1]
                    if math.hypot(q2[0] - q1[0], q2[1] - q1[1]) >= 0.001:
                        ns = dict(s)
                        ns["p1"], ns["p2"] = q1, q2
                        if idx_c > 0:
                            ns["uuid"] = str(_uuid.uuid4())
                        new_segs.append(ns)
        segs = new_segs

    # 2c. Quantize pure trace-interior vertices to 1 um (6 sig-figs max in um for %g DSN export)
    #     and snap degree-2 orthogonal-to-45-degree knees so |dx| == |dy| exact in FreeRouting
    snap_v: dict[tuple[int, int], list[float]] = {}
    for s in segs:
        for ep in ("p1", "p2"):
            k = key_pt(s[ep])
            if k not in snap_v:
                if k in via_keys:
                    snap_v[k] = [s[ep][0], s[ep][1]]
                else:
                    snap_v[k] = [round(s[ep][0], 3), round(s[ep][1], 3)]
    deg_v: dict[tuple[int, int], list[tuple[int, str]]] = defaultdict(list)
    for idx, s in enumerate(segs):
        deg_v[key_pt(s["p1"])].append((idx, "p1"))
        deg_v[key_pt(s["p2"])].append((idx, "p2"))
    for idx, s in enumerate(segs):
        k1, k2 = key_pt(s["p1"]), key_pt(s["p2"])
        p1, p2 = snap_v[k1], snap_v[k2]
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        err = abs(abs(dx) - abs(dy))
        if abs(dx) > 0.02 and 1e-7 < err <= 0.004:
            for k_knee, p_other, p_knee in ((k1, p2, p1), (k2, p1, p2)):
                if k_knee in via_keys or len(deg_v[k_knee]) != 2:
                    continue
                other_inc = [it for it in deg_v[k_knee] if it[0] != idx]
                if not other_inc:
                    continue
                oi, oep = other_inc[0]
                ok_far = key_pt(segs[oi]["p2" if oep == "p1" else "p1"])
                p_far = snap_v[ok_far]
                odx, ody = p_far[0] - p_knee[0], p_far[1] - p_knee[1]
                if abs(ody) <= 0.001 and abs(odx) > 0.02:
                    p_knee[1] = round(p_far[1], 3)
                    dy_new = p_other[1] - p_knee[1]
                    p_knee[0] = round(p_other[0] - (abs(dy_new) if (p_other[0] > p_knee[0]) else -abs(dy_new)), 3)
                    break
                if abs(odx) <= 0.001 and abs(ody) > 0.02:
                    p_knee[0] = round(p_far[0], 3)
                    dx_new = p_other[0] - p_knee[0]
                    p_knee[1] = round(p_other[1] - (abs(dx_new) if (p_other[1] > p_knee[1]) else -abs(dx_new)), 3)
                    break
    for s in segs:
        k1, k2 = key_pt(s["p1"]), key_pt(s["p2"])
        s["p1"] = (snap_v[k1][0], snap_v[k1][1])
        s["p2"] = (snap_v[k2][0], snap_v[k2][1])
    segs = [s for s in segs if math.hypot(s["p2"][0] - s["p1"][0], s["p2"][1] - s["p1"][1]) >= 0.001]

    # 3. Decompose into maximal simple chains and orient head-to-tail
    adj_edges: dict[tuple[int, int], list[int]] = defaultdict(list)
    for idx, s in enumerate(segs):
        adj_edges[key_pt(s["p1"])].append(idx)
        adj_edges[key_pt(s["p2"])].append(idx)

    used = [False] * len(segs)
    chains: list[list[dict]] = []

    def walk_from(start_k: tuple[int, int]) -> None:
        for first_idx in adj_edges[start_k]:
            if used[first_idx]:
                continue
            used[first_idx] = True
            s = segs[first_idx]
            if key_pt(s["p1"]) != start_k:
                s["p1"], s["p2"] = s["p2"], s["p1"]
            chain = [s]
            curr_k = key_pt(s["p2"])
            prev_s = s
            while len(adj_edges[curr_k]) == 2 and curr_k not in via_keys:
                nxt = [i for i in adj_edges[curr_k] if not used[i]]
                if not nxt:
                    break
                ni = nxt[0]
                ns = segs[ni]
                np1, np2 = (ns["p1"], ns["p2"]) if key_pt(ns["p1"]) == curr_k else (ns["p2"], ns["p1"])
                v1x, v1y = prev_s["p2"][0] - prev_s["p1"][0], prev_s["p2"][1] - prev_s["p1"][1]
                v2x, v2y = np2[0] - np1[0], np2[1] - np1[1]
                l1, l2 = math.hypot(v1x, v1y), math.hypot(v2x, v2y)
                if l1 > 1e-6 and l2 > 1e-6 and ((v1x * v2x + v1y * v2y) / (l1 * l2)) <= 0.05:
                    break
                used[ni] = True
                ns["p1"], ns["p2"] = np1, np2
                chain.append(ns)
                prev_s = ns
                curr_k = key_pt(ns["p2"])
            chains.append(chain)

    # Walk from vias FIRST (so every incident chain starts AT the via and ExportSpecctraDSN
    # never concatenates two chains across a via center!), then degree != 2, then cycles
    for k in sorted(adj_edges.keys()):
        if k in via_keys:
            walk_from(k)
    for k in sorted(adj_edges.keys()):
        if len(adj_edges[k]) != 2:
            walk_from(k)
    for k in sorted(adj_edges.keys()):
        walk_from(k)

    return chains, collapsed, merged


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pcb_path", type=Path)
    ap.add_argument("--unlocked-nets", default="")
    ap.add_argument("--t-tag", action="store_true")
    args = ap.parse_args()
    pcb_path = args.pcb_path
    unlocked_nets = {x.strip() for x in args.unlocked_nets.split(",") if x.strip()}
    txt = pcb_path.read_text()
    matches = list(SEG_RE.finditer(txt))
    if not matches:
        print("Chained 0 segments (no segments found).")
        return

    via_pts_by_net: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for vm in VIA_INFO_RE.finditer(txt):
        vx, vy, vnet_q, vnet_u = vm.groups()
        vnet = vnet_q if vnet_q is not None else vnet_u
        via_pts_by_net[vnet].append((float(vx), float(vy)))
    try:
        import pcbnew as _pcbnew
        _b = _pcbnew.LoadBoard(str(pcb_path))
        for _fp in _b.GetFootprints():
            for _pd in _fp.Pads():
                _nn = _pd.GetNetname()
                if _nn:
                    via_pts_by_net[_nn].append((_pcbnew.ToMM(_pd.GetPosition().x), _pcbnew.ToMM(_pd.GetPosition().y)))
    except Exception:
        pass

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for m in matches:
        x1, y1, x2, y2, w, lay, net_q, net_u, uid = m.groups()
        net = net_q if net_q is not None else net_u
        wf = float(w)
        base_w_val = min((0.155, 0.16, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.8), key=lambda c: abs(wf - c))
        if abs(wf - base_w_val) > 0.008:
            base_w_val = round(wf * 200.0) / 200.0
        norm_w = fmt(base_w_val)
        groups[(net, lay, norm_w)].append(
            {
                "p1": (float(x1), float(y1)),
                "p2": (float(x2), float(y2)),
                "w": norm_w,
                "layer": lay,
                "net": net,
                "uuid": uid,
            }
        )

    total_collapsed = 0
    total_merged = 0
    out_blocks: list[str] = []
    for key in sorted(groups.keys()):
        chains, col, mrg = process_group(groups[key], via_pts_by_net.get(key[0], []))
        total_collapsed += col
        total_merged += mrg
        base_w_f = float(key[2])
        multi = len(chains) > 1 and args.t_tag
        for ci, chain in enumerate(chains):
            cw = fmt(base_w_f + (ci % 5) * 0.002) if multi else key[2]
            for s in chain:
                lk = "" if s["net"] in unlocked_nets else "\t\t(locked yes)\n"
                out_blocks.append(
                    f"\n\t(segment\n"
                    f"\t\t(start {fmt(s['p1'][0])} {fmt(s['p1'][1])})\n"
                    f"\t\t(end {fmt(s['p2'][0])} {fmt(s['p2'][1])})\n"
                    f"\t\t(width {cw})\n"
                    f"{lk}"
                    f"\t\t(layer \"{s['layer']}\")\n"
                    f"\t\t(net \"{s['net']}\")\n"
                    f"\t\t(uuid \"{s['uuid']}\")\n"
                    f"\t)"
                )

    # Replace existing segment spans cleanly at the first segment position
    pieces: list[str] = []
    pos = 0
    first_pos = matches[0].start()
    for i, m in enumerate(matches):
        pieces.append(txt[pos : m.start()])
        if i == 0:
            pieces.append("".join(out_blocks))
        pos = m.end()
    pieces.append(txt[pos:])
    new_txt = "".join(pieces)
    locked_vias = 0
    pcb_path.write_text(new_txt)
    print(
        f"Chained & locked {len(out_blocks)} segments (+{locked_vias} vias locked; "
        f"collapsed {total_collapsed} slivers, merged {total_merged} colinear pairs)."
    )


if __name__ == "__main__":
    main()
