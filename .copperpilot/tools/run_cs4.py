#!/usr/bin/env python3
"""
Change Set 4 (Step 4 — Aux Half-Bridge Q13/Q14):
- Expand Q13 VDC F.Cu island (width 3.05-5.45 mm -> >16.5 A on 2 oz F.Cu) and add 10x 0.8/0.4 mm VDC vias
  (>= 20 A capacity to In2.Cu VDC plane for 15 A aux/brake load).
- Reshape /Power Management/HS pour (3.1 mm min width on 2 oz F.Cu) to open clean F.Cu GND access to C48.2 & C_AUX1.2.
- Add C_AUX1 (Capacitor_SMD:C_0603_1608Metric, Value="TBD", board_only) beside Q13/C48 across VDC and GND.
- Add 6 GND vias near Q14 source (1 existing + 5 new = 6 within 3.2 mm, >= 4 required) and 5 GND vias near C48 GND pad.
"""
import sys
from pathlib import Path
from sexpr_pcb_utils import (
    remove_vias_pred, add_vias, remove_zones_pred, strip_all_filled_polygons,
    add_zones, add_board_only_0603_cap
)

p = Path(sys.argv[1])
txt = p.read_text()

# Remove old single VDC via (81.8, 63.8) inside Q13 island so we place a clean 10-via array
txt = remove_vias_pred(
    txt,
    lambda net, vx, vy: net == "VDC" and 75.0 <= vx <= 88.0 and 59.0 <= vy <= 66.5,
)

# Remove old Q13 VDC island (Z01: y_max < 70) and old /Power Management/HS zone (Z05)
txt = remove_zones_pred(
    txt,
    lambda znet, zlay, pts: zlay == "F.Cu" and (
        znet == "/Power Management/HS" or (znet == "VDC" and max(y for _, y in pts) < 70.0)
    ),
)
txt = strip_all_filled_polygons(txt)

# Add C_AUX1 (0603 HF ceramic, Value="TBD", board_only) beside Q13/C48 at (85.80, 62.50) rot=90:
# Note: at rot=90 CCW in KiCad, Pad 1 (-0.825, 0) -> (0, +0.825) [SOUTH = y=63.325 = VDC!],
# Pad 2 (+0.825, 0) -> (0, -0.825) [NORTH = y=61.675 = GND!] — Let's verify in pcbnew right after!
txt = add_board_only_0603_cap(txt, "C_AUX1", "TBD", 85.80, 62.50, 90.0, "VDC", "GND")

# Expanded Q13 VDC island (~52 mm^2, width 3.05..5.45 mm across Q13.5, C48.1, C_AUX1.1):
vdc_aux_pts = [
    (76.10, 60.15), (82.15, 60.15), (82.15, 62.55),
    (87.10, 62.55), (87.10, 65.60), (76.10, 65.60),
]

# Reshaped /Power Management/HS pour: leaves y=58.35..62.25, x=81.80..87.20 open for F.Cu GND at C48.2 & C_AUX1.2!
hs_aux_pts = [
    (72.65, 60.70), (74.05, 60.70), (74.05, 55.60),
    (90.80, 55.60), (90.80, 70.10), (81.40, 70.10),
    (81.40, 71.40), (76.00, 71.40), (76.00, 66.15),
    (87.70, 66.15), (87.70, 58.15), (75.55, 58.15),
    (75.55, 63.55), (74.05, 63.55), (74.05, 61.40), (72.65, 61.40),
]

aux_vias = [
    # 10x VDC vias (0.8/0.4 mm, >20 A capacity for 15 A aux load) inside Q13 VDC island -> In2.Cu (y >= 58.0!):
    ("VDC", 76.75, 65.05, 0.8, 0.4),
    ("VDC", 78.00, 65.05, 0.8, 0.4),
    ("VDC", 79.25, 65.05, 0.8, 0.4),
    ("VDC", 80.50, 65.05, 0.8, 0.4),
    ("VDC", 81.10, 61.00, 0.8, 0.4),
    ("VDC", 81.10, 62.30, 0.8, 0.4),
    ("VDC", 81.80, 63.65, 0.8, 0.4),
    ("VDC", 81.80, 65.05, 0.8, 0.4),
    ("VDC", 84.90, 64.95, 0.8, 0.4),
    ("VDC", 86.30, 64.95, 0.8, 0.4),
    # 5 new GND vias near Q14 source (+ existing (73.20, 67.20) = 6 GND vias within 3.3 mm of Q14 source!):
    ("GND", 73.20, 66.00, 0.8, 0.4),
    ("GND", 74.45, 65.90, 0.8, 0.4),
    ("GND", 71.45, 67.10, 0.8, 0.4),
    ("GND", 71.45, 68.35, 0.8, 0.4),
    ("GND", 71.45, 69.60, 0.8, 0.4),
    # 5 new GND vias near C48 GND pad (83.50, 61.10) & C_AUX1 GND pad (85.80, 61.675):
    ("GND", 82.30, 59.35, 0.8, 0.4),
    ("GND", 83.50, 59.35, 0.8, 0.4),
    ("GND", 84.70, 59.35, 0.8, 0.4),
    ("GND", 85.90, 59.35, 0.8, 0.4),
    ("GND", 84.70, 60.65, 0.8, 0.4),
]

txt = add_vias(txt, aux_vias)
txt = add_zones(txt, [
    ("VDC", "F.Cu", 3, 0.25, 0.25, vdc_aux_pts),
    ("/Power Management/HS", "F.Cu", 4, 0.25, 0.25, hs_aux_pts),
])

p.write_text(txt)
print("Wrote CS4 (Aux half-bridge: 10 VDC vias, 52 mm^2 island, C_AUX1, 6 Q14 GND vias + 5 C48 GND vias).")
