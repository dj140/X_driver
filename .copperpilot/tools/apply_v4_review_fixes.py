#!/usr/bin/env python3
"""
Fast single-pass application of all v4 review & schematic-sync fixes to staged bldc_motor_cntroller_v4.kicad_pcb.
"""
import sys, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sexpr_pcb_utils import (
    _find_top_blocks,
    set_footprint_poses_batch,
    remove_vias_pred,
    mark_all_vias_free,
    add_vias,
    remove_zones_pred,
    strip_all_filled_polygons,
    add_zones,
)

pcb_path = Path(sys.argv[1])
txt = pcb_path.read_text()

# 0. Strip filled_polygons FIRST (3.2 MB -> 450 KB -> 0.15s execution)
txt = strip_all_filled_polygons(txt)

# 1. Fix C_HF1..C_HF6 and C_AUX1 attributes & Value="100nF 100V"
for ref in ["C_HF1", "C_HF2", "C_HF3", "C_HF4", "C_HF5", "C_HF6", "C_AUX1"]:
    r_idx = txt.find(f'"Reference" "{ref}"')
    assert r_idx != -1, f"Missing {ref}"
    f_start = txt.rfind("(footprint", 0, r_idx)
    depth = 0
    f_end = f_start
    while f_end < len(txt):
        if txt[f_end] == "(":
            depth += 1
        elif txt[f_end] == ")":
            depth -= 1
            if depth == 0:
                f_end += 1
                break
        f_end += 1
    blk = txt[f_start:f_end]
    blk = blk.replace(
        "(attr smd board_only exclude_from_pos_files exclude_from_bom)",
        "(attr smd)",
    )
    blk = re.sub(r'(\(property\s+"Value"\s+)"[^"]*"', r'\1"100nF 100V"', blk, count=1)
    txt = txt[:f_start] + blk + txt[f_end:]

# Gather existing positions of U1/U2 clusters before batch update
fp_blocks = _find_top_blocks(txt, "footprint")
orig_poses = {}
for _, _, blk in fp_blocks:
    p_idx = blk.find('(property "Reference" "')
    if p_idx != -1:
        q0 = p_idx + len('(property "Reference" "')
        q1 = blk.find('"', q0)
        ref = blk[q0:q1]
        first_p = blk.find('(property "')
        m = re.search(r"\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+([-0-9.]+))?\)", blk[:first_p])
        if m:
            orig_poses[ref] = (float(m.group(1)), float(m.group(2)), float(m.group(3) or 0.0))

pose_map = {}

# 2. USB-C front-end placement adjacent to J4 (6.50, 36.00) (TP4 & TP5 spaced 2.70 mm -> 0 courtyard overlap)
for ref, x, y, rot in [
    ("U8", 14.20, 36.00, 0),
    ("R52", 18.20, 35.05, 180),
    ("R53", 18.20, 36.95, 180),
    ("TP4", 21.20, 34.65, 0),
    ("TP5", 21.20, 37.35, 0),
    ("R64", 14.20, 32.30, 0),
    ("R65", 14.20, 39.70, 0),
    ("F1", 18.50, 31.50, 0),
    ("D4", 24.00, 31.50, 180),
]:
    pose_map[ref] = (x, y, rot)

# 3. Relocate +5V -> +3.3V / +3.3VA LDO cluster between L1 (buck) and U6 (MCU)
for ref, x, y, rot in [
    ("U4", 96.00, 49.50, 90),
    ("C49", 99.20, 49.50, 90),
    ("C58", 92.80, 48.50, 90),
    ("C62", 92.80, 50.80, 90),
    ("U5", 96.00, 54.50, 90),
    ("C50", 99.20, 54.50, 90),
    ("C59", 92.80, 53.50, -90),
    ("C63", 92.80, 55.80, -90),
    ("TP1", 102.20, 52.00, 0),
]:
    pose_map[ref] = (x, y, rot)

# 4. Shift U1 & U2 (+1.65 mm in x, +1.00 mm in y -> (111.65, 72.00) & (41.65, 72.00))
u1_cluster = [
    "U1", "C7", "R4", "R20", "R21", "R19", "R6", "R7", "R5", "R22", "C20", "C17",
    "C8", "R17", "R18", "C9", "R3", "C4", "C5", "C6", "C1", "R10", "C11",
    "D1", "L1", "C10", "C12", "C18", "C19",
]
u2_cluster = [
    "U2", "R30", "R27", "R39", "R40", "C28", "C29", "R38", "R37", "C30", "R26", "C25", "C27", "C26", "C22", "C31",
]
for ref in u1_cluster + u2_cluster:
    ox, oy, orot = orig_poses[ref]
    # Nudge C22 +0.35 mm in x so its silk ref doesn't touch U2 silkscreen
    extra_dx = 0.35 if ref == "C22" else 0.0
    pose_map[ref] = (round(ox + 1.65 + extra_dx, 3), round(oy + 1.00, 3), orot)

for ref, x, y, rot in [
    ("C3", 103.50, 78.15, 0),
    ("C2", 106.20, 78.15, 0),
    ("C15", 108.90, 78.15, 0),
    ("C14", 111.60, 78.15, 0),
    ("C13", 114.30, 78.15, 0),
    ("C36", 121.00, 78.15, 0),
    ("C24", 33.50, 78.15, 0),
    ("C23", 36.20, 78.15, 0),
    ("C34", 38.90, 78.15, 0),
    ("C33", 41.60, 78.15, 0),
    ("C32", 44.30, 78.15, 0),
]:
    pose_map[ref] = (x, y, rot)

# 5. Symmetrical FET banks (M0 centered at 110.00, M1 = M0 - 70.00), gate resistors, straddling C_HF1..C_HF6
for ref, x, y, rot in [
    ("Q5", 92.40, 90.00, -90), ("Q6", 98.60, 90.00, -90),
    ("Q3", 106.90, 90.00, -90), ("Q4", 113.10, 90.00, -90),
    ("Q1", 121.40, 90.00, -90), ("Q2", 127.60, 90.00, -90),
    ("R13", 93.35, 84.90, -90), ("R14", 99.55, 84.90, -90),
    ("R8", 107.85, 84.90, -90), ("R9", 114.05, 84.90, -90),
    ("R1", 122.35, 84.90, -90), ("R2", 128.55, 84.90, -90),
    ("C_HF3", 95.85, 85.15, 0),
    ("C_HF2", 110.35, 85.15, 0),
    ("C_HF1", 124.85, 85.15, 0),
    ("Q11", 22.40, 90.00, -90), ("Q12", 28.60, 90.00, -90),
    ("Q9", 36.90, 90.00, -90), ("Q10", 43.10, 90.00, -90),
    ("Q7", 51.40, 90.00, -90), ("Q8", 57.60, 90.00, -90),
    ("R33", 23.35, 84.90, -90), ("R34", 29.55, 84.90, -90),
    ("R28", 37.85, 84.90, -90), ("R29", 44.05, 84.90, -90),
    ("R24", 52.35, 84.90, -90), ("R25", 58.55, 84.90, -90),
    ("C_HF6", 25.85, 85.15, 0),
    ("C_HF5", 40.35, 85.15, 0),
    ("C_HF4", 54.85, 85.15, 0),
]:
    pose_map[ref] = (x, y, rot)

# 6. 15x 1206 bulk capacitors per bank at y = 81.65 mm (rot = 90) with 3x 4.1 mm wide gate corridors
cap_xs_m0 = [87.60, 90.15, 92.70, 95.25,  101.85, 104.40, 106.95, 109.50,  116.10, 118.65, 121.20, 123.75,  130.55, 133.10, 135.65]
m0_1206_refs = ["C16", "C61", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C73", "C74", "C75", "C76", "C77"]
m1_1206_refs = ["C35", "C39", "C40", "C42", "C44", "C45", "C46", "C47", "C51", "C53", "C54", "C55", "C56", "C57", "C60"]
for ref, cx in zip(m0_1206_refs, cap_xs_m0):
    pose_map[ref] = (cx, 81.65, 90)
for ref, cx in zip(m1_1206_refs, cap_xs_m0):
    pose_map[ref] = (round(cx - 70.00, 3), 81.65, 90)

pose_map["C80"] = (84.70, 81.65, 90)
pose_map["C81"] = (85.95, 81.65, 90)
pose_map["C78"] = (67.75, 81.65, 90)
pose_map["C79"] = (69.00, 81.65, 90)

# 7. Horizontal 2512 shunts at y = 97.10 mm (rot = 180), Kelvin net-ties + 120R sense resistors at y = 94.50 mm,
#    thermistors spaced cleanly outside phase cones (dy = 1.85 mm -> 0 silk overlap!), and J1/J2/J3 at y = 106.50 mm
for ref, x, y, rot in [
    ("R16", 100.80, 97.35, 180),
    ("NT3", 97.55, 94.75, 180),
    ("R15", 99.60, 94.75, 0),
    ("NT4", 104.20, 94.75, 0),
    ("R12", 115.30, 97.35, 180),
    ("NT1", 112.05, 94.75, 180),
    ("R11", 114.10, 94.75, 0),
    ("NT2", 118.70, 94.75, 0),
    ("TH1", 86.20, 95.20, 0), ("R23", 86.20, 97.20, 0), ("C21", 86.20, 99.20, 0),
    ("TH4", 134.20, 95.20, 0), ("R62", 134.20, 97.20, 0), ("C101", 134.20, 99.20, 0),
    ("J1", 115.50, 106.50, 180),
    ("R36", 30.80, 97.35, 180),
    ("NT7", 27.55, 94.75, 180),
    ("R35", 29.60, 94.75, 0),
    ("NT8", 34.20, 94.75, 0),
    ("R32", 45.30, 97.35, 180),
    ("NT5", 42.05, 94.75, 180),
    ("R31", 44.10, 94.75, 0),
    ("NT6", 48.70, 94.75, 0),
    ("TH2", 16.20, 95.20, 0), ("R42", 16.20, 97.20, 0), ("C38", 16.20, 99.20, 0),
    ("TH5", 64.20, 95.20, 0), ("R63", 64.20, 97.20, 0), ("C102", 64.20, 99.20, 0),
    ("J2", 45.50, 106.50, 180),
    ("J3", 75.00, 106.50, 0),
]:
    pose_map[ref] = (x, y, rot)

txt = set_footprint_poses_batch(txt, pose_map)

# 8. Rebuild high-power zones and stitching vias cleanly (zero self-pinches, 100% single-connected islands!)
txt = remove_zones_pred(
    txt,
    lambda net, layer, pts: (
        "SH_" in net
        or "SL_" in net
        or (net == "VDC" and layer == "F.Cu" and any(p[1] > 75.0 for p in pts))
        or (net == "/Power Management/HS" and layer == "B.Cu")
    ),
)
txt = remove_vias_pred(txt, lambda net, vx, vy: vy >= 78.0)

def shift_pts(pts, dx):
    return [(round(x + dx, 3), round(y, 3)) for x, y in pts]

new_zones = []
new_vias = []

# B.Cu /Power Management/HS thermal/current island under Q14 pad 5 -> H6 + 4x 0.8/0.4 vias
hs_b_pts = [(75.60, 66.80), (85.20, 66.80), (85.20, 70.10), (75.60, 70.10)]
new_zones.append(("/Power Management/HS", "B.Cu", 4, 0.30, 0.25, hs_b_pts))
for vx, vy in [(76.60, 67.60), (78.40, 67.60), (76.60, 69.30), (78.40, 69.30)]:
    new_vias.append(("/Power Management/HS", vx, vy, 0.8, 0.4))

# Central J3 XT90 GND (69.55, 106.50) & VDC (80.45, 106.50) via arrays
for vx in [66.8, 68.4, 70.0, 71.6, 73.0]:
    for vy in [102.5, 104.5, 108.8, 110.5]:
        if not (abs(vx - 69.55) < 2.6 and abs(vy - 106.50) < 2.6):
            new_vias.append(("GND", vx, vy, 0.8, 0.4))
for vx in [77.5, 79.1, 80.7, 82.3, 83.9]:
    for vy in [96.0, 98.2, 100.4, 102.5, 108.8, 110.5]:
        if not (abs(vx - 80.45) < 2.6 and abs(vy - 106.50) < 2.6):
            new_vias.append(("VDC", vx, vy, 0.8, 0.4))

# Simple, strictly non-self-intersecting F.Cu VDC bus bar covering M1, central J3 spine, and M0!
vdc_main_pts = [
    # Top north edge left -> right (y = 82.25 across M1 & M0, dipping to y = 82.50 across center)
    (16.40, 82.25), (137.20, 82.25),
    # Right end down to y = 83.95, then right -> left along M0 lower contour:
    (137.20, 83.95),
    (129.40, 83.95), (129.40, 83.75), (124.50, 83.75),
    (124.50, 86.00), (123.15, 86.00), (123.15, 87.85), (120.75, 87.85),
    (120.75, 92.15), (123.15, 92.15), (123.15, 94.30), (117.75, 94.30),
    (117.75, 83.95),
    (110.00, 83.95), (110.00, 86.00), (108.65, 86.00), (108.65, 87.85), (106.25, 87.85),
    (106.25, 92.15), (108.65, 92.15), (108.65, 94.30), (103.25, 94.30),
    (103.25, 83.95),
    (95.50, 83.95), (95.50, 86.00), (94.15, 86.00), (94.15, 87.85), (91.75, 87.85),
    (91.75, 92.15), (94.15, 92.15), (94.15, 94.30), (88.75, 94.30),
    (88.75, 85.80),
    # Central J3 VDC spine (x = 76.80..84.60 down to y = 111.20) — 3.55 mm tall bridge (82.25..85.80) on both sides!
    (84.60, 85.80), (84.60, 111.20), (76.80, 111.20), (76.80, 85.80),
    # M1 right -> left lower contour (exact -70.00 mm mirror of M0):
    (59.40, 85.80), (59.40, 83.75), (54.50, 83.75),
    (54.50, 86.00), (53.15, 86.00), (53.15, 87.85), (50.75, 87.85),
    (50.75, 92.15), (53.15, 92.15), (53.15, 94.30), (47.75, 94.30),
    (47.75, 83.95),
    (40.00, 83.95), (40.00, 86.00), (38.65, 86.00), (38.65, 87.85), (36.25, 87.85),
    (36.25, 92.15), (38.65, 92.15), (38.65, 94.30), (33.25, 94.30),
    (33.25, 83.95),
    (25.50, 83.95), (25.50, 86.00), (24.15, 86.00), (24.15, 87.85), (21.75, 87.85),
    (21.75, 92.15), (24.15, 92.15), (24.15, 94.30), (18.75, 94.30),
    (18.75, 83.95), (16.40, 83.95),
]
new_zones.append(("VDC", "F.Cu", 3, 0.25, 0.25, vdc_main_pts))

# M0 Phase Pour polygons on F.Cu (Priority 5):
# Note: between Q_HS east drain (x_hs+1.65 = 94.05, 108.55, 123.05) and Q_LS west source pad 8 (x_ls-1.175 = 97.425, 111.925, 126.425),
# SH spans x_hs+2.00 .. x_ls-1.50 (2.70 mm wide!) straight up to y=85.85 to embrace Q_LS pads 9,10 (north drain) in ONE solid piece!
# And at Q_LS south drain pads 1,2 (x_ls-1.20 & x_ls+1.20, y=93.20, pad right = x_ls+1.65 = 100.25, 114.75),
# SH stops at x_ls+1.75 (100.35, 114.85) at y=92.20..94.20 so SL_C / SL_B passes freely east of 100.65 / 115.15!
sh_c_f_m0 = [
    (90.90, 88.00), (94.35, 88.00), (94.35, 85.85),
    (100.30, 85.85), (100.30, 87.80), (97.10, 87.80),
    (97.10, 92.20), (100.35, 92.20), (100.35, 94.15),
    (96.35, 94.15), (96.35, 99.55), (106.95, 99.55),
    (106.95, 110.20), (90.90, 110.20),
    (90.90, 94.80), (94.60, 94.80), (94.60, 91.95), (90.90, 91.95),
]
sh_b_f_m0 = [
    (105.40, 88.00), (108.85, 88.00), (108.85, 85.85),
    (114.80, 85.85), (114.80, 87.80), (111.60, 87.80),
    (111.60, 92.20), (114.85, 92.20), (114.85, 94.15),
    (110.95, 94.15), (110.95, 99.55), (112.65, 99.55),
    (112.65, 110.20), (107.60, 110.20),
    (107.60, 98.85), (105.10, 98.85), (105.10, 94.80),
    (109.10, 94.80), (109.10, 91.95), (105.40, 91.95),
]
sh_a_f_m0 = [
    (119.90, 88.00), (123.35, 88.00), (123.35, 85.85),
    (129.30, 85.85), (129.30, 87.80), (126.10, 87.80),
    (126.10, 92.20), (129.30, 92.20), (129.30, 110.20),
    (113.30, 110.20), (113.30, 99.55), (120.05, 99.55),
    (120.05, 94.80), (123.60, 94.80), (123.60, 91.95), (119.90, 91.95),
]

# B.Cu SH mirror pours (Priority 5, >= 0.65 mm gap; R16/R12 are F.Cu SMD only so B.Cu SH_C & SH_B run wide & straight!)
sh_c_b_m0 = [
    (91.00, 88.10), (96.90, 88.10), (96.90, 92.25), (101.00, 92.25),
    (101.00, 99.55), (106.95, 99.55),
    (106.95, 110.20), (91.00, 110.20),
]
sh_b_b_m0 = [
    (105.50, 88.10), (111.40, 88.10), (111.40, 92.25), (115.50, 92.25),
    (115.50, 98.85), (112.65, 98.85),
    (112.65, 110.20), (107.60, 110.20), (107.60, 98.85), (105.50, 98.85),
]
sh_a_b_m0 = [
    (120.00, 88.10), (125.90, 88.10), (125.90, 92.25), (129.20, 92.25),
    (129.20, 110.20), (113.30, 110.20), (113.30, 99.55), (121.80, 99.55),
    (121.80, 94.80), (120.00, 94.80),
]

# F.Cu SL_C & SL_B pours: start east wing at y=89.20 so (100.95, 88.45) & (115.45, 88.45) sit in F.Cu+B.Cu GND (< 3.0 mm from Q6/Q4!)
sl_c_f_m0 = [
    (97.35, 88.05), (98.40, 88.05), (98.40, 89.05), (100.15, 89.05),
    (100.15, 89.40), (102.95, 89.40),
    (102.95, 96.00), (99.65, 96.00), (99.65, 98.85), (96.75, 98.85),
    (96.75, 94.40), (97.50, 94.40), (97.50, 95.55), (100.68, 95.55),
    (100.68, 91.95), (97.35, 91.95),
]
sl_c_hf_top_m0 = [
    (96.25, 84.35), (98.35, 84.35), (98.35, 85.60), (96.25, 85.60),
]
sl_c_b_m0 = [
    (96.85, 84.35), (102.95, 84.35), (102.95, 91.95), (101.65, 91.95),
    (101.65, 85.60), (96.85, 85.60),
]

sl_b_f_m0 = [
    (111.85, 88.05), (112.90, 88.05), (112.90, 89.05), (114.65, 89.05),
    (114.65, 89.40), (117.45, 89.40),
    (117.45, 96.00), (114.15, 96.00), (114.15, 98.85), (111.25, 98.85),
    (111.25, 94.40), (112.00, 94.40), (112.00, 95.55), (115.18, 95.55),
    (115.18, 91.95), (111.85, 91.95),
]
sl_b_hf_top_m0 = [
    (110.75, 84.35), (112.85, 84.35), (112.85, 85.60), (110.75, 85.60),
]
sl_b_b_m0 = [
    (111.35, 84.35), (117.45, 84.35), (117.45, 91.95), (116.15, 91.95),
    (116.15, 85.60), (111.35, 85.60),
]

for pfx, dx in [("/Motor Driver", 0.0), ("/Motor_Driver2", -70.0)]:
    new_zones.append((f"{pfx}/SH_C", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_c_f_m0, dx)))
    new_zones.append((f"{pfx}/SH_B", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_b_f_m0, dx)))
    new_zones.append((f"{pfx}/SH_A", "F.Cu", 5, 0.25, 0.25, shift_pts(sh_a_f_m0, dx)))

    new_zones.append((f"{pfx}/SH_C", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_c_b_m0, dx)))
    new_zones.append((f"{pfx}/SH_B", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_b_b_m0, dx)))
    new_zones.append((f"{pfx}/SH_A", "B.Cu", 5, 0.30, 0.25, shift_pts(sh_a_b_m0, dx)))

    new_zones.append((f"{pfx}/SL_C", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_c_f_m0, dx)))
    new_zones.append((f"{pfx}/SL_C", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_c_hf_top_m0, dx)))
    new_zones.append((f"{pfx}/SL_C", "B.Cu", 4, 0.30, 0.25, shift_pts(sl_c_b_m0, dx)))

    new_zones.append((f"{pfx}/SL_B", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_b_f_m0, dx)))
    new_zones.append((f"{pfx}/SL_B", "F.Cu", 4, 0.25, 0.25, shift_pts(sl_b_hf_top_m0, dx)))
    new_zones.append((f"{pfx}/SL_B", "B.Cu", 4, 0.30, 0.25, shift_pts(sl_b_b_m0, dx)))

    # SH stitching vias (0.8/0.4 mm, >= 1.70 mm pitch -> In1.Cu GND 100% solid)
    sh_vias_m0 = [
        ("SH_C", [
            (94.45, 89.80), (94.45, 91.40), (96.05, 89.80), (96.05, 91.40), (98.80, 93.10),
            (92.20, 96.20), (94.80, 96.20),
            (92.20, 100.50), (95.00, 100.50), (98.20, 100.50), (101.40, 100.50),
            (96.00, 103.50), (99.50, 103.50),
            (101.20, 106.50), (104.50, 109.50),
        ]),
        ("SH_B", [
            (108.95, 89.80), (108.95, 91.40), (110.55, 89.80), (110.55, 91.40), (113.30, 93.10),
            (106.20, 96.20), (108.50, 95.80), (110.20, 95.80),
            (106.20, 98.10), (108.50, 98.50), (110.20, 98.50),
            (108.60, 101.50), (111.40, 101.50),
            (110.00, 109.50),
        ]),
        ("SH_A", [
            (124.20, 89.20), (124.20, 91.00),
            (126.80, 95.20),
            (122.80, 100.50), (126.50, 100.50),
            (119.50, 103.50), (123.50, 103.50),
            (118.80, 106.50), (115.50, 109.50),
        ]),
    ]
    for snet, pts in sh_vias_m0:
        for vx, vy in pts:
            new_vias.append((f"{pfx}/{snet}", round(vx + dx, 3), vy, 0.8, 0.4))

    # SL_C & SL_B HF commutation loop vias (connecting C_HF3.2 / C_HF2.2 -> B.Cu strap -> Q6 / Q4 source)
    for vx, vy in [(97.60, 84.95), (102.25, 89.80), (102.25, 91.35)]:
        new_vias.append((f"{pfx}/SL_C", round(vx + dx, 3), vy, 0.8, 0.4))
    for vx, vy in [(112.10, 84.95), (116.75, 89.80), (116.75, 91.35)]:
        new_vias.append((f"{pfx}/SL_B", round(vx + dx, 3), vy, 0.8, 0.4))

    # C_HF1 / C_HF4 Phase A GND via right at Pad 2 + Q2/Q8 LS source GND vias
    new_vias.append(("GND", round(126.55 + dx, 3), 84.95, 0.8, 0.4))
    for vy in [88.60, 90.20, 91.80]:
        new_vias.append(("GND", round(130.60 + dx, 3), vy, 0.8, 0.4))
        new_vias.append(("GND", round(132.30 + dx, 3), vy, 0.8, 0.4))

    # Shunt-side FET-edge GND vias at (100.95, 88.70) & (115.45, 88.70) -> 2.92 mm (< 3.0 mm) from Q6/Q4 LS source centroid!
    new_vias.append(("GND", round(100.95 + dx, 3), 88.70, 0.8, 0.4))
    new_vias.append(("GND", round(115.45 + dx, 3), 88.70, 0.8, 0.4))

    for sx_gnd in [103.25, 117.75]:
        for vx in [sx_gnd - 0.15, sx_gnd + 0.95]:
            for vy in [96.10, 97.35, 98.60]:
                new_vias.append(("GND", round(vx + dx, 3), vy, 0.8, 0.4))

    # >= 4 VDC vias beside pads 1,2 on EVERY HS FET (Q5=92.40, Q3=106.90, Q1=121.40)
    for x_hs in [92.40, 106.90, 121.40]:
        for vy in [88.80, 90.80, 92.40, 93.80]:
            new_vias.append(("VDC", round(x_hs - 2.65 + dx, 3), vy, 0.8, 0.4))
        new_vias.append(("VDC", round(x_hs - 1.15 + dx, 3), 93.90, 0.8, 0.4))
        new_vias.append(("VDC", round(x_hs + 0.15 + dx, 3), 93.90, 0.8, 0.4))

    # Top VDC & GND stitching vias along the 15x 1206 cap row
    for cx in cap_xs_m0:
        new_vias.append(("GND", round(cx + dx, 3), 79.15, 0.8, 0.4))
        new_vias.append(("VDC", round(cx + dx, 3), 83.45, 0.8, 0.4))

txt = add_zones(txt, new_zones)
txt = add_vias(txt, new_vias)
txt = mark_all_vias_free(txt)

pcb_path.write_text(txt)
print(f"Applied fast v4 review fixes: {len(new_zones)} zones, {len(new_vias)} vias written.")
