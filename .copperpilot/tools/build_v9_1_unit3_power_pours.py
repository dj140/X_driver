#!/usr/bin/env python3
"""Build Unit 3 symmetric power-stage copper pours and stitching vias on staged v9.1 PCB.

Targets ONLY the explicitly passed staged candidate .kicad_pcb path.
Enforces:
- 0 non-GND vias in [y = 86.0 .. 97.5 mm]
- 0 non-GND vias within 3.5 mm of C_HF1..C_HF6
- Exact +100.0 mm channel symmetry between M1 (left) and M0 (right)
"""

import math
import re
import sys
import uuid
from pathlib import Path


C_HF_CENTERS = [
    (158.4, 95.2),  # C_HF1
    (140.2, 95.2),  # C_HF2
    (121.4, 95.2),  # C_HF3
    (58.4, 95.2),   # C_HF4
    (40.2, 95.2),   # C_HF5
    (21.4, 95.2),   # C_HF6
]


def det_uuid(tag: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_OID, f"v9.1-unit3-{tag}"))


def parse_net_names(pcb_text: str) -> set[str]:
    names = set()
    for m in re.finditer(r'\(\s*net\s+(?:\d+\s+)?"([^"]+)"\s*\)', pcb_text):
        names.add(m.group(1))
    return names


def format_zone(
    net_name: str,
    layer: str,
    pts: list[tuple[float, float]],
    priority: int,
    clearance: float,
    solid: bool,
    tag: str,
    min_thickness: float = 0.25,
    thermal_gap: float = 0.30,
    thermal_bridge: float = 0.45,
) -> str:
    zuuid = det_uuid(f"zone-{tag}")
    connect_str = (
        f"(connect_pads yes (clearance {clearance:.3f}))"
        if solid
        else f"(connect_pads (clearance {clearance:.3f}))"
    )
    xy_str = " ".join(f"(xy {x:.4f} {y:.4f})" for x, y in pts)
    lines = [
        f'\t(zone',
        f'\t\t(net "{net_name}")',
        f'\t\t(layer "{layer}")',
        f'\t\t(uuid "{zuuid}")',
        f'\t\t(hatch edge 0.5)',
    ]
    if priority > 0:
        lines.append(f'\t\t(priority {priority})')
    lines.append(f'\t\t{connect_str}')
    lines.append(f'\t\t(min_thickness {min_thickness:.3f})')
    lines.append(f'\t\t(filled_areas_thickness no)')
    lines.append(
        f'\t\t(fill yes (thermal_gap {thermal_gap:.3f}) (thermal_bridge_width {thermal_bridge:.3f}) (island_removal_mode 0))'
    )
    lines.append(f'\t\t(polygon (pts {xy_str}))')
    lines.append(f'\t)')
    return "\n".join(lines)


def format_via(x: float, y: float, size: float, drill: float, net_name: str, tag: str) -> str:
    vuuid = det_uuid(f"via-{tag}-{x:.3f}-{y:.3f}")
    return (
        f'\t(via (at {x:.4f} {y:.4f}) (size {size:.3f}) (drill {drill:.3f}) '
        f'(layers "F.Cu" "B.Cu") (net "{net_name}") (uuid "{vuuid}"))'
    )


def build_zones_and_vias(net_names: set[str]) -> tuple[list[str], list[tuple[float, float, float, float, str, str]]]:
    zones: list[str] = []
    # (x, y, size, drill, net_name, tag)
    vias: list[tuple[float, float, float, float, str, str]] = []

    def add_z(net_name: str, layer: str, pts: list[tuple[float, float]], priority: int, clearance: float, solid: bool, tag: str):
        if net_name not in net_names:
            raise KeyError(f"Net not found in PCB: {net_name}")
        zones.append(format_zone(net_name, layer, pts, priority, clearance, solid, tag))

    def add_v(x: float, y: float, size: float, drill: float, net_name: str, tag: str):
        if net_name not in net_names:
            raise KeyError(f"Net not found in PCB: {net_name}")
        # Match KiCad netclass via_drill so pcbnew.ImportSpecctraSES preserves exact drill on every non-target via:
        # Power class (VDC, GND, SH_*, SL_*, HS) -> via_drill = 0.40 mm (min size 0.70 mm for 0.15 mm annular ring on 2oz)
        # Supply class (+3.3V, +5V, +3.3VA, GVDD) -> via_drill = 0.35 mm (min size 0.70 mm)
        if net_name == "+3.3V" and drill < 0.35:
            size = max(size, 0.70)
            drill = 0.35
        elif (
            net_name in ("VDC", "GND", "/Power Management/HS")
            or "/SH_" in net_name
            or "/SL_" in net_name
        ) and drill < 0.40:
            size = max(size, 0.70)
            drill = 0.40
        vias.append((round(x, 4), round(y, 4), size, drill, net_name, tag))

    # 1. Inner Reference & Power Planes
    add_z("GND", "In1.Cu", [(1.0, 16.0), (179.0, 16.0), (179.0, 129.0), (1.0, 129.0)], 0, 0.20, False, "in1-gnd")
    add_z("+3.3V", "In2.Cu", [(1.0, 16.0), (179.0, 16.0), (179.0, 56.5), (1.0, 56.5)], 1, 0.20, False, "in2-3v3")
    add_z("VDC", "In2.Cu", [(1.0, 57.5), (179.0, 57.5), (179.0, 129.0), (1.0, 129.0)], 3, 0.25, True, "in2-vdc")

    # 2. Symmetric M1 (dx=0.0, /Motor_Driver2) and M0 (dx=100.0, /Motor Driver) Power Stages
    channels = [
        ("M1", 0.0, "/Motor_Driver2"),
        ("M0", 100.0, "/Motor Driver"),
    ]

    for ch_tag, dx, pfx in channels:
        sh_a = f"{pfx}/SH_A"
        sh_b = f"{pfx}/SH_B"
        sh_c = f"{pfx}/SH_C"
        sl_b = f"{pfx}/SL_B"
        sl_c = f"{pfx}/SL_C"

        # --- SH_C (Priority 5) ---
        add_z(sh_c, "F.Cu", [
            (dx + 14.00, 84.85), (dx + 20.50, 84.85), (dx + 20.50, 90.65),
            (dx + 28.35, 90.65), (dx + 28.35, 94.45), (dx + 23.50, 94.45),
            (dx + 23.50, 93.45), (dx + 19.65, 93.45), (dx + 19.65, 88.45),
            (dx + 14.00, 88.45),
        ], 5, 0.25, True, f"{ch_tag}-fcu-shc-north")

        add_z(sh_c, "F.Cu", [
            (dx + 14.00, 95.55), (dx + 20.10, 95.55), (dx + 20.10, 97.80),
            (dx + 27.60, 97.80), (dx + 27.60, 112.50), (dx + 37.10, 118.50),
            (dx + 37.10, 126.20), (dx + 31.20, 126.20), (dx + 17.00, 115.00),
            (dx + 17.00, 97.45), (dx + 14.00, 97.45),
        ], 5, 0.25, True, f"{ch_tag}-fcu-shc-south")

        add_z(sh_c, "B.Cu", [
            (dx + 14.00, 84.85), (dx + 24.80, 84.85), (dx + 24.80, 97.80),
            (dx + 27.60, 97.80), (dx + 27.60, 112.50), (dx + 37.10, 118.50),
            (dx + 37.10, 126.20), (dx + 31.20, 126.20), (dx + 17.20, 115.00),
            (dx + 17.20, 88.45), (dx + 14.00, 88.45),
        ], 5, 0.25, True, f"{ch_tag}-bcu-shc")

        # SH_C North vias (strictly North of y=86.0)
        for vx in [14.6, 15.6, 16.6, 17.6, 18.6, 19.6]:
            add_v(dx + vx, 85.35, 0.60, 0.30, sh_c, f"{ch_tag}-shc-n")
        # SH_C South vias (strictly South of y=97.5 and >3.5mm from C_HF)
        for vy in [99.2, 102.5, 106.0, 109.5]:
            for vx in [18.5, 21.5, 24.5]:
                add_v(dx + vx, vy, 0.60, 0.30, sh_c, f"{ch_tag}-shc-s")

        # --- SL_C (Priority 4) ---
        add_z(sl_c, "F.Cu", [
            (dx + 8.65, 90.65), (dx + 19.15, 90.65), (dx + 19.15, 93.85),
            (dx + 21.95, 93.85), (dx + 21.95, 94.95), (dx + 19.15, 94.95),
            (dx + 19.15, 94.45), (dx + 13.70, 94.45), (dx + 13.70, 97.75),
            (dx + 16.55, 97.75), (dx + 16.55, 103.35), (dx + 11.15, 103.35),
            (dx + 11.15, 97.75), (dx + 8.65, 97.75),
        ], 4, 0.25, True, f"{ch_tag}-fcu-slc")

        add_z(sl_c, "B.Cu", [
            (dx + 11.15, 98.10), (dx + 16.55, 98.10),
            (dx + 16.55, 103.35), (dx + 11.15, 103.35),
        ], 4, 0.25, True, f"{ch_tag}-bcu-slc")

        for vx in [12.1, 13.9, 15.7]:
            add_v(dx + vx, 98.65, 0.70, 0.40, sl_c, f"{ch_tag}-slc-top")
        for vx in [12.1, 13.9, 15.7]:
            add_v(dx + vx, 102.85, 0.70, 0.40, sl_c, f"{ch_tag}-slc-bot")

        # --- SH_B (Priority 5) ---
        add_z(sh_b, "F.Cu", [
            (dx + 32.80, 84.85), (dx + 39.30, 84.85), (dx + 39.30, 90.65),
            (dx + 47.15, 90.65), (dx + 47.15, 94.45), (dx + 42.30, 94.45),
            (dx + 42.30, 93.45), (dx + 38.45, 93.45), (dx + 38.45, 88.45),
            (dx + 32.80, 88.45),
        ], 5, 0.25, True, f"{ch_tag}-fcu-shb-north")

        add_z(sh_b, "F.Cu", [
            (dx + 32.80, 95.55), (dx + 38.90, 95.55), (dx + 38.90, 97.80),
            (dx + 44.00, 97.80), (dx + 44.00, 116.50), (dx + 42.55, 119.00),
            (dx + 42.55, 126.20), (dx + 37.45, 126.20), (dx + 37.45, 118.00),
            (dx + 35.80, 114.50), (dx + 35.80, 97.45), (dx + 32.80, 97.45),
        ], 5, 0.25, True, f"{ch_tag}-fcu-shb-south")

        add_z(sh_b, "B.Cu", [
            (dx + 38.00, 84.85), (dx + 43.80, 84.85), (dx + 43.80, 116.50),
            (dx + 42.55, 119.00), (dx + 42.55, 126.20), (dx + 37.45, 126.20),
            (dx + 37.45, 118.00), (dx + 35.80, 114.50), (dx + 35.80, 88.45),
            (dx + 38.00, 88.45),
        ], 5, 0.25, True, f"{ch_tag}-bcu-shb")

        add_v(dx + 38.65, 85.35, 0.70, 0.40, sh_b, f"{ch_tag}-shb-n")
        for vy in [99.2, 103.0, 107.0, 111.0]:
            for vx in [37.0, 39.8, 42.6]:
                add_v(dx + vx, vy, 0.60, 0.30, sh_b, f"{ch_tag}-shb-s")

        # --- SL_B (Priority 4) ---
        add_z(sl_b, "F.Cu", [
            (dx + 29.35, 90.65), (dx + 37.95, 90.65), (dx + 37.95, 93.85),
            (dx + 40.75, 93.85), (dx + 40.75, 94.95), (dx + 37.95, 94.95),
            (dx + 37.95, 94.45), (dx + 32.50, 94.45), (dx + 32.50, 97.75),
            (dx + 35.20, 97.75), (dx + 35.20, 103.35), (dx + 29.65, 103.35),
            (dx + 29.65, 97.75), (dx + 29.35, 97.75),
        ], 4, 0.25, True, f"{ch_tag}-fcu-slb")

        add_z(sl_b, "B.Cu", [
            (dx + 29.65, 98.10), (dx + 35.20, 98.10),
            (dx + 35.20, 103.35), (dx + 29.65, 103.35),
        ], 4, 0.25, True, f"{ch_tag}-bcu-slb")

        for vx in [30.5, 32.4, 34.3]:
            add_v(dx + vx, 98.65, 0.70, 0.40, sl_b, f"{ch_tag}-slb-top")
        for vx in [30.5, 32.4, 34.3]:
            add_v(dx + vx, 102.85, 0.70, 0.40, sl_b, f"{ch_tag}-slb-bot")

        # --- SH_A (Priority 5) ---
        # Continuous F.Cu pour uniting Q7/Q1 Source, Q8/Q2 North Drain (via East wrap), Q8/Q2 South Drain, and J2.1/J1.1
        add_z(sh_a, "F.Cu", [
            (dx + 48.15, 90.65), (dx + 56.15, 90.65), (dx + 56.15, 94.45),
            (dx + 50.65, 94.45), (dx + 50.65, 99.30), (dx + 58.60, 99.30),
            (dx + 58.60, 97.60), (dx + 60.15, 97.60), (dx + 60.15, 95.55),
            (dx + 65.85, 95.55), (dx + 65.85, 88.45), (dx + 60.15, 88.45),
            (dx + 60.15, 84.85), (dx + 69.00, 84.85), (dx + 69.00, 99.00),
            (dx + 58.60, 99.00), (dx + 58.60, 118.00), (dx + 52.00, 126.20),
            (dx + 43.15, 126.20), (dx + 43.15, 119.00), (dx + 44.60, 116.50),
            (dx + 44.60, 99.30), (dx + 48.15, 99.30),
        ], 5, 0.25, True, f"{ch_tag}-fcu-sha")

        add_z(sh_a, "B.Cu", [
            (dx + 44.60, 90.65), (dx + 58.60, 90.65), (dx + 58.60, 84.85),
            (dx + 68.50, 84.85), (dx + 68.50, 98.80), (dx + 58.60, 98.80),
            (dx + 58.60, 118.00), (dx + 52.00, 126.20), (dx + 43.15, 126.20),
            (dx + 43.15, 119.00), (dx + 44.60, 116.50),
        ], 5, 0.25, True, f"{ch_tag}-bcu-sha")

        for vx in [60.8, 62.0, 63.2, 64.4, 65.6, 67.2]:
            add_v(dx + vx, 85.35, 0.60, 0.30, sh_a, f"{ch_tag}-sha-n")
        for vy in [100.2, 104.5, 109.0, 113.5]:
            for vx in [46.5, 50.5, 54.5]:
                add_v(dx + vx, vy, 0.60, 0.30, sh_a, f"{ch_tag}-sha-s")

        # --- Per-Channel VDC Commutation & Bulk Cap Pours (Priority 3) ---
        # West 1206 bank (C78, C35, C39, C40, C42, C44, C45, C46 + C31.1 / C80, C16, C61, C64..C68 + C11.1) -> Q11/Q5 North Drain
        add_z("VDC", "F.Cu", [
            (dx + 10.90, 80.15), (dx + 30.80, 80.15), (dx + 30.80, 78.65),
            (dx + 32.05, 78.65), (dx + 32.05, 81.05), (dx + 30.80, 81.05),
            (dx + 30.80, 88.45), (dx + 23.05, 88.45), (dx + 23.05, 83.25),
            (dx + 10.90, 83.25),
        ], 3, 0.22, True, f"{ch_tag}-fcu-vdc-west")

        # Dedicated VDC vias for EVERY West bank capacitor (explicitly stitching C35,C39,C40,C78 & C16,C61,C64,C80!)
        for vx in [11.5, 13.4, 15.85, 18.3, 20.75, 23.2, 25.65, 28.1, 30.1]:
            add_v(dx + vx, 82.75, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-west")
        add_v(dx + 31.5, 80.35, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-c31-c11")

        # Middle Q9/Q3 North Drain VDC block + vias (notched at top-west dx+41.95..43.35, y=82.55..84.35 for SH_A tap via)
        if ch_tag == "M0":
            add_z("VDC", "F.Cu", [
                (dx + 43.35, 82.55), (dx + 44.55, 82.55), (dx + 44.55, 81.45),
                (dx + 45.35, 81.45), (dx + 45.35, 82.55), (dx + 48.20, 82.55),
                (dx + 48.20, 88.45), (dx + 41.95, 88.45), (dx + 41.95, 84.35),
                (dx + 43.35, 84.35),
            ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-mid")
        else:
            add_z("VDC", "F.Cu", [
                (dx + 43.35, 82.55), (dx + 48.20, 82.55), (dx + 48.20, 88.45),
                (dx + 41.95, 88.45), (dx + 41.95, 84.35), (dx + 43.35, 84.35),
            ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-mid")
        for vx in [44.0, 45.7, 47.4]:
            add_v(dx + vx, 82.90, 0.70, 0.40, "VDC", f"{ch_tag}-vdc-mid")

        # East 1206 bank (C47..C79 / C69..C81) -> Q7/Q1 North Drain
        add_z("VDC", "F.Cu", [
            (dx + 50.10, 80.15), (dx + 65.70, 80.15), (dx + 65.70, 83.25),
            (dx + 57.15, 83.25), (dx + 57.15, 88.45), (dx + 50.90, 88.45),
            (dx + 50.90, 83.25), (dx + 50.10, 83.25),
        ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-east")
        for vx in [50.8, 53.25, 55.7, 58.15, 60.6, 63.05, 65.1]:
            add_v(dx + vx, 82.75, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-east")

        # South HS Drain + C_HF.1 VDC strips (vias strictly at y=98.60 > 97.5 and >5.9mm from C_HF!)
        add_z("VDC", "F.Cu", [
            (dx + 20.85, 95.45), (dx + 28.85, 95.45), (dx + 28.85, 99.15),
            (dx + 25.50, 99.15), (dx + 25.50, 97.45), (dx + 20.85, 97.45),
        ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-sc")
        add_z("VDC", "B.Cu", [
            (dx + 25.50, 98.00), (dx + 28.85, 98.00), (dx + 28.85, 99.20), (dx + 25.50, 99.20),
        ], 3, 0.25, True, f"{ch_tag}-bcu-vdc-sc")
        add_v(dx + 26.3, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sc1")
        add_v(dx + 28.0, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sc2")

        add_z("VDC", "F.Cu", [
            (dx + 39.65, 95.45), (dx + 47.65, 95.45), (dx + 47.65, 99.15),
            (dx + 44.50, 99.15), (dx + 44.50, 97.45), (dx + 39.65, 97.45),
        ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-sb")
        add_z("VDC", "B.Cu", [
            (dx + 44.50, 98.00), (dx + 47.65, 98.00), (dx + 47.65, 99.20), (dx + 44.50, 99.20),
        ], 3, 0.25, True, f"{ch_tag}-bcu-vdc-sb")
        add_v(dx + 45.3, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sb1")
        add_v(dx + 47.0, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sb2")

        add_z("VDC", "F.Cu", [
            (dx + 50.95, 95.45), (dx + 58.95, 95.45), (dx + 58.95, 97.45),
            (dx + 54.40, 97.45), (dx + 54.40, 99.15), (dx + 50.95, 99.15),
        ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-sa")
        add_z("VDC", "B.Cu", [
            (dx + 50.95, 98.00), (dx + 54.40, 98.00), (dx + 54.40, 99.20), (dx + 50.95, 99.20),
        ], 3, 0.25, True, f"{ch_tag}-bcu-vdc-sa")
        add_v(dx + 51.7, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sa1")
        add_v(dx + 53.5, 98.60, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-sa2")

        # Bottom Phase-A 1206 VDC caps (C56/C53 on M1, C75/C71 on M0)
        add_z("VDC", "F.Cu", [
            (dx + 59.25, 99.45), (dx + 64.60, 99.45), (dx + 64.60, 101.40), (dx + 59.25, 101.40),
        ], 3, 0.25, True, f"{ch_tag}-fcu-vdc-botcap")
        add_z("VDC", "B.Cu", [
            (dx + 59.25, 99.45), (dx + 64.60, 99.45), (dx + 64.60, 101.40), (dx + 59.25, 101.40),
        ], 3, 0.25, True, f"{ch_tag}-bcu-vdc-botcap")
        add_v(dx + 61.3, 100.40, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-botcap1")
        add_v(dx + 63.9, 100.40, 0.60, 0.30, "VDC", f"{ch_tag}-vdc-botcap2")

        # --- Per-Channel GND Pours & Stitching Vias ---
        # Top West & East 1206 capacitor GND strips + 1 dedicated GND via per cap to In1.Cu
        add_z("GND", "F.Cu", [
            (dx + 10.90, 76.60), (dx + 32.10, 76.60), (dx + 32.10, 78.35),
            (dx + 30.60, 78.35), (dx + 30.60, 79.85), (dx + 10.90, 79.85),
        ], 2, 0.20, True, f"{ch_tag}-fcu-gnd-capwest")
        for vx in [11.5, 13.4, 15.85, 18.3, 20.75, 23.2, 25.65, 28.1, 31.5]:
            add_v(dx + vx, 77.15, 0.60, 0.30, "GND", f"{ch_tag}-gnd-capwest")

        add_z("GND", "F.Cu", [
            (dx + 50.10, 76.60), (dx + 65.70, 76.60), (dx + 65.70, 79.85), (dx + 50.10, 79.85),
        ], 2, 0.20, True, f"{ch_tag}-fcu-gnd-capeast")
        for vx in [50.8, 53.25, 55.7, 58.15, 60.6, 63.05, 65.1]:
            add_v(dx + vx, 77.15, 0.60, 0.30, "GND", f"{ch_tag}-gnd-capeast")

        # Phase A LS Source (Q8/Q2) + C_HF4.2/C_HF1.2 GND pour (GND vias bond directly to In1.Cu 0.11mm below!)
        add_z("GND", "F.Cu", [
            (dx + 57.85, 93.85), (dx + 60.65, 93.85), (dx + 60.65, 90.65),
            (dx + 65.35, 90.65), (dx + 65.35, 94.45), (dx + 60.65, 94.45),
            (dx + 60.65, 94.95), (dx + 57.85, 94.95),
        ], 2, 0.22, True, f"{ch_tag}-fcu-gnd-qa")
        for vx in [61.4, 62.5, 63.5, 64.6]:
            add_v(dx + vx, 92.55, 0.60, 0.30, "GND", f"{ch_tag}-gnd-qa-src")
        add_v(dx + 59.65, 94.425, 0.60, 0.30, "GND", f"{ch_tag}-gnd-chf")

        # Shunt R36/R16 GND return + Kelvin NT8.2/NT4.2
        add_z("GND", "F.Cu", [
            (dx + 11.20, 105.65), (dx + 16.40, 105.65), (dx + 16.40, 114.00), (dx + 11.20, 114.00),
        ], 2, 0.22, True, f"{ch_tag}-fcu-gnd-shuntc")
        add_z("GND", "B.Cu", [
            (dx + 11.20, 105.65), (dx + 16.40, 105.65), (dx + 16.40, 114.00), (dx + 11.20, 114.00),
        ], 2, 0.22, True, f"{ch_tag}-bcu-gnd-shuntc")
        for vy in [109.8, 111.8]:
            for vx in [12.0, 13.3, 14.6, 15.8]:
                add_v(dx + vx, vy, 0.60, 0.30, "GND", f"{ch_tag}-gnd-shuntc")

        # Shunt R32/R12 GND return + Kelvin NT6.2/NT2.2
        add_z("GND", "F.Cu", [
            (dx + 29.70, 105.65), (dx + 35.10, 105.65), (dx + 35.10, 113.20), (dx + 29.70, 113.20),
        ], 2, 0.22, True, f"{ch_tag}-fcu-gnd-shuntb")
        add_z("GND", "B.Cu", [
            (dx + 29.70, 105.65), (dx + 35.10, 105.65), (dx + 35.10, 113.20), (dx + 29.70, 113.20),
        ], 2, 0.22, True, f"{ch_tag}-bcu-gnd-shuntb")
        for vy in [109.8, 111.8]:
            for vx in [30.5, 31.8, 33.1, 34.4]:
                add_v(dx + vx, vy, 0.60, 0.30, "GND", f"{ch_tag}-gnd-shuntb")

    # M0 U1 local PVDD1/PVDD2 C36 (145.45, 81.88): C36.1 joined M0-fcu-vdc-mid; C36.2 (145.935, 81.88) gets local East GND via
    add_v(147.05, 81.88, 0.60, 0.30, "GND", "u1-c36-gnd")
    add_z("GND", "F.Cu", [
        (145.60, 81.48), (147.45, 81.48), (147.45, 82.28), (145.60, 82.28),
    ], 2, 0.18, True, "u1-c36-gnd-tab")

    # U4 (+3.3V LDO output 107.55, 47.40) + C58.1 (105.30, 47.885) + C62.1 (105.30, 50.285) stitching into In2.Cu +3.3V plane
    add_z("+3.3V", "F.Cu", [
        (104.90, 47.55), (106.20, 47.55), (106.20, 47.05),
        (108.10, 47.05), (108.10, 48.25), (104.90, 48.25),
    ], 1, 0.18, True, "u4-c58-3v3-tab")
    add_v(106.45, 47.80, 0.60, 0.30, "+3.3V", "u4-c58-3v3")
    add_z("+3.3V", "F.Cu", [
        (104.90, 49.95), (106.85, 49.95), (106.85, 50.65), (104.90, 50.65),
    ], 1, 0.18, True, "c62-3v3-tab")
    add_v(106.45, 50.30, 0.60, 0.30, "+3.3V", "c62-3v3")

    # 3. Central J3 Battery Spine & B.Cu Horizontal VDC Distribution Bus
    add_z("VDC", "F.Cu", [
        (90.20, 80.00), (105.50, 80.00), (105.50, 128.60), (90.20, 128.60),
    ], 3, 0.25, True, "j3-fcu-vdc-spine")

    add_z("VDC", "B.Cu", [
        (10.90, 80.00), (165.70, 80.00), (165.70, 83.30),
        (105.50, 83.30), (105.50, 128.60), (90.20, 128.60),
        (90.20, 83.30), (10.90, 83.30),
    ], 3, 0.25, True, "bcu-vdc-bus-and-spine")

    for vy in [82.0, 84.5, 99.0, 103.5, 108.0, 112.5, 117.0, 127.0]:
        for vx in [92.0, 95.45, 99.0, 102.5]:
            add_v(vx, vy, 0.80, 0.40, "VDC", "j3-vdc-spine")

    # Central J3.1 GND Spine + M1 C56/C53 GND return
    add_z("GND", "F.Cu", [
        (59.20, 102.25), (70.00, 102.25), (70.00, 80.00),
        (89.40, 80.00), (89.40, 128.60), (59.20, 128.60),
    ], 2, 0.25, True, "j3-fcu-gnd-spine")
    add_z("GND", "B.Cu", [
        (59.20, 102.25), (70.00, 102.25), (70.00, 84.00),
        (89.40, 84.00), (89.40, 128.60), (59.20, 128.60),
    ], 2, 0.25, True, "j3-bcu-gnd-spine")
    for vy in [82.0, 84.8, 99.0, 103.5, 108.0, 112.5, 117.0, 127.0]:
        for vx in [74.0, 78.5, 83.0, 87.5]:
            add_v(vx, vy, 0.80, 0.40, "GND", "j3-gnd-spine")
    for vx in [60.0, 61.8, 63.6]:
        add_v(vx, 105.0, 0.60, 0.30, "GND", "m1-botcap-gnd")

    # M0 C75/C71 GND return block
    add_z("GND", "F.Cu", [
        (159.20, 102.25), (169.50, 102.25), (169.50, 128.60), (159.20, 128.60),
    ], 2, 0.25, True, "m0-fcu-botcap-gnd")
    add_z("GND", "B.Cu", [
        (159.20, 102.25), (169.50, 102.25), (169.50, 128.60), (159.20, 128.60),
    ], 2, 0.25, True, "m0-bcu-botcap-gnd")
    for vx in [160.0, 161.8, 163.6, 166.5]:
        add_v(vx, 105.0, 0.60, 0.30, "GND", "m0-botcap-gnd")

    # 4. Brake Chopper (Q13, Q14, C48, C_AUX1, H5, H6) Pours & Vias
    add_z("VDC", "F.Cu", [
        (91.15, 60.10), (96.00, 60.10), (96.00, 63.40),
        (102.00, 63.40), (102.00, 65.00), (91.15, 65.00),
    ], 3, 0.22, True, "brake-fcu-vdc")
    for vx in [92.5, 94.5, 97.5, 99.8, 101.4]:
        add_v(vx, 64.55, 0.60, 0.30, "VDC", "brake-vdc")

    add_z("/Power Management/HS", "F.Cu", [
        (87.55, 60.75), (90.50, 60.75), (90.50, 65.25),
        (101.20, 65.25), (101.20, 70.60), (96.20, 70.60),
        (96.20, 71.35), (91.15, 71.35), (91.15, 66.45),
        (89.05, 66.45), (89.05, 61.35), (87.55, 61.35),
    ], 4, 0.22, True, "brake-fcu-hs")
    add_z("/Power Management/HS", "B.Cu", [
        (91.15, 65.40), (101.20, 65.40), (101.20, 70.60),
        (96.20, 70.60), (96.20, 71.35), (91.15, 71.35),
    ], 4, 0.22, True, "brake-bcu-hs")
    for vx, vy in [(92.5, 66.0), (95.0, 66.0), (96.5, 68.4), (96.5, 70.0)]:
        add_v(vx, vy, 0.60, 0.30, "/Power Management/HS", "brake-hs")

    add_z("GND", "F.Cu", [
        (96.80, 60.00), (102.00, 60.00), (102.00, 63.05), (96.80, 63.05),
    ], 2, 0.20, True, "brake-fcu-capgnd")
    add_v(98.5, 60.05, 0.60, 0.30, "GND", "brake-c48-gnd")
    add_v(101.1, 61.60, 0.60, 0.30, "GND", "brake-caux-gnd")

    add_z("GND", "F.Cu", [
        (88.80, 66.80), (90.40, 66.80), (90.40, 74.20),
        (101.20, 74.20), (101.20, 71.65), (90.40, 71.65),
    ], 2, 0.20, True, "brake-fcu-q14-h5-gnd")
    # Wait: make that a clean non-self-intersecting L-polygon for Q14.1..3 + H5 (99.0, 72.8)
    zones.pop()
    add_z("GND", "F.Cu", [
        (88.80, 66.85), (90.35, 66.85), (90.35, 71.65),
        (101.20, 71.65), (101.20, 74.20), (88.80, 74.20),
    ], 2, 0.20, True, "brake-fcu-q14-h5-gnd")
    for vx in [89.6, 92.0, 95.0, 96.6]:
        add_v(vx, 72.80, 0.60, 0.30, "GND", "brake-h5-gnd")

    # U3 thermal pad GND vias (0.60/0.30 mm outside pads or 2x2 centered in U3.9 [2.6x3.0] at 84.0, 65.0)
    for vx in [83.4, 84.6]:
        for vy in [64.3, 65.7]:
            add_v(vx, vy, 0.60, 0.30, "GND", "u3-ep-gnd")

    # 5. Left & Right Edge Perimeter GND Guard Strips (connecting H7, H1, H2, H9, J4.S1, C102/R63 and H8, H3, H4, H10)
    add_z("GND", "F.Cu", [
        (1.0, 16.0), (8.30, 16.0), (8.30, 129.0), (1.0, 129.0),
    ], 0, 0.22, False, "left-edge-fcu-gnd")
    add_z("GND", "B.Cu", [
        (1.0, 16.0), (8.30, 16.0), (8.30, 129.0), (1.0, 129.0),
    ], 0, 0.22, False, "left-edge-bcu-gnd")

    add_z("GND", "F.Cu", [
        (170.80, 16.0), (179.0, 16.0), (179.0, 129.0), (170.80, 129.0),
    ], 0, 0.22, False, "right-edge-fcu-gnd")
    add_z("GND", "B.Cu", [
        (170.80, 16.0), (179.0, 16.0), (179.0, 129.0), (170.80, 129.0),
    ], 0, 0.22, False, "right-edge-bcu-gnd")

    for vy in [28.0, 46.0, 56.0, 66.0, 74.0, 112.0, 118.0]:
        add_v(3.0, vy, 0.60, 0.30, "GND", "left-guard-gnd")
        add_v(177.0, vy, 0.60, 0.30, "GND", "right-guard-gnd")

    # M0 Thermistor C21.2 / R23.1 local GND tie via at (107.8, 91.95) -> GND only!
    add_v(106.7, 91.95, 0.60, 0.30, "GND", "m0-th1-gnd")
    add_z("GND", "F.Cu", [
        (106.2, 91.10), (108.3, 91.10), (108.3, 92.80), (106.2, 92.80),
    ], 2, 0.18, True, "m0-th1-gnd-tab")

    # Hard Antipad Keepout Verification!
    for x, y, sz, dr, nname, tag in vias:
        if nname != "GND":
            if 86.0 <= y <= 97.5:
                raise AssertionError(f"Keepout violation: non-GND via {nname} ({tag}) at ({x}, {y}) inside y=[86.0, 97.5]!")
            for cx, cy in C_HF_CENTERS:
                dist = math.hypot(x - cx, y - cy)
                if dist < 3.5:
                    raise AssertionError(
                        f"Keepout violation: non-GND via {nname} ({tag}) at ({x}, {y}) is {dist:.2f} mm < 3.5 mm from C_HF ({cx}, {cy})!"
                    )

    # Check via-to-via spacing
    for i in range(len(vias)):
        for j in range(i + 1, len(vias)):
            x1, y1, s1, d1, n1, t1 = vias[i]
            x2, y2, s2, d2, n2, t2 = vias[j]
            dist = math.hypot(x1 - x2, y1 - y2)
            min_d = (d1 + d2) / 2.0 + 0.25 if n1 == n2 else (s1 + s2) / 2.0 + 0.25
            if dist < min_d - 1e-6:
                raise AssertionError(f"Via spacing violation ({dist:.3f} < {min_d:.3f}): {t1}({x1},{y1}) vs {t2}({x2},{y2})")

    return zones, vias


def strip_existing_zones_and_vias(pcb_text: str) -> str:
    # Remove top-level (zone ...) and (via ...) blocks cleanly using parenthesis depth
    out = []
    i = 0
    n = len(pcb_text)
    while i < n:
        if pcb_text[i] == "(":
            m = re.match(r"\(\s*(zone|via)\b", pcb_text[i:i+20])
            if m:
                depth = 0
                while i < n:
                    if pcb_text[i] == '"':
                        i += 1
                        while i < n and pcb_text[i] != '"':
                            if pcb_text[i] == "\\":
                                i += 1
                            i += 1
                    elif pcb_text[i] == "(":
                        depth += 1
                    elif pcb_text[i] == ")":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            while i < n and pcb_text[i] in " \t\r\n":
                                i += 1
                            break
                    i += 1
                continue
        out.append(pcb_text[i])
        i += 1
    return "".join(out)


def main():
    if len(sys.argv) != 2:
        print("Usage: build_v9_1_unit3_power_pours.py <staged_candidate.kicad_pcb>", file=sys.stderr)
        sys.exit(2)
    pcb_path = Path(sys.argv[1])
    if ".copperpilot/tmp/staging/" not in pcb_path.as_posix():
        raise RuntimeError(f"Refusing to mutate non-staged PCB path: {pcb_path}")

    raw = pcb_path.read_text()
    net_names = parse_net_names(raw)
    cleaned = strip_existing_zones_and_vias(raw)
    zones, vias = build_zones_and_vias(net_names)

    via_strs = [format_via(x, y, sz, dr, nname, tag) for x, y, sz, dr, nname, tag in vias]
    insert_block = "\n" + "\n".join(via_strs) + "\n" + "\n".join(zones) + "\n"

    emb_idx = cleaned.rfind("(embedded_fonts")
    if emb_idx != -1:
        updated = cleaned[:emb_idx] + insert_block + "\t" + cleaned[emb_idx:]
    else:
        last_paren = cleaned.rfind(")")
        if last_paren == -1:
            raise RuntimeError("Malformed .kicad_pcb file")
        updated = cleaned[:last_paren] + insert_block + ")\n"
    pcb_path.write_text(updated)
    print(f"Wrote {len(zones)} zones and {len(vias)} stitching vias to {pcb_path}")


if __name__ == "__main__":
    main()
