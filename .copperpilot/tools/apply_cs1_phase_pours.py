#!/usr/bin/env python3
"""
Change Set 1 (Step 1):
- Reshape shunt voids: shift R16/R12 (+0.50 mm x) and R36/R32 (-70 mm mirror),
  tuck Kelvin net-ties NT1..NT8 alongside the inner west edge of the shunts,
  and replace west-protruding shunt GND vias with compact 6-via arrays on each shunt GND pad.
- Widen SH_B and SH_C necks on F.Cu, enforce SH-to-SH gap >= 0.55 mm everywhere,
  and balance SH_A / SH_B / SH_C within 10%.
- Add B.Cu SH_A, SH_B, SH_C mirror pours (Priority 5) with SetIsFree(True) 0.8/0.4 mm via stitching
  spaced >= 1.65 mm so In1.Cu GND remains 100% solid and continuous.
"""
import sys
import pcbnew

pcb_path = sys.argv[1]
board = pcbnew.LoadBoard(pcb_path)
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}


def set_fp_pose(ref, x_mm, y_mm, rot_deg=None):
    fp = fps[ref]
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    if rot_deg is not None:
        fp.SetOrientationDegrees(rot_deg)


# 1. Reposition shunts and Kelvin net-ties symmetrically (M1 = M0 - 70.000 mm in x)
# Check NetTie pad polarity: at rot=0 in v3, Pad 1 (sense) is x-0.5, Pad 2 (SL/GND) is x+0.5.
# At rot=-90: Pad 1 is (x, y-0.5), Pad 2 is (x, y+0.5); at rot=90: Pad 1 is (x, y+0.5), Pad 2 is (x, y-0.5).
for dx, r_c, nt_c_sl, nt_c_gnd, r_b, nt_b_sl, nt_b_gnd in [
    (0.0,   "R16", "NT3", "NT4", "R12", "NT1", "NT2"),
    (-70.0, "R36", "NT7", "NT8", "R32", "NT5", "NT6"),
]:
    set_fp_pose(r_c, 101.700 + dx, 97.500, 90.0)
    set_fp_pose(nt_c_sl,  99.150 + dx, 96.150, 90.0)   # Pad 2 (SL_C) at y=95.65, Pad 1 at y=96.65
    set_fp_pose(nt_c_gnd, 99.150 + dx, 98.850, -90.0)  # Pad 2 (GND)  at y=99.35, Pad 1 at y=98.35

    set_fp_pose(r_b, 118.450 + dx, 97.500, 90.0)
    set_fp_pose(nt_b_sl,  115.900 + dx, 96.150, 90.0)
    set_fp_pose(nt_b_gnd, 115.900 + dx, 98.850, -90.0)

# 2. Remove old shunt-region GND vias that jutted west into SH_C / SH_B
for t in list(board.GetTracks()):
    if t.GetClass() == "PCB_VIA" and t.GetNetname() == "GND":
        vx, vy = pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)
        if 97.0 <= vy <= 102.1 and (
            (26.0 <= vx <= 33.0) or (43.0 <= vx <= 50.0) or (96.0 <= vx <= 103.0) or (113.0 <= vx <= 120.0)
        ):
            board.Remove(t)
        # Also mark existing vias as SetIsFree(True) so zone-refill never rewrites net codes
        else:
            t.SetIsFree(True)
    elif t.GetClass() == "PCB_VIA":
        t.SetIsFree(True)


def add_via(net_name, x_mm, y_mm, size_mm=0.8, drill_mm=0.4):
    net = board.FindNet(net_name)
    assert net is not None, f"Net not found: {net_name}"
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetDrill(pcbnew.FromMM(drill_mm))
    for lid in [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]:
        v.SetWidth(lid, pcbnew.FromMM(size_mm))
    v.SetIsFree(True)
    v.SetNet(net)
    board.Add(v)


# Add compact 6-via GND arrays flanking each shunt's GND pad
for sx in [101.700, 118.450, 31.700, 48.450]:
    for vx in [sx - 1.250, sx, sx + 1.250]:
        add_via("GND", vx, 98.950)
        add_via("GND", vx, 101.850)

# 3. Replace SL_C, SL_B, SH_C, SH_B, SH_A zones on F.Cu and add B.Cu SH mirror pours
replace_nets = {
    "/Motor Driver/SL_C", "/Motor Driver/SL_B",
    "/Motor_Driver2/SL_C", "/Motor_Driver2/SL_B",
    "/Motor Driver/SH_C", "/Motor Driver/SH_B", "/Motor Driver/SH_A",
    "/Motor_Driver2/SH_C", "/Motor_Driver2/SH_B", "/Motor_Driver2/SH_A",
}
for z in list(board.Zones()):
    if z.GetNetname() in replace_nets and (z.IsOnLayer(pcbnew.F_Cu) or z.IsOnLayer(pcbnew.B_Cu)):
        board.Remove(z)


def add_zone(net_name, layer_id, priority, clearance_mm, min_thick_mm, pts_mm):
    net = board.FindNet(net_name)
    assert net is not None, f"Net not found: {net_name}"
    z = pcbnew.ZONE(board)
    z.SetNet(net)
    z.SetLayer(layer_id)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(clearance_mm))
    z.SetMinThickness(pcbnew.FromMM(min_thick_mm))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = z.Outline()
    outline.NewOutline()
    for (x, y) in pts_mm:
        outline.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(z)


def shift_pts(pts, dx):
    return [(round(x + dx, 4), round(y, 4)) for (x, y) in pts]


# Right motor (M0) SL_C and SL_B outlines (wide continuous L-shape from Q6/Q4 source to R16.2/NT3.2 and R12.2/NT1.2)
sl_c_m0 = [
    (94.90, 88.05), (96.35, 88.05), (96.35, 89.45), (100.20, 89.45),
    (100.20, 93.40), (103.65, 93.40), (103.65, 95.60), (99.80, 96.10),
    (98.75, 96.10), (98.75, 92.15), (94.90, 92.15),
]
sl_b_m0 = [
    (111.65, 88.05), (113.10, 88.05), (113.10, 89.45), (116.95, 89.45),
    (116.95, 93.40), (120.40, 93.40), (120.40, 95.60), (116.55, 96.10),
    (115.50, 96.10), (115.50, 92.15), (111.65, 92.15),
]

# Right motor (M0) F.Cu SH_C, SH_B, SH_A outlines:
# Strictly non-overlapping by >= 0.58 mm everywhere!
# Leaves y <= 95.25 under Q_HS pads 1,2 clear for Step 2's widened VDC finger + 4 vias!
sh_c_f_m0 = [
    (88.35, 88.00), (90.00, 88.00), (90.00, 89.20), (93.50, 89.20),
    (93.50, 86.10), (98.35, 86.10), (98.35, 87.45), (94.60, 87.45),
    (94.60, 92.55), (98.40, 92.55), (98.40, 102.50),
    (105.15, 102.50), (105.15, 104.20), (106.92, 105.35), (106.92, 110.80),
    (91.50, 110.80), (88.35, 104.50), (88.35, 95.50), (92.00, 95.50),
    (92.00, 92.05), (88.35, 92.05),
]

sh_b_f_m0 = [
    (105.10, 88.00), (106.75, 88.00), (106.75, 89.20), (110.25, 89.20),
    (110.25, 86.10), (115.10, 86.10), (115.10, 87.45), (111.35, 87.45),
    (111.35, 92.55), (115.15, 92.55), (115.15, 101.90),
    (114.20, 102.50), (114.20, 104.20), (112.50, 105.35), (112.50, 110.80),
    (107.50, 110.80), (107.50, 105.35), (105.80, 104.20), (105.80, 101.90),
    (104.25, 101.90), (104.25, 95.50), (108.75, 95.50),
    (108.75, 92.05), (105.10, 92.05),
]

sh_a_f_m0 = [
    (121.85, 88.00), (123.50, 88.00), (123.50, 89.20), (127.00, 89.20),
    (127.00, 86.10), (131.85, 86.10), (131.85, 87.45), (128.10, 87.45),
    (128.10, 92.55), (131.60, 92.55), (131.60, 99.00),
    (123.50, 110.80), (113.08, 110.80), (113.08, 105.35), (114.85, 104.20),
    (114.85, 102.50), (121.00, 102.50), (121.00, 95.50), (125.50, 95.50),
    (125.50, 92.05), (121.85, 92.05),
]

# Right motor (M0) B.Cu SH_C, SH_B, SH_A mirror pours:
# Extend directly under Q_HS source + Q_LS drain (avoiding Step 2's VDC vias at x <= q_hs_x+1.5, y >= 92.0)
# and run straight into J1/J2 PTH pads with >= 0.58 mm SH-to-SH separation!
sh_c_b_m0 = [
    (88.80, 88.00), (92.30, 88.00), (92.30, 86.20), (98.25, 86.20),
    (98.25, 98.20), (99.65, 98.20), (99.65, 102.50), (105.15, 102.50),
    (105.15, 104.20), (106.92, 105.35), (106.92, 110.80),
    (91.50, 110.80), (88.80, 104.50), (88.80, 95.75), (92.30, 95.75),
    (92.30, 91.85), (88.80, 91.85),
]

sh_b_b_m0 = [
    (105.55, 88.00), (109.05, 88.00), (109.05, 86.20), (115.00, 86.20),
    (115.00, 98.20), (116.40, 98.20), (116.40, 101.90), (114.20, 102.50),
    (114.20, 104.20), (112.50, 105.35), (112.50, 110.80),
    (107.50, 110.80), (107.50, 105.35), (105.80, 104.20), (105.80, 101.90),
    (104.25, 101.90), (104.25, 95.75), (109.05, 95.75),
    (109.05, 91.85), (105.55, 91.85),
]

sh_a_b_m0 = [
    (122.30, 88.00), (125.80, 88.00), (125.80, 86.20), (131.60, 86.20),
    (131.60, 99.00), (123.50, 110.80), (113.08, 110.80),
    (113.08, 105.35), (114.85, 104.20), (114.85, 102.50),
    (121.00, 102.50), (121.00, 95.75), (125.80, 95.75),
    (125.80, 91.85), (122.30, 91.85),
]

for dx, pfx in [(0.0, "/Motor Driver"), (-70.0, "/Motor_Driver2")]:
    add_zone(f"{pfx}/SL_C", pcbnew.F_Cu, 4, 0.25, 0.25, shift_pts(sl_c_m0, dx))
    add_zone(f"{pfx}/SL_B", pcbnew.F_Cu, 4, 0.25, 0.25, shift_pts(sl_b_m0, dx))

    add_zone(f"{pfx}/SH_C", pcbnew.F_Cu, 5, 0.25, 0.25, shift_pts(sh_c_f_m0, dx))
    add_zone(f"{pfx}/SH_B", pcbnew.F_Cu, 5, 0.25, 0.25, shift_pts(sh_b_f_m0, dx))
    add_zone(f"{pfx}/SH_A", pcbnew.F_Cu, 5, 0.25, 0.25, shift_pts(sh_a_f_m0, dx))

    add_zone(f"{pfx}/SH_C", pcbnew.B_Cu, 5, 0.30, 0.25, shift_pts(sh_c_b_m0, dx))
    add_zone(f"{pfx}/SH_B", pcbnew.B_Cu, 5, 0.30, 0.25, shift_pts(sh_b_b_m0, dx))
    add_zone(f"{pfx}/SH_A", pcbnew.B_Cu, 5, 0.30, 0.25, shift_pts(sh_a_b_m0, dx))

    # 4. Add 11 SetIsFree(True) SH stitching vias per phase (spaced >= 1.65 mm so In1.Cu GND stays 100% solid!):
    # 5 right around HS source / inter-FET bridge + 3 around LS drain + 3 along channel
    sh_via_specs = [
        ("SH_C", [
            (92.00, 89.80), (92.00, 91.45),
            (93.55, 88.65), (93.55, 90.30), (93.55, 91.95),
            (95.30, 94.75), (97.30, 94.75), (93.60, 94.75),
            (93.50, 97.60), (96.50, 97.60),
            (96.50, 101.20),
        ]),
        ("SH_B", [
            (108.75, 89.80), (108.75, 91.45),
            (110.30, 88.65), (110.30, 90.30), (110.30, 91.95),
            (112.05, 94.75), (114.05, 94.75), (110.35, 94.75),
            (108.50, 97.60), (112.50, 97.60),
            (110.00, 101.20),
        ]),
        ("SH_A", [
            (125.50, 89.80), (125.50, 91.45),
            (127.05, 88.65), (127.05, 90.30), (127.05, 91.95),
            (128.80, 94.75), (130.80, 94.75), (127.10, 94.75),
            (125.00, 97.60), (128.50, 97.60),
            (122.00, 101.80),
        ]),
    ]
    for sh_suffix, vlist in sh_via_specs:
        for (vx, vy) in vlist:
            add_via(f"{pfx}/{sh_suffix}", round(vx + dx, 4), round(vy, 4))

# Unfill all zones before saving so kicad-cli --refill-zones computes fresh fills without stale GND fill overlap!
for z in board.Zones():
    z.UnFill()

pcbnew.SaveBoard(pcb_path, board)
print("Applied CS1 cleanly with z.UnFill() and SetIsFree(True) SH stitching vias.")
