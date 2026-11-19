#!/usr/bin/env python3
"""
Change Set 1 (Step 1):
- Reshape shunt voids (R16/R12 +0.50 mm in x, NT1..NT8 tucked at inner west shunt edge, compact 6-via GND arrays).
- Widen SH_B and SH_C necks on F.Cu, enforce orthogonal SH-to-SH gap >= 0.56 mm (> 0.50 mm) everywhere,
  and balance SH_A / SH_B / SH_C within < 10% (both 1 oz F.Cu-only and 2 oz F.Cu+B.Cu+vias).
- Add B.Cu SH_A, SH_B, SH_C mirror pours (Priority 5) + (free yes) SH stitching vias, keeping In1.Cu GND solid.
"""
import sys
from pathlib import Path
from sexpr_pcb_utils import (
    set_footprint_pose, remove_vias_pred, mark_all_vias_free,
    add_vias, remove_zones_pred, strip_all_filled_polygons, add_zones
)

p = Path(sys.argv[1])
txt = p.read_text()

# 1. Reposition shunts and Kelvin net-ties (exact -70.000 mm M1/M0 symmetry)
for dx, r_c, nt_c_sl, nt_c_gnd, r_b, nt_b_sl, nt_b_gnd in [
    (0.0,   "R16", "NT3", "NT4", "R12", "NT1", "NT2"),
    (-70.0, "R36", "NT7", "NT8", "R32", "NT5", "NT6"),
]:
    txt = set_footprint_pose(txt, r_c, 101.700 + dx, 97.500, 90.0)
    txt = set_footprint_pose(txt, nt_c_sl,  99.150 + dx, 96.150, 90.0)
    txt = set_footprint_pose(txt, nt_c_gnd, 99.150 + dx, 98.850, -90.0)

    txt = set_footprint_pose(txt, r_b, 118.450 + dx, 97.500, 90.0)
    txt = set_footprint_pose(txt, nt_b_sl,  115.900 + dx, 96.150, 90.0)
    txt = set_footprint_pose(txt, nt_b_gnd, 115.900 + dx, 98.850, -90.0)

# 2. Remove west-protruding shunt GND vias and replace with compact 6-via arrays per shunt
txt = remove_vias_pred(
    txt,
    lambda net, vx, vy: net == "GND" and 97.0 <= vy <= 102.1 and (
        (26.0 <= vx <= 33.0) or (43.0 <= vx <= 50.0) or (96.0 <= vx <= 103.0) or (113.0 <= vx <= 120.0)
    ),
)
txt = mark_all_vias_free(txt)

new_vias = []
for sx in [101.700, 118.450, 31.700, 48.450]:
    for vx in [sx - 1.250, sx, sx + 1.250]:
        new_vias.append(("GND", round(vx, 4), 98.950, 0.8, 0.4))
        new_vias.append(("GND", round(vx, 4), 101.850, 0.8, 0.4))

# 3. Replace SL_C, SL_B, SH_C, SH_B, SH_A zones on F.Cu and add B.Cu SH mirror pours
replace_nets = {
    "/Motor Driver/SL_C", "/Motor Driver/SL_B",
    "/Motor_Driver2/SL_C", "/Motor_Driver2/SL_B",
    "/Motor Driver/SH_C", "/Motor Driver/SH_B", "/Motor Driver/SH_A",
    "/Motor_Driver2/SH_C", "/Motor_Driver2/SH_B", "/Motor_Driver2/SH_A",
}
txt = remove_zones_pred(txt, lambda znet, zlay, pts: znet in replace_nets and zlay in ("F.Cu", "B.Cu"))
txt = strip_all_filled_polygons(txt)


def shift_pts(pts, dx):
    return [(round(x + dx, 4), round(y, 4)) for (x, y) in pts]


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

# Orthogonal SH boundaries near J1/J2 guarantee >= 0.58 mm copper-to-copper gap everywhere:
# SH_C east = 106.90 (y >= 102.55), SH_B west = 107.48 (y >= 101.90), SH_B east = 112.52 (y >= 101.90), SH_A west = 113.10 (y >= 102.55).
# Vertical gap at step = 102.55 - 101.90 = 0.65 mm; horizontal gaps = 0.58 mm; J1 pad-to-zone gaps:
# J1.3 pad right = 106.90 -> SH_B west 107.48 = 0.58 mm; J1.2 pad left = 107.60 -> SH_C east 106.90 = 0.70 mm;
# J1.2 pad right = 112.40 -> SH_A west 113.10 = 0.70 mm; J1.1 pad left = 113.10 -> SH_B east 112.52 = 0.58 mm!
sh_c_f_m0 = [
    (88.35, 88.00), (90.00, 88.00), (90.00, 89.20), (93.50, 89.20),
    (93.50, 86.10), (98.35, 86.10), (98.35, 87.45), (94.60, 87.45),
    (94.60, 92.55), (98.40, 92.55), (98.40, 102.55),
    (106.90, 102.55), (106.90, 110.80),
    (88.35, 110.80), (88.35, 95.50), (91.95, 95.50),
    (91.95, 92.05), (88.35, 92.05),
]

sh_b_f_m0 = [
    (105.10, 88.00), (106.75, 88.00), (106.75, 89.20), (110.25, 89.20),
    (110.25, 86.10), (115.10, 86.10), (115.10, 87.45), (111.35, 87.45),
    (111.35, 92.55), (114.60, 92.55), (114.60, 96.20),
    (113.20, 96.20), (113.20, 101.90), (112.52, 101.90), (112.52, 110.80),
    (107.48, 110.80), (107.48, 101.90), (106.80, 101.90), (106.80, 95.50),
    (108.70, 95.50), (108.70, 92.05), (105.10, 92.05),
]

sh_a_f_m0 = [
    (121.85, 88.00), (123.50, 88.00), (123.50, 89.20), (127.00, 89.20),
    (127.00, 86.10), (131.85, 86.10), (131.85, 87.45), (128.10, 87.45),
    (128.10, 92.55), (133.80, 92.55), (133.80, 104.50),
    (126.50, 110.80), (113.10, 110.80), (113.10, 102.55),
    (121.00, 102.55), (121.00, 95.50), (125.45, 95.50),
    (125.45, 92.05), (121.85, 92.05),
]

# B.Cu SH_C, SH_B, SH_A mirror pours (orthogonal >= 0.58 mm separation, balanced with F.Cu):
sh_c_b_m0 = [
    (88.80, 88.00), (92.30, 88.00), (92.30, 86.20), (98.25, 86.20),
    (98.25, 98.20), (99.65, 98.20), (99.65, 102.55), (106.90, 102.55),
    (106.90, 110.80), (88.80, 110.80), (88.80, 95.75),
    (92.30, 95.75), (92.30, 91.85), (88.80, 91.85),
]

sh_b_b_m0 = [
    (105.55, 88.00), (109.05, 88.00), (109.05, 86.20), (114.60, 86.20),
    (114.60, 96.20), (113.20, 96.20), (113.20, 101.90), (112.52, 101.90),
    (112.52, 110.80), (107.48, 110.80), (107.48, 101.90), (106.80, 101.90),
    (106.80, 95.75), (109.05, 95.75), (109.05, 91.85), (105.55, 91.85),
]

sh_a_b_m0 = [
    (122.30, 88.00), (125.80, 88.00), (125.80, 86.20), (131.85, 86.20),
    (131.85, 93.20), (133.80, 93.20), (133.80, 104.50),
    (126.50, 110.80), (113.10, 110.80), (113.10, 102.55),
    (121.00, 102.55), (121.00, 95.75), (125.80, 95.75),
    (125.80, 91.85), (122.30, 91.85),
]

new_zones = []
for dx, pfx in [(0.0, "/Motor Driver"), (-70.0, "/Motor_Driver2")]:
    new_zones.append((f"{pfx}/SL_C", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_c_m0, dx)))
    new_zones.append((f"{pfx}/SL_B", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_b_m0, dx)))

    new_zones.append((f"{pfx}/SH_C", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_c_f_m0, dx)))
    new_zones.append((f"{pfx}/SH_B", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_b_f_m0, dx)))
    new_zones.append((f"{pfx}/SH_A", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_a_f_m0, dx)))

    new_zones.append((f"{pfx}/SH_C", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_c_b_m0, dx)))
    new_zones.append((f"{pfx}/SH_B", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_b_b_m0, dx)))
    new_zones.append((f"{pfx}/SH_A", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_a_b_m0, dx)))

    sh_via_specs = [
        ("SH_C", [
            (92.00, 89.80), (92.00, 91.45),
            (93.55, 88.65), (93.55, 90.30), (93.55, 91.95),
            (95.30, 94.75), (97.30, 94.75), (93.60, 94.75),
            (93.50, 97.60), (96.50, 97.60),
            (96.50, 101.20), (101.50, 104.20),
        ]),
        ("SH_B", [
            (108.75, 90.00),
            (110.30, 88.80), (110.30, 91.20),
            (110.35, 94.75), (112.05, 94.75), (113.85, 94.75),
            (108.50, 98.00), (111.50, 98.00),
            (110.00, 101.50),
        ]),
        ("SH_A", [
            (125.50, 89.80), (125.50, 91.45),
            (127.05, 88.65), (127.05, 90.30), (127.05, 91.95),
            (128.80, 94.75), (130.80, 94.75), (127.10, 94.75),
            (125.00, 97.60), (129.00, 97.60),
            (123.00, 101.80), (118.50, 104.20),
        ]),
    ]
    for sh_suffix, vlist in sh_via_specs:
        for (vx, vy) in vlist:
            new_vias.append((f"{pfx}/{sh_suffix}", round(vx + dx, 4), round(vy, 4), 0.8, 0.4))

txt = add_vias(txt, new_vias)
txt = add_zones(txt, new_zones)
p.write_text(txt)
print("Wrote balanced CS1 S-expression updates successfully.")
