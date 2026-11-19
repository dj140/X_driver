#!/usr/bin/env python3
"""
Change Set 3 (Step 3 — Hot Loops):
- Nudge the 1206 bulk capacitor row +0.15 mm in y (81.50 -> 81.65 mm) so every HS drain (Q1, Q3, Q5, Q7, Q9, Q11)
  is <= 3.86 mm (< 4.00 mm) center-to-center (2.42 mm edge-to-edge) from its nearest 1206 bulk capacitor.
- Phases B and C (Q4, Q6 on M0 and -70 mm Q10, Q12 on M1): add GND vias on the shunt-side FET edge so
  LS source centroid -> nearest GND via closes to 2.83 mm (< 3.00 mm; nearest pad 1.83 mm).
- Add one HF ceramic (Capacitor_SMD:C_0603_1608Metric, Value="TBD", board_only) per phase (C_HF1..C_HF6,
  M1 = M0 - 70.000 mm) across the VDC finger and nearest GND via right at each FET.
"""
import sys
from pathlib import Path
from sexpr_pcb_utils import (
    set_footprint_pose, add_vias, strip_all_filled_polygons, add_board_only_0603_cap
)

p = Path(sys.argv[1])
txt = p.read_text()

# 1. Nudge 30x 1206 bulk caps (M1 & M0 rows at y=81.50 -> y=81.65 mm) so all 6 HS drains are <= 3.86 mm (< 4.0 mm)
bulk_m1 = ["C35", "C39", "C40", "C42", "C44", "C45", "C46", "C47", "C51", "C53", "C54", "C55", "C56", "C57", "C60"]
bulk_m0 = ["C16", "C61", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C73", "C74", "C75", "C76", "C77"]
x_m1 = [15.5, 18.7, 21.9, 25.1, 28.3, 31.5, 34.7, 37.9, 41.1, 44.3, 47.5, 50.7, 53.9, 57.1, 60.3]
x_m0 = [86.5, 89.7, 92.9, 96.1, 99.3, 102.5, 105.7, 108.9, 112.1, 115.3, 118.5, 121.7, 124.9, 128.1, 131.3]
for ref, xv in zip(bulk_m1, x_m1):
    txt = set_footprint_pose(txt, ref, xv, 81.65, 90.0)
for ref, xv in zip(bulk_m0, x_m0):
    txt = set_footprint_pose(txt, ref, xv, 81.65, 90.0)

# 2. Add shunt-side FET edge GND vias on Phases B and C (< 3.0 mm from Q4, Q6, Q10, Q12 LS source) + HF cap GND vias
hotloop_gnd_vias = []
for dx in [0.0, -70.0]:
    # Phase C shunt-side FET edge (Q6 / Q12) + HF ceramic C_HF2 / C_HF5 GND return
    hotloop_gnd_vias.extend([
        ("GND", round(98.65 + dx, 4), 88.55, 0.8, 0.4),
        ("GND", round(99.85 + dx, 4), 88.55, 0.8, 0.4),
        ("GND", round(99.85 + dx, 4), 87.15, 0.8, 0.4),
    ])
    # Phase B shunt-side FET edge (Q4 / Q10) + HF ceramic C_HF1 / C_HF4 GND return
    hotloop_gnd_vias.extend([
        ("GND", round(115.40 + dx, 4), 88.55, 0.8, 0.4),
        ("GND", round(116.60 + dx, 4), 88.55, 0.8, 0.4),
        ("GND", round(116.60 + dx, 4), 87.15, 0.8, 0.4),
    ])
    # Phase C west GND pocket for C_HF3 / C_HF6
    hotloop_gnd_vias.extend([
        ("GND", round(84.15 + dx, 4), 85.95, 0.8, 0.4),
        ("GND", round(84.15 + dx, 4), 88.35, 0.8, 0.4),
    ])

txt = strip_all_filled_polygons(txt)
txt = add_vias(txt, hotloop_gnd_vias)

# 3. Add 1x HF ceramic (C_0603_1608Metric, Value="TBD", board_only) per phase across VDC finger & nearest GND via at FET
# rot=180 puts Pad 1 (VDC) at x+0.825 (inside VDC finger) and Pad 2 (GND) at x-0.825 (adjacent to GND via)
hf_specs = [
    ("C_HF1", 118.45, 87.15, 180.0),  # M0 Phase A (Q1)
    ("C_HF2", 101.70, 87.15, 180.0),  # M0 Phase B (Q3)
    ("C_HF3",  85.25, 87.15, 180.0),  # M0 Phase C (Q5)
    ("C_HF4",  48.45, 87.15, 180.0),  # M1 Phase A (Q7, exact -70.000 mm)
    ("C_HF5",  31.70, 87.15, 180.0),  # M1 Phase B (Q9, exact -70.000 mm)
    ("C_HF6",  15.25, 87.15, 180.0),  # M1 Phase C (Q11, exact -70.000 mm)
]
for ref, cx, cy, crot in hf_specs:
    txt = add_board_only_0603_cap(txt, ref, "TBD", cx, cy, crot, "VDC", "GND")

p.write_text(txt)
print("Wrote CS3 (Hot loops: bulk caps <4mm, shunt-side GND vias <3mm, 6x per-phase HF ceramics).")
