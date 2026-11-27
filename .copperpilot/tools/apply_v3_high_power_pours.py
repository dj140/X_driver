#!/usr/bin/env python3
"""
Construct high-power multi-layer copper zones and symmetric high-current stitching via arrays
on a staged candidate of bldc_motor_cntroller_v3.kicad_pcb using read-only pad geometry from
pcbnew and deterministic KiCad 10 S-expression output.
"""
import math
import sys
import uuid
import pcbnew


def hs_fet_south_pts(x0, x_west):
    return [
        (x_west, 83.80),
        (x_west, 94.10),
        (x0 + 2.25, 94.10),
        (x0 + 2.25, 92.55),
        (x0 - 1.85, 92.55),
        (x0 - 1.85, 87.45),
        (x0 + 2.25, 87.45),
        (x0 + 2.25, 86.15),
        (x0 + 0.25, 86.15),
        (x0 + 0.25, 83.80),
    ]


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def min_dist_to_poly_edges(x, y, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        l2 = dx * dx + dy * dy
        if l2 == 0:
            d = math.hypot(x - x1, y - y1)
        else:
            t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / l2))
            px, py = x1 + t * dx, y1 + t * dy
            d = math.hypot(x - px, y - py)
        if d < best:
            best = d
    return best


def format_zone(netname, layer, priority, pts, clearance_mm=0.25, min_thick_mm=0.25, island_mode=0):
    pts_str = " ".join(f"(xy {x:.4f} {y:.4f})" for x, y in pts)
    prio_str = f"\n\t\t(priority {priority})" if priority > 0 else ""
    return (
        f'\n\t(zone\n'
        f'\t\t(net "{netname}")\n'
        f'\t\t(layer "{layer}")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t\t(hatch edge 0.5){prio_str}\n'
        f'\t\t(connect_pads yes\n'
        f'\t\t\t(clearance {clearance_mm:.3f})\n'
        f'\t\t)\n'
        f'\t\t(min_thickness {min_thick_mm:.3f})\n'
        f'\t\t(fill yes\n'
        f'\t\t\t(thermal_gap 0.5)\n'
        f'\t\t\t(thermal_bridge_width 0.8)\n'
        f'\t\t\t(island_removal_mode {island_mode})\n'
        f'\t\t)\n'
        f'\t\t(polygon\n'
        f'\t\t\t(pts\n'
        f'\t\t\t\t{pts_str}\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )


def format_via(x, y, netname, size_mm=0.80, drill_mm=0.40):
    return (
        f'\n\t(via\n'
        f'\t\t(at {x:.4f} {y:.4f})\n'
        f'\t\t(size {size_mm:.3f})\n'
        f'\t\t(drill {drill_mm:.3f})\n'
        f'\t\t(layers "F.Cu" "B.Cu")\n'
        f'\t\t(net "{netname}")\n'
        f'\t\t(uuid "{uuid.uuid4()}")\n'
        f'\t)'
    )


def build_pours_and_vias(baseline_path, candidate_path):
    board = pcbnew.LoadBoard(baseline_path)

    pad_boxes = []
    drill_circles = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pnet = pad.GetNetname()
            bb = pad.GetBoundingBox()
            l = pcbnew.ToMM(bb.GetLeft())
            t = pcbnew.ToMM(bb.GetTop())
            r = pcbnew.ToMM(bb.GetRight())
            b = pcbnew.ToMM(bb.GetBottom())
            pad_boxes.append((pnet, l, t, r, b))
            dsz = pad.GetDrillSize()
            dx, dy = pcbnew.ToMM(dsz.x), pcbnew.ToMM(dsz.y)
            if dx > 0 or dy > 0:
                pos = pad.GetPosition()
                drill_circles.append((pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y), max(dx, dy) / 2.0))

    # 1. 6x Motor Phase Output Copper Zones on F.Cu (Priority 5, Solid Fill)
    # Stepped at y = 103.60 mm so each MR60PB-M pin gets a >7.2 mm tall x 6.8-18.7 mm wide
    # copper feed while opening a generous GND stitching bay south of every 2512 shunt.
    m1_sh_c = [
        (18.35, 88.00), (20.00, 88.00), (20.00, 89.20), (23.50, 89.20),
        (23.50, 86.10), (28.75, 86.10), (28.75, 87.45), (24.60, 87.45),
        (24.60, 92.55), (28.85, 92.55), (28.85, 95.30), (25.20, 95.30),
        (25.20, 103.60), (37.05, 103.60), (37.05, 110.80), (18.35, 110.80),
        (18.35, 94.45), (22.55, 94.45), (22.55, 92.05), (18.35, 92.05),
    ]
    m1_sh_b = [
        (35.10, 88.00), (36.75, 88.00), (36.75, 89.20), (40.25, 89.20),
        (40.25, 86.10), (45.50, 86.10), (45.50, 87.45), (41.35, 87.45),
        (41.35, 92.55), (45.60, 92.55), (45.60, 95.30), (42.05, 95.30),
        (42.05, 104.60), (42.65, 104.60), (42.65, 110.80), (37.35, 110.80),
        (37.35, 103.60), (33.45, 103.60), (33.45, 94.45), (39.30, 94.45),
        (39.30, 92.05), (35.10, 92.05),
    ]
    m1_sh_a = [
        (51.85, 88.00), (53.50, 88.00), (53.50, 89.20), (57.00, 89.20),
        (57.00, 86.10), (62.25, 86.10), (62.25, 87.45), (58.10, 87.45),
        (58.10, 92.55), (62.50, 92.55), (62.50, 105.00), (48.40, 110.80),
        (42.95, 110.80), (42.95, 103.60), (50.20, 103.60), (50.20, 94.45),
        (56.05, 94.45), (56.05, 92.05), (51.85, 92.05),
    ]

    # 2. 4x Low-Side Shunt Return Copper Zones on F.Cu (Priority 4, Solid Fill)
    base_sl = [
        (24.90, 88.05), (26.35, 88.05), (26.35, 89.20), (33.15, 89.20),
        (33.15, 95.60), (31.80, 96.45), (26.75, 96.45), (26.75, 95.90),
        (29.25, 95.90), (29.25, 92.15), (24.90, 92.15),
    ]

    # 3. Brake Chopper Switch Node /Power Management/HS on F.Cu (Priority 4, Solid Fill)
    hs_chopper = [
        (72.65, 60.70), (74.05, 60.70), (74.05, 56.80), (89.20, 56.80),
        (89.20, 70.10), (81.40, 70.10), (81.40, 71.40), (76.00, 71.40),
        (76.00, 66.10), (85.50, 66.10), (85.50, 59.50), (75.55, 59.50),
        (75.55, 63.55), (74.05, 63.55), (74.05, 61.40), (72.65, 61.40),
    ]

    # 4. Monolithic VDC Bus Bar + Local Chopper VDC Pour on F.Cu (Priority 3, Solid Fill)
    vdc_chopper = [
        (76.10, 60.10), (81.40, 60.10), (81.40, 62.65),
        (84.70, 62.65), (84.70, 64.85), (76.10, 64.85),
    ]

    vdc_north = [
        (14.50, 82.10),
        (62.20, 82.10),
        (62.20, 81.65),
        (65.20, 81.65),
        (65.20, 82.10),
        (133.20, 82.10),
        (133.20, 81.65),
        (136.30, 81.65),
        (136.30, 83.80),
    ]
    vdc_south_lr = []
    vdc_south_lr.extend(hs_fet_south_pts(20.00, 14.50)[1:])
    vdc_south_lr.extend(hs_fet_south_pts(36.75, 33.55))
    vdc_south_lr.extend(hs_fet_south_pts(53.50, 50.30))
    vdc_south_lr.extend([
        (68.00, 83.80),
        (68.00, 87.50),
        (75.60, 87.50),
        (75.60, 111.80),
        (84.80, 111.80),
        (84.80, 100.50),
        (84.30, 100.50),
        (84.30, 94.10),
        (92.25, 94.10),
        (92.25, 92.55),
        (88.15, 92.55),
        (88.15, 87.45),
        (92.25, 87.45),
        (92.25, 86.15),
        (90.25, 86.15),
        (90.25, 83.80),
    ])
    vdc_south_lr.extend(hs_fet_south_pts(106.75, 103.55))
    vdc_south_lr.extend(hs_fet_south_pts(123.50, 120.30))
    vdc_main = vdc_north + list(reversed(vdc_south_lr))

    full_board_pts = [(1.0, 16.0), (149.0, 16.0), (149.0, 112.5), (1.0, 112.5)]
    in2_vdc_pts = [(1.0, 58.0), (149.0, 58.0), (149.0, 112.5), (1.0, 112.5)]

    zones_sexpr = [
        format_zone("/Motor_Driver2/SH_C", "F.Cu", 5, m1_sh_c, 0.25),
        format_zone("/Motor_Driver2/SH_B", "F.Cu", 5, m1_sh_b, 0.25),
        format_zone("/Motor_Driver2/SH_A", "F.Cu", 5, m1_sh_a, 0.25),
        format_zone("/Motor Driver/SH_C", "F.Cu", 5, [(x + 70.0, y) for x, y in m1_sh_c], 0.25),
        format_zone("/Motor Driver/SH_B", "F.Cu", 5, [(x + 70.0, y) for x, y in m1_sh_b], 0.25),
        format_zone("/Motor Driver/SH_A", "F.Cu", 5, [(x + 70.0, y) for x, y in m1_sh_a], 0.25),
        format_zone("/Motor_Driver2/SL_C", "F.Cu", 4, base_sl, 0.25),
        format_zone("/Motor_Driver2/SL_B", "F.Cu", 4, [(x + 16.75, y) for x, y in base_sl], 0.25),
        format_zone("/Motor Driver/SL_C", "F.Cu", 4, [(x + 70.0, y) for x, y in base_sl], 0.25),
        format_zone("/Motor Driver/SL_B", "F.Cu", 4, [(x + 86.75, y) for x, y in base_sl], 0.25),
        format_zone("/Power Management/HS", "F.Cu", 4, hs_chopper, 0.25),
        format_zone("VDC", "F.Cu", 3, vdc_chopper, 0.25),
        format_zone("VDC", "F.Cu", 3, vdc_main, 0.25),
        format_zone("GND", "F.Cu", 0, full_board_pts, 0.25),
        format_zone("GND", "In1.Cu", 0, full_board_pts, 0.30),
        format_zone("VDC", "In2.Cu", 0, in2_vdc_pts, 0.30),
        format_zone("GND", "B.Cu", 0, full_board_pts, 0.30),
    ]

    non_gnd_polys = (
        [m1_sh_c, m1_sh_b, m1_sh_a]
        + [[(x + 70.0, y) for x, y in p] for p in (m1_sh_c, m1_sh_b, m1_sh_a)]
        + [base_sl, [(x + 16.75, y) for x, y in base_sl], [(x + 70.0, y) for x, y in base_sl], [(x + 86.75, y) for x, y in base_sl]]
        + [hs_chopper, vdc_chopper, vdc_main]
    )

    placed_vias = []
    vias_sexpr = []

    def try_place_via(x, y, netname, size_mm=0.80, drill_mm=0.40):
        r_via = size_mm / 2.0
        r_drill = drill_mm / 2.0

        for hx, hy, hr in drill_circles:
            if math.hypot(x - hx, y - hy) < (r_drill + hr + 0.40):
                return False
        for vx, vy, vr, vdr, _ in placed_vias:
            if math.hypot(x - vx, y - vy) < (r_via + vr + 0.30):
                return False

        for pnet, l, t, r, b in pad_boxes:
            margin = 0.35 if pnet != netname else 0.12
            if (l - r_via - margin) <= x <= (r + r_via + margin) and (t - r_via - margin) <= y <= (b + r_via + margin):
                return False

        if netname == "VDC":
            in_main = point_in_poly(x, y, vdc_main) and min_dist_to_poly_edges(x, y, vdc_main) >= 0.50
            in_chop = point_in_poly(x, y, vdc_chopper) and min_dist_to_poly_edges(x, y, vdc_chopper) >= 0.50
            in_in2 = (1.5 <= x <= 148.5) and (58.5 <= y <= 112.0)
            if not ((in_main or in_chop) and in_in2):
                return False
        elif netname == "GND":
            if not ((1.5 <= x <= 148.5) and (16.5 <= y <= 112.0)):
                return False
            for poly in non_gnd_polys:
                if point_in_poly(x, y, poly) or min_dist_to_poly_edges(x, y, poly) < (r_via + 0.45):
                    return False

        placed_vias.append((x, y, r_via, r_drill, netname))
        vias_sexpr.append(format_via(x, y, netname, size_mm, drill_mm))
        return True

    # VDC Vias: J3 Pin 2 spine + capacitor seam + HS DirectFET drains + Q13/C48 chopper
    for y in [83.0, 84.8, 86.6, 88.8, 91.0, 93.2, 95.5, 97.8, 100.0, 102.2, 104.2, 111.0]:
        for x in [76.6, 78.4, 80.2, 82.0, 83.5]:
            try_place_via(x, y, "VDC")
    for x in [69.0, 71.0, 73.0, 74.8]:
        for y in [83.0, 85.0, 86.7]:
            try_place_via(x, y, "VDC")

    m1_cap_xs = [15.5 + 3.2 * i for i in range(15)]
    for cx in m1_cap_xs[:-1]:
        try_place_via(cx + 1.6, 82.95, "VDC")
    m0_cap_xs = [86.5 + 3.2 * i for i in range(15)]
    for cx in m0_cap_xs[:-1]:
        try_place_via(cx + 1.6, 82.95, "VDC")

    for x0 in [20.0, 36.75, 53.5, 90.0, 106.75, 123.5]:
        for x in [x0 - 2.55, x0 - 1.2, x0 - 0.35]:
            try_place_via(x, 84.8, "VDC")
        try_place_via(x0, 93.3, "VDC")
        if x0 in (20.0, 90.0):
            for y in [86.5, 88.5, 90.5, 92.5]:
                try_place_via(x0 - 2.8, y, "VDC")
                try_place_via(x0 - 4.2, y, "VDC")

    for x, y in [(76.8, 60.8), (76.8, 64.1), (80.8, 60.8), (81.8, 63.8), (83.8, 63.8)]:
        try_place_via(x, y, "VDC")

    # GND Vias: J3 Pin 1 spine + north capacitor seam + Phase A Q8/Q2 sources + 2512 shunt GND bays + chopper/drivers
    for y in [89.0, 91.2, 93.4, 95.6, 97.8, 100.0, 102.2, 104.0, 111.6]:
        for x in [66.5, 68.3, 70.1, 71.9, 73.7]:
            try_place_via(x, y, "GND")
    for y in [104.5, 106.5, 108.5, 110.5]:
        for x in [63.8, 65.0, 74.2]:
            try_place_via(x, y, "GND")

    for cx in m1_cap_xs + m0_cap_xs:
        try_place_via(cx, 78.7, "GND")
    for cx in [62.8, 64.6, 133.8, 135.6]:
        try_place_via(cx, 79.8, "GND")

    # Unshunted Phase-A LS source exits (Q8 & Q2)
    for y in [88.4, 89.6, 90.8, 92.0]:
        for dx in [2.4, 3.8, 5.2]:
            try_place_via(60.0 + dx, y, "GND")
            try_place_via(130.0 + dx, y, "GND")

    # Dense high-current GND return arrays around all 4x 2512 shunts (R36, R32, R16, R12 Pad 1)
    for sx in [31.2, 47.95, 101.2, 117.95]:
        for y in [101.75, 102.75]:
            for dx in [-4.8, -3.6, -2.4, -1.2, 0.0, 1.2]:
                try_place_via(sx + dx, y, "GND")
        for y in [97.55, 98.70]:
            for dx in [-2.6, -1.4, -0.2, 1.0]:
                try_place_via(sx + dx, y, "GND")

    for x, y in [
        (73.2, 67.2), (73.2, 68.5), (73.2, 69.8), (82.0, 61.1), (84.8, 61.1),
        (81.5, 72.5), (86.6, 72.5), (84.0, 74.8),
        (106.0, 70.2), (114.0, 70.2), (36.0, 70.2), (44.0, 70.2),
    ]:
        try_place_via(x, y, "GND")

    for y in [78.0, 85.0, 90.0, 95.0, 103.0]:
        try_place_via(11.5, y, "GND")
        try_place_via(138.5, y, "GND")

    raw = open(baseline_path, "r", encoding="utf-8").read().rstrip()
    if not raw.endswith(")"):
        raise RuntimeError("Unexpected EOF in baseline KiCad PCB file")
    out = raw[:-1] + "".join(zones_sexpr) + "".join(vias_sexpr) + "\n)\n"
    with open(candidate_path, "w", encoding="utf-8") as f:
        f.write(out)

    vdc_cnt = sum(1 for v in placed_vias if v[4] == "VDC")
    gnd_cnt = sum(1 for v in placed_vias if v[4] == "GND")
    print(f"Wrote {len(zones_sexpr)} zones and {len(placed_vias)} vias (VDC={vdc_cnt}, GND={gnd_cnt}) to {candidate_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: apply_v3_high_power_pours.py <baseline_pcb> <candidate_pcb>")
        sys.exit(1)
    build_pours_and_vias(sys.argv[1], sys.argv[2])
