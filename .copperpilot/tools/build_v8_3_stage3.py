import math
import sys
import os
import pathlib
import re
import pcbnew

CAND_PCB = ".copperpilot/tmp/staging/v8_3_power_stage/candidate/bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_pcb"
BASE_PCB = ".copperpilot/tmp/staging/v8_3_power_stage/baseline/bldc_motor_cntroller/bldc_motor_cntroller_v8.2.kicad_pcb"

keep_tracks = "--keep-tracks" in sys.argv
no_vias = "--no-vias" in sys.argv

src_pcb = CAND_PCB if (keep_tracks and pathlib.Path(CAND_PCB).exists()) else BASE_PCB
if no_vias and src_pcb == BASE_PCB:
    # Strip baseline vias cleanly before loading so DSN has 0 pre-existing vias
    raw = pathlib.Path(BASE_PCB).read_text()
    raw = re.sub(r"\n?\t*\(via\s+(?:\([^\(\)]*\)|[^\(\)])*\((?:\([^\(\)]*\)|[^\(\)])*\)[^\(\)]*\)", "", raw)
    pathlib.Path(CAND_PCB).write_text(raw)
    src_pcb = CAND_PCB

board = pcbnew.LoadBoard(src_pcb)
tb = board.GetTitleBlock()
tb.SetRevision("v8.3")
board.SetTitleBlock(tb)

def mm(v):
    return round(pcbnew.ToMM(v), 4)

# Remove any temporary CP_TEMP_SENSE_GUIDE Rule Areas from prior routing passes
for z in [z for z in list(board.Zones()) if z.GetIsRuleArea() and z.GetZoneName().startswith("CP_TEMP_")]:
    board.Remove(z)

# ---------------------------------------------------------------------------
# 1. MOVABLE COMPONENT POSES (strictly movable set, F.Cu only, 0 overlaps)
# ---------------------------------------------------------------------------
poses = {
    # Per-leg 100nF 100V HF commutation caps (0.90 mm from FET pads, <= 3 mm)
    "C_HF1": (124.425, 89.95,  90.0),
    "C_HF2": (111.900, 89.95,  90.0),
    "C_HF3": ( 99.350, 89.95,  90.0),
    "C_HF4": ( 54.425, 89.95,  90.0),
    "C_HF5": ( 41.900, 89.95,  90.0),
    "C_HF6": ( 29.350, 89.95,  90.0),

    # Motor 1 1206 100uF 50V bulk caps (>= 2 within 6 mm of every leg, outside phase lanes)
    "C65":   ( 94.900, 80.00,  90.0),
    "C66":   ( 97.350, 80.00,  90.0),
    "C67":   ( 99.800, 80.00,  90.0),
    "C68":   (102.250, 80.00,  90.0),
    "C69":   (121.950, 80.00,  90.0),
    "C70":   (124.350, 80.00,  90.0),
    "C73":   (126.750, 80.00,  90.0),
    "C74":   (129.150, 80.00,  90.0),
    "C75":   (125.800,101.80, -90.0),
    "C71":   (128.400,101.80, -90.0),

    # Motor 2 1206 100uF 50V bulk caps
    "C42":   ( 24.900, 80.00,  90.0),
    "C44":   ( 27.350, 80.00,  90.0),
    "C45":   ( 29.800, 80.00,  90.0),
    "C46":   ( 32.250, 80.00,  90.0),
    "C47":   ( 50.450, 80.00,  90.0),
    "C51":   ( 52.850, 80.00,  90.0),
    "C54":   ( 55.250, 80.00,  90.0),
    "C55":   ( 57.650, 80.00,  90.0),
    "C56":   ( 55.800,101.80, -90.0),
    "C53":   ( 58.400,101.80, -90.0),

    # Center bulk caps
    "C57":   ( 60.100, 80.00,  90.0),
    "C60":   ( 62.550, 80.00,  90.0),
    "C61":   ( 86.350, 80.00,  90.0),
    "C64":   ( 88.800, 80.00,  90.0),

    # Motor 1 shunts + Kelvin net-ties & 120R (outside SH_C>=100.70, leaving x=89.45..90.95 west corridor!)
    "R16":   ( 95.750, 99.10,   0.0),
    "NT4":   ( 93.550,101.65,   0.0),
    "R15":   ( 95.750,101.65,   0.0),
    "NT3":   ( 97.950,101.65,   0.0),
    "NT2":   ( 93.550,104.25,   0.0),
    "R11":   ( 95.750,104.25,   0.0),
    "NT1":   ( 97.950,104.25,   0.0),
    "R12":   ( 95.750,106.80,   0.0),

    # Motor 2 shunts + Kelvin net-ties & 120R (exact -70.0 mm mirror)
    "R36":   ( 25.750, 99.10,   0.0),
    "NT8":   ( 23.550,101.65,   0.0),
    "R35":   ( 25.750,101.65,   0.0),
    "NT7":   ( 27.950,101.65,   0.0),
    "NT6":   ( 23.550,104.25,   0.0),
    "R31":   ( 25.750,104.25,   0.0),
    "NT5":   ( 27.950,104.25,   0.0),
    "R32":   ( 25.750,106.80,   0.0),

    # Thermistor dividers within 5 mm of FET row, off power pours
    "TH1":   ( 88.800, 86.20,  90.0),
    "R23":   ( 88.800, 88.35,  90.0),
    "C21":   ( 88.800, 90.50,  90.0),
    "TH5":   ( 61.800, 86.20,  90.0),
    "R63":   ( 61.800, 88.35,  90.0),
    "C102":  ( 61.800, 90.50,  90.0),
}

if not keep_tracks:
    for ref, (x, y, rot) in poses.items():
        fp = board.FindFootprintByReference(ref)
        assert fp is not None, f"Missing footprint {ref}"
        fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        fp.SetOrientationDegrees(rot)
        if ref == "TH1":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x - 1.65, y - 0.55))
        elif ref == "R23":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x - 1.65, y))
        elif ref == "C21":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x - 1.65, y + 0.55))
        elif ref == "TH5":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x + 1.65, y - 0.55))
        elif ref == "R63":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x + 1.65, y))
        elif ref == "C102":
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x + 1.65, y + 0.55))
        elif ref in ("R15", "R35"):
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x - 1.05, y + 1.15))
        elif ref in ("R11", "R31"):
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x + 1.05, y - 1.15))
        else:
            fp.Reference().SetPosition(pcbnew.VECTOR2I_MM(x, y))

# Verify 0 polygon courtyard overlaps across entire board
fps = list(board.GetFootprints())
cys = []
for fp in fps:
    poly = fp.GetCourtyard(pcbnew.F_Cu)
    if not poly.IsEmpty():
        cys.append((fp.GetReference(), poly, poly.BBox()))
overlaps = []
for i in range(len(cys)):
    r1, p1, b1 = cys[i]
    for j in range(i + 1, len(cys)):
        r2, p2, b2 = cys[j]
        if not b1.Intersects(b2):
            continue
        inter = pcbnew.SHAPE_POLY_SET(p1)
        inter.BooleanIntersection(p2)
        if not inter.IsEmpty() and inter.Area() > 0:
            overlaps.append((r1, r2))
assert not overlaps, f"Courtyard overlaps detected: {overlaps}"

fet_pad_boxes = []
all_pads = []
for fp in fps:
    ref = fp.GetReference()
    is_fet = ref in [f"Q{i}" for i in range(1, 13)]
    for p in list(fp.Pads()):
        if not p.GetNumber():
            continue
        bb = p.GetBoundingBox()
        box = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()), p.GetNetname(), p.GetDrillSize().x > 0, ref)
        all_pads.append(box)
        if is_fet:
            fet_pad_boxes.append(box[:4])

# ---------------------------------------------------------------------------
# 2. REBUILD POWER-STAGE ZONES (only when building fresh stage, or keep if keep_tracks)
# ---------------------------------------------------------------------------
if not keep_tracks:
    to_del = []
    for z in board.Zones():
        layers = [board.GetLayerName(l) for l in z.GetLayerSet().CuStack()]
        bb = z.GetBoundingBox()
        net = z.GetNetname()
        if "In1.Cu" in layers or "In2.Cu" in layers:
            continue
        if (net == "GND" and mm(bb.GetTop()) < 20.0 and mm(bb.GetBottom()) > 100.0) or mm(bb.GetBottom()) >= 82.0:
            to_del.append(z)
    for z in to_del:
        board.Remove(z)

    pending_zones = {}
    created_zones = []

    def add_zone(net_name, layer_name, pts, prio=3):
        pending_zones.setdefault((net_name, layer_name, prio), []).append(pts)

    def flush_zones():
        for (net_name, layer_name, prio), poly_list in pending_zones.items():
            clearance, min_thick = (0.22, 0.20) if prio in (0, 2) else (0.25, 0.22)
            netinfo = board.FindNet(net_name)
            assert netinfo is not None, f"Net not found: {net_name}"
            sps = pcbnew.SHAPE_POLY_SET()
            for pts in poly_list:
                sps.NewOutline()
                for (px, py) in pts:
                    sps.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
            sps.Simplify()
            for ci in range(sps.OutlineCount()):
                outline = sps.Outline(ci)
                z = pcbnew.ZONE(board)
                z.SetLayer(board.GetLayerID(layer_name))
                z.SetAssignedPriority(prio)
                z.SetLocalClearance(pcbnew.FromMM(clearance))
                z.SetMinThickness(pcbnew.FromMM(min_thick))
                z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
                z.SetThermalReliefGap(pcbnew.FromMM(0.50))
                z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.80))
                z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
                z.SetIsRuleArea(False)
                zol = z.Outline()
                zol.NewOutline()
                for pi in range(outline.PointCount()):
                    pt = outline.CPoint(pi)
                    zol.Append(pt.x, pt.y)
                board.Add(z)
                z.SetNet(netinfo)
                created_zones.append((z, net_name, layer_name, prio))

    # A0. Outer GND stops at y=82.25 across x=10.8..139.2 (0 shared outer copper between Shunt GND & DRV8301!)
    for lyr in ["F.Cu", "B.Cu"]:
        add_zone("GND", lyr, [
            (1.0, 16.0), (149.0, 16.0), (149.0, 112.6), (139.2, 112.6),
            (139.2, 82.25), (10.8, 82.25), (10.8, 112.6), (1.0, 112.6)
        ], prio=0)

    # A1. Quiet local GND pads for TH1/R23/C21 (x=88.8) and TH5/R63/C102 (x=61.8) -> In1.Cu
    for qx in [88.8, 61.8]:
        for lyr in ["F.Cu", "B.Cu"]:
            add_zone("GND", lyr, [
                (qx - 0.95, 88.55), (qx + 0.40, 88.55), (qx + 0.40, 90.25), (qx - 0.95, 90.25)
            ], prio=2)

    # B. Dedicated J3.1 Battery Return Spine GND (F.Cu & B.Cu) -> In1.Cu
    for lyr in ["F.Cu", "B.Cu"]:
        add_zone("GND", lyr, [
            (64.5, 94.0), (74.8, 94.0), (74.8, 111.8), (64.5, 111.8)
        ], prio=2)

    # C. Dedicated J3.2 Battery VDC Spine + top-row 1206 VDC bars
    add_zone("VDC", "F.Cu", [
        (75.8, 84.5), (85.8, 84.5), (85.8, 111.8), (75.8, 111.8)
    ], prio=3)
    add_zone("VDC", "B.Cu", [
        (64.2, 80.2), (89.5, 80.2), (89.5, 84.5), (85.8, 84.5),
        (85.8, 111.8), (75.8, 111.8), (75.8, 84.5), (64.2, 84.5)
    ], prio=3)

    add_zone("VDC", "F.Cu", [(11.2, 80.15), (19.42, 80.15), (19.42, 83.35), (11.2, 83.35)], prio=3)
    add_zone("VDC", "F.Cu", [
        (24.10, 80.15), (33.45, 80.15), (33.45, 81.95), (33.15, 81.95), (33.15, 82.35),
        (32.2, 84.35), (35.05, 84.35), (35.05, 85.55), (30.5, 85.55), (30.5, 84.15), (26.8, 84.15),
        (26.8, 82.35), (24.10, 82.35)
    ], prio=3)
    add_zone("VDC", "F.Cu", [
        (49.6, 80.15), (66.4, 80.15), (66.4, 82.35), (58.9, 82.35),
        (58.9, 84.15), (57.3, 84.15), (57.3, 82.35), (53.2, 82.35),
        (53.2, 85.55), (43.2, 85.55), (43.2, 84.35), (50.2, 84.35),
        (50.2, 82.35), (49.6, 82.35)
    ], prio=3)

    add_zone("VDC", "F.Cu", [(81.2, 80.15), (89.42, 80.15), (89.42, 83.35), (81.2, 83.35)], prio=3)
    add_zone("VDC", "F.Cu", [
        (94.10, 80.15), (103.45, 80.15), (103.45, 81.95), (103.15, 81.95), (103.15, 82.35),
        (102.2, 84.35), (105.05, 84.35), (105.05, 85.55), (100.5, 85.55), (100.5, 84.15), (96.8, 84.15),
        (96.8, 82.35), (94.10, 82.35)
    ], prio=3)
    add_zone("VDC", "F.Cu", [
        (120.9, 80.15), (136.8, 80.15), (136.8, 84.15), (128.9, 84.15),
        (128.9, 82.35), (127.3, 82.35), (127.3, 84.15), (123.2, 84.15),
        (123.2, 85.55), (113.2, 85.55), (113.2, 84.35), (120.2, 84.35),
        (120.2, 82.35), (120.9, 82.35)
    ], prio=3)

    for dx, pfx in [(0.0, "/Motor Driver"), (-70.0, "/Motor_Driver2")]:
        def S(pts):
            return [(round(x + dx, 3), round(y, 3)) for (x, y) in pts]

        # 1. Shunt GND pour (F.Cu & B.Cu): leaves x < 91.12 open at y=98.2..105.4 for coupled SP/SN corridor!
        add_zone("GND", "F.Cu", S([
            (91.12, 98.25), (94.70, 98.25), (94.70, 109.80), (86.80, 109.80),
            (86.80, 105.45), (93.85, 105.45), (93.85, 100.05), (91.12, 100.05)
        ]), prio=4)
        add_zone("GND", "B.Cu", S([
            (86.80, 98.25), (94.70, 98.25), (94.70, 109.80), (86.80, 109.80)
        ]), prio=4)

        # 2. Leg A GND (Q2/Q8 + C_HF1/4 + East Bulk Caps C75/C71) -> In1.Cu
        add_zone("GND", "F.Cu", S([
            (123.85, 86.25), (129.60, 86.25), (129.60, 90.15), (123.85, 90.15)
        ]), prio=6)
        add_zone("GND", "B.Cu", S([
            (124.45, 86.25), (129.60, 86.25), (129.60, 90.15), (124.45, 90.15)
        ]), prio=6)
        add_zone("GND", "F.Cu", S([
            (124.50, 102.90), (130.80, 102.90), (130.80, 109.50), (124.50, 109.50)
        ]), prio=4)
        add_zone("GND", "B.Cu", S([
            (124.50, 102.20), (130.80, 102.20), (130.80, 109.50), (124.50, 109.50)
        ]), prio=4)

        # 3. South & B.Cu VDC tabs -> In2.Cu
        add_zone("VDC", "F.Cu", S([
            (98.75, 90.20), (105.05, 90.20), (105.05, 91.95), (98.75, 91.95)
        ]), prio=3)
        add_zone("VDC", "F.Cu", S([
            (111.35, 90.20), (125.00, 90.20), (125.00, 91.95), (118.55, 91.95),
            (118.55, 93.15), (115.35, 93.15), (115.35, 91.95), (111.35, 91.95)
        ]), prio=3)
        add_zone("VDC", "F.Cu", S([
            (124.50, 98.20), (130.80, 98.20), (130.80, 101.00), (124.50, 101.00)
        ]), prio=3)
        add_zone("VDC", "B.Cu", [
            (20.0 if dx < 0 else 81.2, 80.2), (33.2 if dx < 0 else 103.2, 80.2),
            (33.2 if dx < 0 else 103.2, 84.1), (20.0 if dx < 0 else 81.2, 84.1)
        ], prio=3)
        add_zone("VDC", "B.Cu", S([
            (113.20, 80.20), (130.80, 80.20), (130.80, 85.40), (113.20, 85.40)
        ]), prio=3)
        add_zone("VDC", "B.Cu", S([
            (98.75, 90.20), (100.10, 90.20), (100.10, 91.95), (98.75, 91.95)
        ]), prio=6)
        add_zone("VDC", "B.Cu", S([
            (115.35, 91.20), (118.55, 91.20), (118.55, 93.15), (115.35, 93.15)
        ]), prio=6)
        add_zone("VDC", "B.Cu", S([
            (124.50, 96.50), (130.80, 96.50), (130.80, 100.80), (124.50, 100.80)
        ]), prio=3)

        # 4. SL_C (west edge = 91.95, leaving x=89.35..91.70 open for coupled SP/SN pairs!)
        add_zone(f"{pfx}/SL_C", "F.Cu", S([
            (91.95, 85.40), (93.45, 85.40), (93.45, 86.20), (98.80, 86.20),
            (98.80, 87.35), (99.90, 87.35), (99.90, 89.85), (98.80, 89.85),
            (98.80, 90.55), (91.95, 90.55)
        ]), prio=6)
        add_zone(f"{pfx}/SL_C", "F.Cu", S([
            (94.95, 93.60), (98.85, 93.60), (98.85, 98.10), (100.40, 98.10),
            (100.40, 100.15), (99.15, 100.15), (99.15, 102.05), (98.20, 102.05),
            (98.20, 100.50), (94.95, 100.50)
        ]), prio=6)
        add_zone(f"{pfx}/SL_C", "B.Cu", S([
            (91.95, 85.40), (98.85, 85.40), (98.85, 100.50), (94.95, 100.50),
            (94.95, 93.60), (91.95, 93.60)
        ]), prio=6)

        # 5. SL_B
        add_zone(f"{pfx}/SL_B", "F.Cu", S([
            (104.95, 86.00), (109.95, 86.00), (109.95, 87.10), (113.50, 87.10),
            (113.50, 89.95), (109.95, 89.95), (109.95, 90.40), (104.95, 90.40)
        ]), prio=6)
        add_zone(f"{pfx}/SL_B", "F.Cu", S([
            (98.20, 103.80), (100.40, 103.80), (100.40, 110.50), (94.95, 110.50),
            (94.95, 105.45), (98.20, 105.45)
        ]), prio=6)
        add_zone(f"{pfx}/SL_B", "B.Cu", S([
            (104.95, 84.35), (113.50, 84.35), (113.50, 90.40), (104.95, 90.40)
        ]), prio=6)
        add_zone(f"{pfx}/SL_B", "B.Cu", S([
            (99.20, 84.35), (106.00, 84.35), (106.00, 85.85), (99.20, 85.85)
        ]), prio=6)
        add_zone(f"{pfx}/SL_B", "B.Cu", S([
            (99.20, 84.35), (100.40, 84.35), (100.40, 110.50), (94.95, 110.50),
            (94.95, 103.80), (99.20, 103.80)
        ]), prio=6)

        # 6. PHASE C: SH_C (x = 100.68 .. 107.90 along shunt bay -> >= 6.17 mm wide on F.Cu & B.Cu!)
        add_zone(f"{pfx}/SH_C", "F.Cu", S([
            (93.60, 84.45), (99.85, 84.45), (99.85, 86.20), (104.55, 86.20),
            (104.55, 90.00), (100.20, 90.00), (100.20, 88.25), (99.05, 88.25),
            (99.05, 85.55), (93.60, 85.55)
        ]), prio=5)
        add_zone(f"{pfx}/SH_C", "F.Cu", S([
            (104.10, 89.50), (105.88, 89.50), (105.88, 92.50), (105.24, 92.50),
            (105.24, 90.00), (104.10, 90.00)
        ]), prio=5)
        add_zone(f"{pfx}/SH_C", "F.Cu", S([
            (93.60, 90.85), (98.40, 90.85), (98.40, 92.20), (106.00, 92.20),
            (106.95, 96.00), (107.90, 103.90), (107.90, 109.20), (100.68, 109.20),
            (100.68, 97.90), (99.15, 95.40), (93.60, 92.40)
        ]), prio=5)
        add_zone(f"{pfx}/SH_C", "B.Cu", S([
            (100.68, 86.20), (104.55, 86.20), (104.55, 90.90), (106.90, 90.90),
            (107.15, 96.00), (107.90, 103.90), (107.90, 109.20), (100.68, 109.20)
        ]), prio=5)

        # 7. PHASE B: SH_B (>= 6.05 mm wide on F.Cu & B.Cu!)
        add_zone(f"{pfx}/SH_B", "F.Cu", S([
            (106.15, 84.45), (112.40, 84.45), (112.40, 86.60), (115.60, 86.60),
            (115.60, 87.60), (111.15, 87.60), (111.15, 85.55), (106.15, 85.55)
        ]), prio=5)
        add_zone(f"{pfx}/SH_B", "F.Cu", S([
            (113.80, 86.25), (118.35, 86.25), (118.35, 90.15), (113.80, 90.15)
        ]), prio=5)
        add_zone(f"{pfx}/SH_B", "F.Cu", S([
            (106.15, 90.85), (111.15, 90.85), (111.15, 92.20), (114.95, 92.20),
            (114.95, 93.50), (114.55, 102.50), (113.85, 104.00), (113.85, 109.20),
            (108.15, 109.20), (108.15, 104.00), (107.40, 96.00), (106.25, 92.20)
        ]), prio=5)
        add_zone(f"{pfx}/SH_B", "B.Cu", S([
            (113.80, 85.95), (118.45, 85.95), (118.45, 90.95), (115.00, 93.50),
            (114.55, 102.50), (113.85, 104.00), (113.85, 109.20), (108.15, 109.20),
            (108.15, 104.00), (107.40, 96.00), (107.15, 90.90), (113.80, 90.90)
        ]), prio=5)

        # 8. PHASE A: SH_A (>= 6.23 mm wide on F.Cu & B.Cu!)
        add_zone(f"{pfx}/SH_A", "F.Cu", S([
            (123.30, 84.45), (130.15, 84.45), (130.15, 85.55), (125.10, 85.55),
            (125.10, 85.95), (123.30, 85.95)
        ]), prio=5)
        add_zone(f"{pfx}/SH_A", "F.Cu", S([
            (119.30, 86.25), (121.00, 86.25), (121.00, 87.25), (123.55, 87.25),
            (123.55, 90.15), (119.30, 90.15)
        ]), prio=5)
        add_zone(f"{pfx}/SH_A", "F.Cu", S([
            (122.70, 85.55), (123.55, 85.55), (123.55, 87.50), (122.70, 87.50)
        ]), prio=5)
        add_zone(f"{pfx}/SH_A", "F.Cu", S([
            (125.40, 90.85), (130.20, 90.85), (130.20, 96.80), (124.10, 96.80),
            (124.10, 109.20), (114.15, 109.20), (114.15, 104.00), (114.90, 102.50),
            (118.95, 93.50), (118.95, 92.20), (125.40, 92.20)
        ]), prio=5)
        add_zone(f"{pfx}/SH_A", "B.Cu", S([
            (118.85, 86.00), (124.10, 86.00), (124.10, 90.85), (130.20, 90.85),
            (130.20, 95.60), (124.10, 95.60), (124.10, 109.20), (114.15, 109.20),
            (114.15, 104.00), (114.90, 102.50), (118.95, 93.50), (118.85, 90.90)
        ]), prio=5)

    flush_zones()

if no_vias:
    # Fill power zones (except prio-0 outer GND) so FreeRouting respects filled power pours!
    filler = pcbnew.ZONE_FILLER(board)
    non_outer_gnd = [
        z for z in board.Zones()
        if not (z.GetNetname() == "GND" and z.GetAssignedPriority() == 0 and (z.IsOnLayer(pcbnew.F_Cu) or z.IsOnLayer(pcbnew.B_Cu)))
    ]
    filler.Fill(non_outer_gnd)
    pcbnew.SaveBoard(CAND_PCB, board)
    os._exit(0)

# ---------------------------------------------------------------------------
# 3. PLACE 0.60/0.30 mm STITCHING VIAS (>= 24 AT EVERY TRANSITION, 0 IN FET PADS)
#    AND RESTORE UPPER-BOARD BASELINE VIAS (y < 78.2 mm)
# ---------------------------------------------------------------------------
# First restore upper-board baseline vias (y < 78.2 mm) from BASE_PCB if they were stripped for routing!
existing_vias = [t for t in list(board.GetTracks()) if t.GetClass() == "PCB_VIA"]
for v in existing_vias:
    board.Remove(v)

base_board = pcbnew.LoadBoard(BASE_PCB)
placed_vias = []

track_segs = []
for t in board.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        s, e = t.GetStart(), t.GetEnd()
        track_segs.append((mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()), t.GetNetname()))

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

def can_place_via(x, y, net_name, via_dia=0.60):
    vr = via_dia / 2.0
    for (x1, y1, x2, y2) in fet_pad_boxes:
        if (x1 - vr - 0.12) <= x <= (x2 + vr + 0.12) and (y1 - vr - 0.12) <= y <= (y2 + vr + 0.12):
            return False
    for (x1, y1, x2, y2, pnet, is_pth, ref) in all_pads:
        margin = 0.32 if pnet != net_name else (0.35 if is_pth else 0.08)
        if (x1 - vr - margin) <= x <= (x2 + vr + margin) and (y1 - vr - margin) <= y <= (y2 + vr + margin):
            return False
    for (sx, sy, ex, ey, sw, snet) in track_segs:
        if snet != net_name:
            if seg_dist(x, y, sx, sy, ex, ey) < (vr + sw / 2.0 + 0.26):
                return False
    for (vx, vy, vnet, vdia) in placed_vias:
        min_d = (vr + vdia / 2.0 + 0.08) if vnet == net_name else (vr + vdia / 2.0 + 0.28)
        if math.hypot(x - vx, y - vy) < min_d - 1e-6:
            return False
    return True

# Copy upper-board vias (y < 78.2 mm) from baseline v8.2 untouched unless a new sense track passes at y=75.8..78.1
for bt in base_board.GetTracks():
    if bt.GetClass() == "PCB_VIA":
        bx, by = mm(bt.GetPosition().x), mm(bt.GetPosition().y)
        if by < 78.2:
            bnet = bt.GetNetname()
            bdia = mm(bt.GetWidth(pcbnew.F_Cu))
            bdrl = mm(bt.GetDrillValue())
            if can_place_via(bx, by, bnet, via_dia=bdia):
                nv = pcbnew.PCB_VIA(board)
                nv.SetPosition(bt.GetPosition())
                nv.SetWidth(bt.GetWidth(pcbnew.F_Cu))
                nv.SetDrill(bt.GetDrillValue())
                nv.SetViaType(pcbnew.VIATYPE_THROUGH)
                nv.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                board.Add(nv)
                nv.SetNet(board.FindNet(bnet))
                nv.SetIsFree(False)
                placed_vias.append((bx, by, bnet, bdia))

def place_via_grid(net_name, xs, ys, max_count=None):
    netinfo = board.FindNet(net_name)
    assert netinfo is not None, f"Missing net {net_name}"
    added = 0
    for y in ys:
        for x in xs:
            if max_count and added >= max_count:
                return added
            rx, ry = round(x, 3), round(y, 3)
            if can_place_via(rx, ry, net_name, via_dia=0.60):
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I_MM(rx, ry))
                v.SetWidth(pcbnew.FromMM(0.60))
                v.SetDrill(pcbnew.FromMM(0.30))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                board.Add(v)
                v.SetNet(netinfo)
                v.SetIsFree(False)
                placed_vias.append((rx, ry, net_name, 0.60))
                added += 1
    return added

def frange(a, b, step):
    out = []
    v = a
    while v <= b + 1e-6:
        out.append(round(v, 3))
        v += step
    return out

# Quiet TH1/TH5 divider GND vias
for qx in [88.15, 61.15]:
    qv = pcbnew.PCB_VIA(board)
    qv.SetPosition(pcbnew.VECTOR2I_MM(qx, 89.42))
    qv.SetWidth(pcbnew.FromMM(0.60))
    qv.SetDrill(pcbnew.FromMM(0.30))
    qv.SetViaType(pcbnew.VIATYPE_THROUGH)
    qv.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(qv)
    qv.SetNet(board.FindNet("GND"))
    qv.SetIsFree(False)
    placed_vias.append((qx, 89.42, "GND", 0.60))

# J3 battery spine vias
c_j3_gnd = place_via_grid("GND", frange(65.2, 74.2, 0.95), frange(94.6, 102.2, 0.95), max_count=32)
c_j3_vdc = place_via_grid("VDC", frange(76.4, 85.2, 0.95), frange(85.2, 102.2, 1.15), max_count=36)
print(f"J3 spine vias: GND={c_j3_gnd}, VDC={c_j3_vdc}")

for dx, pfx in [(0.0, "/Motor Driver"), (-70.0, "/Motor_Driver2")]:
    def Sx(vals): return [round(v + dx, 3) for v in vals]

    # 1. Shunt GND -> In1.Cu + B.Cu (>= 28 vias)
    n_sgnd = place_via_grid("GND", Sx(frange(87.20, 94.30, 0.76)), frange(105.80, 109.45, 0.80), max_count=30)

    # 2. Leg A GND + Bulk Cap GND -> In1.Cu + B.Cu (>= 28 vias)
    n_agnd = 0
    n_agnd += place_via_grid("GND", Sx([124.80, 125.52]), frange(86.55, 89.65, 0.72))
    n_agnd += place_via_grid("GND", Sx(frange(125.00, 130.30, 0.85)), frange(103.50, 108.80, 0.85), max_count=20)
    n_agnd += place_via_grid("GND", Sx(frange(121.40, 130.20, 1.10)), [78.00], max_count=8)

    # 3. VDC (F/B/In2) (>= 44 vias per motor, strictly inside x = 20..131!)
    n_vdc = 0
    n_vdc += place_via_grid("VDC", Sx(frange(97.00, 102.20, 0.75)), [82.65, 83.45])
    n_vdc += place_via_grid("VDC", Sx(frange(121.80, 127.00, 0.75)), [82.65, 83.45])
    n_vdc += place_via_grid("VDC", Sx(frange(129.05, 130.45, 0.70)), [82.65, 83.45])
    n_vdc += place_via_grid("VDC", Sx([99.10, 99.80]), [91.62])
    n_vdc += place_via_grid("VDC", Sx(frange(115.70, 118.20, 0.75)), [92.15, 92.85])
    n_vdc += place_via_grid("VDC", Sx(frange(125.00, 130.30, 0.78)), [98.55, 99.45])

    # 4. SL_C: >= 25 at Q6 source (F->B) AND >= 25 at R16.2 shunt (B->F)!
    n_slc_q = place_via_grid(f"{pfx}/SL_C", Sx([92.30, 93.02, 93.75]), frange(85.75, 90.25, 0.70))
    n_slc_q += place_via_grid(f"{pfx}/SL_C", Sx([97.78, 98.48]), frange(86.50, 90.20, 0.70))
    n_slc_r = place_via_grid(f"{pfx}/SL_C", Sx(frange(95.30, 98.50, 0.72)), frange(93.95, 97.95, 0.72), max_count=26)

    # 5. SL_B: >= 26 at Q4 source (F->B) AND >= 26 at R12.2 shunt (B->F)!
    n_slb_q = place_via_grid(f"{pfx}/SL_B", Sx([105.25, 105.98]), frange(86.30, 90.10, 0.72))
    n_slb_q += place_via_grid(f"{pfx}/SL_B", Sx(frange(110.30, 113.20, 0.72)), [87.42, 88.14, 88.86, 89.62])
    n_slb_r = place_via_grid(f"{pfx}/SL_B", Sx(frange(95.30, 100.05, 0.72)), [105.75, 107.90, 108.62, 109.34, 110.06], max_count=28)

    # 6. SH_C (F<->B): >= 36 vias outside FET pads!
    n_shc = 0
    n_shc += place_via_grid(f"{pfx}/SH_C", Sx([100.98]), [86.65, 87.45, 88.25, 89.05])
    n_shc += place_via_grid(f"{pfx}/SH_C", Sx(frange(101.00, 105.85, 0.82)), frange(92.55, 96.55, 0.95))
    n_shc += place_via_grid(f"{pfx}/SH_C", Sx(frange(101.00, 106.85, 0.92)), frange(98.20, 102.80, 1.10), max_count=16)

    # 7. SH_B (F<->B): >= 30 vias outside FET pads!
    n_shb = 0
    n_shb += place_via_grid(f"{pfx}/SH_B", Sx([117.32, 118.08]), frange(87.25, 89.90, 0.75))
    n_shb += place_via_grid(f"{pfx}/SH_B", Sx(frange(107.65, 114.25, 0.90)), frange(92.55, 102.55, 1.20), max_count=26)

    # 8. SH_A (F<->B): >= 32 vias outside FET pads!
    n_sha = 0
    n_sha += place_via_grid(f"{pfx}/SH_A", Sx([122.78, 123.25]), [87.60, 88.35, 89.10, 89.85])
    n_sha += place_via_grid(f"{pfx}/SH_A", Sx(frange(119.15, 123.65, 0.88)), [92.75, 93.75, 94.75, 95.75])
    n_sha += place_via_grid(f"{pfx}/SH_A", Sx(frange(117.65, 123.65, 0.92)), [98.50, 99.65, 100.80, 101.95], max_count=16)

    print(f"{pfx}: ShuntGND={n_sgnd}, LegAGND={n_agnd}, VDC={n_vdc}, SL_C=({n_slc_q}+{n_slc_r}={n_slc_q+n_slc_r}), SL_B=({n_slb_q}+{n_slb_r}={n_slb_q+n_slb_r}), SH_C={n_shc}, SH_B={n_shb}, SH_A={n_sha}")

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(CAND_PCB, board)
print("Saved stage-3 final candidate:", CAND_PCB, flush=True)
os._exit(0)
