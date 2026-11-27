#!/usr/bin/env python3
"""
Change Set 2 (Step 2):
- Widen VDC fingers to lower drain row on all 6 HS FETs (Q1, Q3, Q5, Q7, Q9, Q11) symmetrically (M1 = M0 - 70 mm).
- Add 4 VDC vias (0.80 / 0.40 mm) to In2.Cu directly beside pads 1,2 on each of Q1, Q3, Q5, Q7, Q9, Q11
  (>= 3 vias target) so every lower-row path is well under 1.0 square (~0.20-0.35 sq).
"""
import sys
from pathlib import Path
from sexpr_pcb_utils import (
    remove_vias_pred, add_vias, remove_zones_pred, strip_all_filled_polygons, add_zones
)

p = Path(sys.argv[1])
txt = p.read_text()

# Remove old outer-edge VDC vias at x=15.8/17.2 and x=85.8/87.2 (y=86.5..92.5) so we replace with clean symmetric arrays
txt = remove_vias_pred(
    txt,
    lambda net, vx, vy: net == "VDC" and 86.0 <= vy <= 93.0 and (
        (15.5 <= vx <= 17.5) or (85.5 <= vx <= 87.5)
    ),
)

# Remove main lower VDC zone Z11 on F.Cu (the one with max y > 90; keep Q13's Z01 at y < 70 for Step 4!)
txt = remove_zones_pred(
    txt,
    lambda znet, zlay, pts: znet == "VDC" and zlay == "F.Cu" and max(y for _, y in pts) > 85.0,
)
txt = strip_all_filled_polygons(txt)

# Construct symmetric widened main VDC F.Cu zone:
# - Covers all 1206 VDC pads (y = 82.1..83.8) + C78..C81 (y = 81.65..83.8)
# - Central J3 VDC spine (x = 75.6..84.8 for y = 95.5..111.8, narrowing to x = 75.6..83.0 for y = 85.8..95.5
#   so M0 Phase C has the exact same GND pocket x = 83.3..85.4 as M1 Phase C x = 13.3..15.4!)
# - Each of the 6 HS FETs (qx in 20.0, 36.75, 53.5, 90.0, 106.75, 123.5) gets a wide VDC finger + south tab under pads 1,2 (y <= 95.20):

def fet_finger_clockwise_top_to_top_right_to_left(qx, is_phase_b_or_a):
    """Return polygon vertices tracing the south protrusion for HS FET at qx (traversed right -> left along y=83.8)."""
    # Entering from east at (qx + 0.25, 83.80):
    # Notch around HS pads 9,10 (y=86.80) and SH pads 3..8 (y=88.0..92.05), then wrap south under pads 1,2 (y=93.20) down to y=95.20!
    if is_phase_b_or_a == "B":
        # Clear SL_C east edge (qx - 6.55 + 3.45 = qx - 3.10 at y=93.40): keep west edge at qx - 4.65 down to y=92.90, then qx - 2.75 down to y=95.20
        return [
            (round(qx + 0.25, 4), 83.80),
            (round(qx + 0.25, 4), 86.15),
            (round(qx + 2.25, 4), 86.15),
            (round(qx + 2.25, 4), 87.45),
            (round(qx - 1.85, 4), 87.45),
            (round(qx - 1.85, 4), 92.55),
            (round(qx + 1.65, 4), 92.55),
            (round(qx + 1.65, 4), 95.20),
            (round(qx - 2.75, 4), 95.20),
            (round(qx - 2.75, 4), 92.90),
            (round(qx - 4.65, 4), 92.90),
            (round(qx - 4.65, 4), 83.80),
        ]
    elif is_phase_b_or_a == "A":
        # Clear SL_B east edge similarly for exact cell uniformity!
        return [
            (round(qx + 0.25, 4), 83.80),
            (round(qx + 0.25, 4), 86.15),
            (round(qx + 2.25, 4), 86.15),
            (round(qx + 2.25, 4), 87.45),
            (round(qx - 1.85, 4), 87.45),
            (round(qx - 1.85, 4), 92.55),
            (round(qx + 1.65, 4), 92.55),
            (round(qx + 1.65, 4), 95.20),
            (round(qx - 2.75, 4), 95.20),
            (round(qx - 2.75, 4), 92.90),
            (round(qx - 4.65, 4), 92.90),
            (round(qx - 4.65, 4), 83.80),
        ]
    else:
        # Phase C (Q5=90.0, Q11=20.0): no shunt on west side! Full x = qx - 4.35 down to y=95.20
        return [
            (round(qx + 0.25, 4), 83.80),
            (round(qx + 0.25, 4), 86.15),
            (round(qx + 2.25, 4), 86.15),
            (round(qx + 2.25, 4), 87.45),
            (round(qx - 1.85, 4), 87.45),
            (round(qx - 1.85, 4), 92.55),
            (round(qx + 1.65, 4), 92.55),
            (round(qx + 1.65, 4), 95.20),
            (round(qx - 4.35, 4), 95.20),
            (round(qx - 4.35, 4), 83.80),
        ]


vdc_main_pts = [
    (14.50, 82.10), (62.20, 82.10), (62.20, 81.65), (65.20, 81.65),
    (65.20, 82.10), (133.20, 82.10), (133.20, 81.65), (136.30, 81.65),
    (136.30, 83.80),
    *fet_finger_clockwise_top_to_top_right_to_left(123.50, "A"),
    *fet_finger_clockwise_top_to_top_right_to_left(106.75, "B"),
    *fet_finger_clockwise_top_to_top_right_to_left(90.00, "C"),
    # Central J3 VDC spine (leaves x = 83.0..85.65 at y = 85.0..95.5 open for GND + C_HF3!)
    (83.00, 83.80), (83.00, 96.80), (84.30, 96.80), (84.30, 100.50),
    (84.80, 100.50), (84.80, 111.80), (75.60, 111.80), (75.60, 87.50),
    (68.00, 87.50), (68.00, 83.80),
    *fet_finger_clockwise_top_to_top_right_to_left(53.50, "A"),
    *fet_finger_clockwise_top_to_top_right_to_left(36.75, "B"),
    *fet_finger_clockwise_top_to_top_right_to_left(20.00, "C"),
    (14.50, 83.80),
]

# Also remove the 4 old central-spine VDC vias at x=83.50, y=86.6..93.2 that would touch x=83.00 boundary
txt = remove_vias_pred(
    txt,
    lambda net, vx, vy: net == "VDC" and abs(vx - 83.50) < 0.2 and 84.5 <= vy <= 96.5,
)

# Add 4 VDC vias beside pads 1,2 + 2 mid-finger VDC vias on EVERY ONE of the 6 HS FETs (Q1, Q3, Q5, Q7, Q9, Q11)
vdc_new_vias = []
for qx, kind in [(123.50, "A"), (106.75, "B"), (90.00, "C"), (53.50, "A"), (36.75, "B"), (20.00, "C")]:
    if kind in ("A", "B"):
        # Mid-finger vias (y=88.5, 90.2) + 4 lower-drain vias right beside pads 1,2!
        vdc_new_vias.extend([
            ("VDC", round(qx - 3.25, 4), 88.60, 0.8, 0.4),
            ("VDC", round(qx - 3.25, 4), 90.40, 0.8, 0.4),
            ("VDC", round(qx - 3.25, 4), 92.10, 0.8, 0.4),
            ("VDC", round(qx - 2.15, 4), 94.30, 0.8, 0.4),
            ("VDC", round(qx - 0.85, 4), 94.70, 0.8, 0.4),
            ("VDC", round(qx + 1.05, 4), 94.70, 0.8, 0.4),
        ])
    else:
        vdc_new_vias.extend([
            ("VDC", round(qx - 3.05, 4), 86.60, 0.8, 0.4),
            ("VDC", round(qx - 3.05, 4), 88.60, 0.8, 0.4),
            ("VDC", round(qx - 3.05, 4), 90.40, 0.8, 0.4),
            ("VDC", round(qx - 3.05, 4), 92.20, 0.8, 0.4),
            ("VDC", round(qx - 3.05, 4), 94.20, 0.8, 0.4),
            ("VDC", round(qx - 1.20, 4), 94.70, 0.8, 0.4),
            ("VDC", round(qx + 1.05, 4), 94.70, 0.8, 0.4),
        ])

txt = add_vias(txt, vdc_new_vias)
txt = add_zones(txt, [("VDC", "F.Cu", 3, 0.25, 0.25, vdc_main_pts)])
p.write_text(txt)
print("Wrote CS2 (HS drain feed widened + >=4 VDC vias beside pads 1,2 per HS FET).")
