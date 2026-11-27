#!/usr/bin/env python3
"""
Idempotently apply Unit 2 PCB layout, heatsink clearance keepouts, aligned H1/H3 copper pours,
and 6x10 (60x 1206) phase-leg VDC decoupling + via stitching on a staged candidate
of bldc_motor_cntroller_v9_4.kicad_pcb.

Interpreter: /usr/bin/python3 (KiCad 10.0.8 native pcbnew)
Usage: /usr/bin/python3 .copperpilot/tools/apply_v9_4_unit2_pcb.py <staged_candidate.kicad_pcb>
"""
import sys
import pcbnew

PCB_PATH = sys.argv[1]
if ".copperpilot/tmp/staging/" not in PCB_PATH:
    raise RuntimeError(f"Refusing to run outside staging candidate: {PCB_PATH}")

board = pcbnew.LoadBoard(PCB_PATH)
board.BuildListOfNets()
net_map = {str(k): v for k, v in board.GetNetInfo().NetsByName().items()}
DX = 118.0  # Exact channel symmetry: M0 = M1 + 118.0 mm


def get_net(name):
    ni = net_map.get(name) or board.FindNet(name)
    if ni is None:
        raise RuntimeError(f"Net not found: {name}")
    return ni


def assign_net(item, name):
    ni = get_net(name)
    item.SetNet(ni)
    if item.GetNetname() != name:
        item.SetNetCode(ni.GetNetCode())
    if item.GetNetname() != name:
        raise RuntimeError(f"Failed to assign net {name!r}: got {item.GetNetname()!r} (code={ni.GetNetCode()})")


def set_pose(ref, x, y, rot_deg=None):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise RuntimeError(f"Footprint not found: {ref}")
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    if rot_deg is not None:
        fp.SetOrientationDegrees(rot_deg)
    return fp


def ensure_field(fp, name, value):
    fp.SetField(name, value)
    fld = fp.GetField(name)
    if fld is not None:
        fld.SetVisible(False)


# 1. Ensure H2 & H4 are removed and H1 & H3 are aligned at (5.50, 92.00) & (214.50, 92.00)
for stale in ("H2", "H4"):
    fp_s = board.FindFootprintByReference(stale)
    if fp_s is not None:
        board.Remove(fp_s)

set_pose("H1", 5.50, 92.00, 0.0)
set_pose("H3", 214.50, 92.00, 0.0)
# Move Q2 Reference out from under H3 solder mask opening (was at 211.5, 92.0)
fp_q2 = board.FindFootprintByReference("Q2")
if fp_q2 is not None:
    fp_q2.Reference().SetTextAngleDegrees(0.0)
    fp_q2.Reference().SetPosition(pcbnew.VECTOR2I_MM(207.00, 98.30))

# 2. Idempotently shift U2 (M1) and U1 (M0 + Buck) clusters North by -5.00 mm (68.5 -> 63.5)
u2_shift_refs = [
    "U2", "C22", "C23", "C24", "C25", "C26", "C29", "C30", "C31",
    "C32", "C33", "C34", "C38", "R26", "R27", "R30", "R37", "R38",
    "R39", "R40", "R42", "TH2",
]
u1_shift_refs = [
    "U1", "L1", "D1", "C1", "C2", "C3", "C4", "C5", "C8", "C9",
    "C10", "C11", "C12", "C13", "C14", "C15", "C17", "C18", "C19",
    "C20", "C36", "C101", "R3", "R4", "R5", "R7", "R10",
    "R17", "R18", "R19", "R20", "R21", "R22", "R62", "TH4", "R6",
]
u1_fp = board.FindFootprintByReference("U1")
if pcbnew.ToMM(u1_fp.GetPosition().y) > 66.0:
    for ref in u2_shift_refs + u1_shift_refs:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            raise RuntimeError(f"Missing driver-cluster ref: {ref}")
        pos = fp.GetPosition()
        fp.SetPosition(pcbnew.VECTOR2I_MM(round(pcbnew.ToMM(pos.x), 4), round(pcbnew.ToMM(pos.y) - 5.0, 4)))

# 3. Place 6 x 10 = 60 1206 phase-leg VDC capacitors at y = 75.50, rot = 90.0 deg (Pad 1 South = VDC, Pad 2 North = GND)
fp_c35 = board.FindFootprintByReference("C35")
c35_ref_vis = fp_c35.Reference().IsVisible()

banks = [
    (13.40,  ["C35", "C39", "C40", "C42", "C44", "C118", "C119", "C120", "C121", "C122"]),
    (43.40,  ["C45", "C46", "C47", "C51", "C54", "C123", "C124", "C125", "C126", "C127"]),
    (70.10,  ["C55", "C57", "C60", "C56", "C53", "C128", "C129", "C130", "C131", "C132"]),
    (131.40, ["C16", "C61", "C64", "C65", "C66", "C103", "C104", "C105", "C106", "C107"]),
    (161.40, ["C67", "C68", "C69", "C70", "C73", "C108", "C109", "C110", "C111", "C112"]),
    (188.10, ["C74", "C76", "C77", "C75", "C71", "C113", "C114", "C115", "C116", "C117"]),
]

for x0, refs in banks:
    for k, ref in enumerate(refs):
        cx = round(x0 + 2.35 * k, 4)
        fp = set_pose(ref, cx, 75.50, 90.0)
        ensure_field(fp, "MPN", "HMK325C7475KN-TE" if ref in ("C16", "C35") else "GMK105CC6105MV-F")
        rtxt = fp.Reference()
        rtxt.SetTextSize(pcbnew.VECTOR2I_MM(0.80, 0.80))
        rtxt.SetTextThickness(pcbnew.FromMM(0.12))
        rtxt.SetTextAngleDegrees(90.0)
        rtxt.SetPosition(pcbnew.VECTOR2I_MM(cx, 72.10))
        # Hide F.SilkS Reference only for dense bank items to prevent solder-mask clipping while keeping F.Fab ${REFERENCE}
        rtxt.SetVisible(False)

for ref, cx in [("C78", 11.40), ("C79", 68.20), ("C80", 129.40), ("C81", 186.20)]:
    fp = set_pose(ref, cx, 75.50, 90.0)
    rtxt = fp.Reference()
    rtxt.SetTextSize(pcbnew.VECTOR2I_MM(0.80, 0.80))
    rtxt.SetTextThickness(pcbnew.FromMM(0.12))
    rtxt.SetTextAngleDegrees(90.0)
    rtxt.SetPosition(pcbnew.VECTOR2I_MM(cx, 71.75))
    rtxt.SetVisible(c35_ref_vis)

# 4. Relocate C_HF1-C_HF6, 12x Gate Resistors, and Heatsink-Edge NTCs strictly North of y = 81.50 mm
chf_poses = [
    ("C_HF6",  13.20, 80.00, -90.0),
    ("C_HF5",  43.00, 80.00, -90.0),
    ("C_HF4",  94.30, 80.00, -90.0),
    ("C_HF3", 131.20, 80.00, -90.0),
    ("C_HF2", 161.00, 80.00, -90.0),
    ("C_HF1", 212.40, 80.00, -90.0),
]
for ref, x, y, rot in chf_poses:
    fp = set_pose(ref, x, y, rot)
    rtxt = fp.Reference()
    rtxt.SetTextSize(pcbnew.VECTOR2I_MM(0.80, 0.80))
    rtxt.SetTextThickness(pcbnew.FromMM(0.12))
    rtxt.SetTextAngleDegrees(0.0)
    rtxt.SetPosition(pcbnew.VECTOR2I_MM(x - 2.10 if x < 90 or (125 < x < 180) else x + 2.20, y))

rgate_poses = [
    ("R34",  15.60, 80.50, -90.0),
    ("R33",  36.40, 80.50, -90.0),
    ("R29",  45.60, 80.50, -90.0),
    ("R28",  66.40, 80.50, -90.0),
    ("R24",  71.80, 80.50, -90.0),
    ("R25",  92.30, 80.50, -90.0),
    ("R14", 133.60, 80.50, -90.0),
    ("R13", 154.40, 80.50, -90.0),
    ("R9",  163.60, 80.50, -90.0),
    ("R8",  184.40, 80.50, -90.0),
    ("R1",  189.80, 80.50, -90.0),
    ("R2",  210.30, 80.50, -90.0),
]
for ref, x, y, rot in rgate_poses:
    fp = set_pose(ref, x, y, rot)
    rtxt = fp.Reference()
    rtxt.SetTextSize(pcbnew.VECTOR2I_MM(0.80, 0.80))
    rtxt.SetTextThickness(pcbnew.FromMM(0.12))
    rtxt.SetTextAngleDegrees(0.0)
    rtxt.SetPosition(pcbnew.VECTOR2I_MM(x, y + 1.45))
    rtxt.SetVisible(c35_ref_vis)

ntc_poses = [
    ("TH5",   8.00, 80.50, -90.0),
    ("R63",   6.20, 80.50, -90.0),
    ("C102",  4.40, 80.50,  90.0),
    ("TH1", 126.50, 78.00, -90.0),
    ("R23", 124.80, 78.00, -90.0),
    ("C21", 123.10, 78.00,  90.0),
]
for ref, x, y, rot in ntc_poses:
    fp = set_pose(ref, x, y, rot)
    rtxt = fp.Reference()
    rtxt.SetTextSize(pcbnew.VECTOR2I_MM(0.80, 0.80))
    rtxt.SetTextThickness(pcbnew.FromMM(0.12))
    rtxt.SetTextAngleDegrees(90.0)
    rtxt.SetPosition(pcbnew.VECTOR2I_MM(x, y - 2.35))
    rtxt.SetVisible(c35_ref_vis)

# 5. Idempotently remove zones & vias in modified bands
zones_to_remove = []
for z in list(board.Zones()):
    outline = z.Outline()
    pts = []
    for ci in range(outline.OutlineCount()):
        ln = outline.Outline(ci)
        for pi in range(ln.PointCount()):
            pt = ln.CPoint(pi)
            pts.append((pcbnew.ToMM(pt.x), pcbnew.ToMM(pt.y)))
    if not pts:
        continue
    min_x, max_x = min(p[0] for p in pts), max(p[0] for p in pts)
    min_y, max_y = min(p[1] for p in pts), max(p[1] for p in pts)
    net_name = z.GetNetname()
    layers = [board.GetLayerName(lid) for lid in z.GetLayerSet().Seq()]

    if z.GetIsRuleArea():
        if z.GetDoNotAllowVias() or z.GetDoNotAllowFootprints():
            zones_to_remove.append(z)
        continue

    if "In2.Cu" in layers:
        zones_to_remove.append(z)
        continue

    if net_name == "GND" and 72.0 <= min_y <= 78.0 and max_y <= 81.0:
        zones_to_remove.append(z)
        continue

    if net_name == "VDC" and 75.5 <= min_y <= 81.2 and max_y < 100.0:
        zones_to_remove.append(z)
        continue

    if net_name == "VDC" and "F.Cu" in layers and 67.5 <= min_y <= 75.5 and max_y <= 77.0 and (max_x < 60.0 or min_x > 160.0):
        zones_to_remove.append(z)
        continue
    if net_name in ("+5V", "GND") and "F.Cu" in layers and min_x > 183.0 and 62.0 <= min_y <= 74.0 and max_y <= 75.5:
        zones_to_remove.append(z)
        continue

    if net_name.endswith("/SL_C") or net_name.endswith("/SL_B"):
        if "F.Cu" in layers and "B.Cu" not in layers:
            zones_to_remove.append(z)
        continue

    if net_name == "GND":
        if "F.Cu" in layers and 86.0 <= min_x <= 87.5 and max_y > 125.0:
            zones_to_remove.append(z)
            continue
        if "B.Cu" in layers and 93.0 <= min_x <= 94.0 and max_y <= 90.5:
            zones_to_remove.append(z)
            continue
        if min_x >= 204.0:
            zones_to_remove.append(z)
            continue
        if max_x <= 9.5 and min_y >= 40.0:
            zones_to_remove.append(z)
            continue

for z in zones_to_remove:
    board.Remove(z)

vias_to_remove = []
for trk in list(board.GetTracks()):
    if trk.Type() == pcbnew.PCB_VIA_T:
        vx = pcbnew.ToMM(trk.GetPosition().x)
        vy = pcbnew.ToMM(trk.GetPosition().y)
        if 60.0 <= vy < 86.0:
            if 98.0 <= vx <= 124.5 and vy < 76.0:
                continue
            vias_to_remove.append(trk)
        elif 89.0 <= vy <= 96.0 and (vx >= 210.0 or (92.5 <= vx <= 99.0)):
            vias_to_remove.append(trk)

for v in vias_to_remove:
    board.Remove(v)

# Deduplicate any pre-existing co-located vias before adding new ones
seen_vias = set()
for trk in list(board.GetTracks()):
    if trk.Type() == pcbnew.PCB_VIA_T:
        key = (round(pcbnew.ToMM(trk.GetPosition().x), 2), round(pcbnew.ToMM(trk.GetPosition().y), 2))
        if key in seen_vias:
            board.Remove(trk)
        else:
            seen_vias.add(key)


def add_copper_zone(net_name, layers, pts, priority=3, clearance=0.25, min_thick=0.25, solid_pads=True):
    z = pcbnew.ZONE(board)
    assign_net(z, net_name)
    lset = pcbnew.LSET()
    for l in layers:
        lset.AddLayer(board.GetLayerID(l))
    z.SetLayerSet(lset)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(clearance))
    z.SetMinThickness(pcbnew.FromMM(min_thick))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid_pads else pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(pcbnew.FromMM(0.25))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.50))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(pcbnew.FromMM(round(x, 4)), pcbnew.FromMM(round(y, 4)))
    board.Add(z)
    return z


def add_keepout(layers, pts, no_tracks=False, no_vias=False, no_pours=False, no_footprints=False):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(no_tracks)
    z.SetDoNotAllowVias(no_vias)
    z.SetDoNotAllowZoneFills(no_pours)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(no_footprints)
    lset = pcbnew.LSET()
    for l in layers:
        lset.AddLayer(board.GetLayerID(l))
    z.SetLayerSet(lset)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(pcbnew.FromMM(round(x, 4)), pcbnew.FromMM(round(y, 4)))
    board.Add(z)
    return z


def add_via(x, y, net_name, size=0.60, drill=0.30):
    key = (round(x, 2), round(y, 2))
    if key in seen_vias:
        return None
    seen_vias.add(key)
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(round(x, 4), round(y, 4)))
    v.SetWidth(pcbnew.FromMM(size))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(board.GetLayerID("F.Cu"), board.GetLayerID("B.Cu"))
    v.SetIsFree(True)
    board.Add(v)
    assign_net(v, net_name)
    return v


# 6. Recreate In2.Cu +3.3V & VDC planes with -5.0 mm North shift under U1/U2 (y = 57.4 / 58.2)
add_copper_zone("+3.3V", ["In2.Cu"], [
    (1.0, 15.55), (219.0, 15.55), (219.0, 57.40),
    (138.0, 57.40), (138.0, 59.20), (110.5, 59.20), (110.5, 57.40),
    (1.0, 57.40),
], priority=0, clearance=0.25, min_thick=0.25, solid_pads=False)

add_copper_zone("VDC", ["In2.Cu"], [
    (1.0, 58.20), (111.2, 58.20), (111.2, 60.00), (137.2, 60.00), (137.2, 58.20),
    (219.0, 58.20), (219.0, 129.00), (1.0, 129.00),
], priority=0, clearance=0.25, min_thick=0.25, solid_pads=False)

# 7. Recreate shifted U2/U1 local PVDD1 VDC padlets (F.Cu+B.Cu so vias tie F.Cu, In2.Cu, and B.Cu!) & U1 Buck +5V / GND pours
add_copper_zone("VDC", ["F.Cu", "B.Cu"], [(46.20, 68.00), (47.40, 68.00), (47.40, 69.50), (46.20, 69.50)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(46.80, 69.05, "VDC", 0.60, 0.30)

add_copper_zone("VDC", ["F.Cu", "B.Cu"], [(164.20, 68.00), (165.40, 68.00), (165.40, 69.50), (164.20, 69.50)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(164.80, 69.05, "VDC", 0.60, 0.30)

add_copper_zone("VDC", ["F.Cu", "B.Cu"], [(179.45, 69.85), (180.25, 69.85), (180.25, 71.60), (179.45, 71.60)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(179.85, 71.25, "VDC", 0.60, 0.30)

add_copper_zone("+5V", ["F.Cu"], [
    (192.00, 62.40), (202.40, 62.40), (202.40, 64.25), (195.20, 64.25),
    (195.20, 65.30), (192.00, 65.30),
], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["F.Cu"], [
    (184.20, 68.30), (186.20, 68.30), (186.20, 65.40), (202.40, 65.40),
    (202.40, 69.80), (184.20, 69.80),
], priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(185.00, 69.10, "GND", 0.60, 0.30)
for vx in [196.20, 198.60, 201.40]:
    add_via(vx, 67.20, "GND", 0.60, 0.30)

# 8. Symmetric M1 (dx=0) and M0 (dx=+118.0) 10-Cap Phase Banks, SL_C/SL_B C_HF Return Strips, and Stitching Vias
for ch_idx, dx in enumerate([0.0, DX]):
    ns = "/Motor_Driver2" if ch_idx == 0 else "/Motor Driver"

    add_copper_zone(f"{ns}/SL_C", ["F.Cu"], [
        (10.85 + dx, 80.25), (14.45 + dx, 80.25), (14.45 + dx, 89.90),
        (16.20 + dx, 89.90), (16.20 + dx, 90.55), (21.90 + dx, 90.55),
        (21.90 + dx, 95.20), (16.45 + dx, 95.20), (16.45 + dx, 103.50),
        (10.85 + dx, 103.50),
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone(f"{ns}/SL_B", ["F.Cu"], [
        (40.50 + dx, 80.25), (44.45 + dx, 80.25), (44.45 + dx, 89.90),
        (46.20 + dx, 89.90), (46.20 + dx, 90.55), (51.90 + dx, 90.55),
        (51.90 + dx, 95.20), (46.45 + dx, 95.20), (46.45 + dx, 103.50),
        (40.50 + dx, 103.50),
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone("GND", ["F.Cu", "B.Cu"], [(10.80 + dx, 72.55), (35.55 + dx, 72.55), (35.55 + dx, 75.20), (10.80 + dx, 75.20)],
                    priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
    add_copper_zone("GND", ["F.Cu", "B.Cu"], [(42.40 + dx, 72.55), (65.55 + dx, 72.55), (65.55 + dx, 75.20), (42.40 + dx, 75.20)],
                    priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
    add_copper_zone("GND", ["F.Cu", "B.Cu"], [(67.60 + dx, 72.55), (92.25 + dx, 72.55), (92.25 + dx, 75.20), (67.60 + dx, 75.20)],
                    priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)

    add_copper_zone("VDC", ["F.Cu"], [
        (10.80 + dx, 75.80), (35.55 + dx, 75.80), (35.55 + dx, 79.40),
        (35.40 + dx, 79.40), (35.40 + dx, 99.20), (28.80 + dx, 99.20),
        (28.80 + dx, 95.55), (34.55 + dx, 95.55), (34.55 + dx, 88.45),
        (28.80 + dx, 88.45), (28.80 + dx, 85.80), (16.75 + dx, 85.80),
        (16.75 + dx, 79.40), (14.45 + dx, 79.40), (14.45 + dx, 79.80),
        (10.80 + dx, 79.80),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone("VDC", ["B.Cu"], [
        (10.80 + dx, 75.80), (35.55 + dx, 75.80), (35.55 + dx, 81.20), (10.80 + dx, 81.20),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone("VDC", ["F.Cu"], [
        (42.20 + dx, 75.80), (65.55 + dx, 75.80), (65.55 + dx, 79.40),
        (65.40 + dx, 79.40), (65.40 + dx, 99.20), (58.80 + dx, 99.20),
        (58.80 + dx, 95.55), (64.55 + dx, 95.55), (64.55 + dx, 88.45),
        (58.80 + dx, 88.45), (58.80 + dx, 85.80), (46.75 + dx, 85.80),
        (46.75 + dx, 79.40), (44.45 + dx, 79.40), (44.45 + dx, 79.80),
        (42.20 + dx, 79.80),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone("VDC", ["B.Cu"], [
        (42.20 + dx, 75.80), (65.55 + dx, 75.80), (65.55 + dx, 81.20), (42.20 + dx, 81.20),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    chf_a_x = 94.30 if ch_idx == 0 else (212.40 - DX)
    add_copper_zone("VDC", ["F.Cu"], [
        (67.60 + dx, 75.80), (chf_a_x + 0.85 + dx, 75.80), (chf_a_x + 0.85 + dx, 79.80),
        (93.30 + dx, 79.80), (93.30 + dx, 79.40), (91.15 + dx, 79.40),
        (91.15 + dx, 85.80), (79.90 + dx, 85.80), (79.90 + dx, 88.45),
        (74.15 + dx, 88.45), (74.15 + dx, 95.55), (79.90 + dx, 95.55),
        (79.90 + dx, 99.20), (73.10 + dx, 99.20), (73.10 + dx, 79.40),
        (67.60 + dx, 79.40),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone("VDC", ["B.Cu"], [
        (67.60 + dx, 75.80), (chf_a_x + 0.85 + dx, 75.80), (chf_a_x + 0.85 + dx, 81.20), (67.60 + dx, 81.20),
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    leg_c_xs = [round(13.40 + 2.35 * k, 4) for k in range(10)]
    leg_b_xs = [round(43.40 + 2.35 * k, 4) for k in range(10)]
    leg_a_xs = [round(70.10 + 2.35 * k, 4) for k in range(10)]

    for cx in [11.40] + leg_c_xs:
        add_via(cx + dx, 72.95, "GND", 0.60, 0.30)
        if abs(cx - 11.40) < 0.1:
            add_via(11.40 + dx, 76.60, "VDC", 0.60, 0.30)
        elif abs(cx - 13.40) < 0.1:
            add_via(14.55 + dx, 76.60, "VDC", 0.60, 0.30)
        else:
            add_via(cx + dx, 78.25, "VDC", 0.60, 0.30)

    for cx in leg_b_xs:
        add_via(cx + dx, 72.95, "GND", 0.60, 0.30)
        if abs(cx - 43.40) < 0.1:
            add_via(44.55 + dx, 76.60, "VDC", 0.60, 0.30)
        else:
            add_via(cx + dx, 78.25, "VDC", 0.60, 0.30)

    for cx in [68.20] + leg_a_xs:
        add_via(cx + dx, 72.95, "GND", 0.60, 0.30)
        add_via(cx + dx, 78.25, "VDC", 0.60, 0.30)

    add_via(chf_a_x + dx, 77.60, "VDC", 0.60, 0.30)

# 9. Central Battery Spine VDC top-up stitch at y = 81.10 (strictly North of y = 81.60!)
for vx in [112.0, 115.5, 119.0, 122.5]:
    add_via(vx, 81.10, "VDC", 0.70, 0.35)

# 10. Reshaped Central, Right-Edge, Left-Edge, and NTC GND Pours
add_copper_zone("GND", ["F.Cu"], [
    (93.45, 80.25), (109.55, 80.25), (109.55, 128.60), (92.00, 128.60),
    (92.00, 95.30), (86.70, 95.30), (86.70, 90.55), (93.45, 90.55),
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["B.Cu"], [
    (93.45, 80.25), (109.55, 80.25), (109.55, 89.90), (93.45, 89.90),
], priority=2, clearance=0.25, min_thick=0.25, solid_pads=True)

for vx, vy in [(95.80, 80.80), (93.80, 91.20), (93.80, 93.80), (96.20, 92.50)]:
    add_via(vx, vy, "GND", 0.60, 0.30)

add_copper_zone("GND", ["F.Cu"], [
    (210.50, 15.55), (219.00, 15.55), (219.00, 129.00), (210.00, 129.00),
    (210.00, 95.30), (204.70, 95.30), (204.70, 90.55), (211.45, 90.55),
    (211.45, 80.25), (213.80, 80.25), (213.80, 75.20), (210.50, 75.20),
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["B.Cu"], [
    (210.50, 15.55), (219.00, 15.55), (219.00, 129.00), (210.20, 129.00),
    (210.20, 81.60), (213.80, 81.60), (213.80, 75.20), (210.50, 75.20),
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

for vx, vy in [(214.20, 80.80), (214.50, 68.00), (214.50, 114.00)]:
    add_via(vx, vy, "GND", 0.60, 0.30)

add_copper_zone("GND", ["F.Cu", "B.Cu"], [
    (1.00, 42.20), (8.60, 42.20), (8.60, 79.40), (6.70, 79.40),
    (6.70, 80.35), (3.40, 80.35), (3.40, 82.20), (9.20, 82.20),
    (9.20, 129.00), (1.00, 129.00),
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=False)
for vy in [68.00, 114.00]:
    add_via(4.50, vy, "GND", 0.60, 0.30)
add_via(5.30, 79.85, "GND", 0.60, 0.30)

add_copper_zone("GND", ["F.Cu", "B.Cu"], [
    (122.50, 76.60), (125.40, 76.60), (125.40, 77.85), (122.50, 77.85),
], priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(123.95, 77.15, "GND", 0.60, 0.30)

# 11. FET + Heatsink Commutation Via-Keepouts (y = [81.60 .. 97.60]) & DRC-enforced Heatsink Footprint-Keepouts
for dx in [0.0, DX]:
    add_keepout(["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"], [
        (10.80 + dx, 81.60), (92.80 + dx, 81.60), (92.80 + dx, 97.60), (10.80 + dx, 97.60),
    ], no_tracks=False, no_vias=True, no_pours=False, no_footprints=False)

add_keepout(["F.Cu"], [
    (1.00, 81.60), (219.00, 81.60), (219.00, 86.65), (1.00, 86.65),
], no_tracks=False, no_vias=False, no_pours=False, no_footprints=True)

inter_fet_gaps = [
    (9.05,  15.65),
    (23.35, 28.15),
    (35.85, 45.65),
    (53.35, 58.15),
    (65.85, 72.65),
    (80.35, 85.15),
    (92.85, 133.65),
    (141.35, 146.15),
    (153.85, 163.65),
    (171.35, 176.15),
    (183.85, 190.65),
    (198.35, 203.15),
]
for gx1, gx2 in inter_fet_gaps:
    add_keepout(["F.Cu"], [
        (gx1, 86.65), (gx2, 86.65), (gx2, 97.40), (gx1, 97.40),
    ], no_tracks=False, no_vias=False, no_pours=False, no_footprints=True)

pcbnew.SaveBoard(PCB_PATH, board)
vdc_vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == "VDC")
gnd_vias = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == "GND")
print(f"Saved staged PCB cleanly: removed_old_vias={len(vias_to_remove)}, VDC vias={vdc_vias}, GND vias={gnd_vias}")
