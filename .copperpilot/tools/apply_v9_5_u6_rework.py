#!/usr/bin/env python3
"""
Relocate all 64 U6 (STM32F405RGTx) fanout vias to outward staggered rings further from U6
(0 vias under U6), add DRC-enforced under-U6 and under-Y1 track/via keepout rule areas,
and optimise placement + silkscreen references of the 28 components in the U6 area on a
staged candidate of bldc_motor_cntroller_v9_5.kicad_pcb.

Never creates or invents track segments; routing is performed exclusively by headless FreeRouting.

Interpreter: /usr/bin/python3 (KiCad 10.0.8 native pcbnew)
Usage: /usr/bin/python3 .copperpilot/tools/apply_v9_5_u6_rework.py <staged_candidate.kicad_pcb>
"""
import math
import sys
import pcbnew

PCB_PATH = sys.argv[1]
if ".copperpilot/tmp/staging/" not in PCB_PATH:
    raise RuntimeError(f"Refusing to run outside staging candidate: {PCB_PATH}")

board = pcbnew.LoadBoard(PCB_PATH)
board.BuildListOfNets()


def get_net(name: str):
    ni = board.FindNet(name)
    if ni is None:
        raise RuntimeError(f"Net not found: {name}")
    return ni


def assign_net(item, name: str):
    ni = get_net(name)
    item.SetNet(ni)
    if item.GetNetname() != name:
        item.SetNetCode(ni.GetNetCode())
    if item.GetNetname() != name:
        raise RuntimeError(f"Failed to assign net {name!r}: got {item.GetNetname()!r}")


# 1. Remove all previous U6 fanout vias (both under U6 and close to U6 in [98..122, 33..55])
# and unroute any tracks on M0_SO1, M0_SO2, M1_SO1, M1_SO2 before re-routing around U6
so_nets = {
    "/Microcontroller Interface/M0_SO1",
    "/Microcontroller Interface/M0_SO2",
    "/Microcontroller Interface/M1_SO1",
    "/Microcontroller Interface/M1_SO2",
}
items_to_remove = []
removed_vias = 0
removed_segs = 0
for trk in list(board.GetTracks()):
    tnet = trk.GetNetname()
    if trk.Type() == pcbnew.PCB_VIA_T:
        vx = pcbnew.ToMM(trk.GetPosition().x)
        vy = pcbnew.ToMM(trk.GetPosition().y)
        if (98.0 <= vx <= 122.0 and 33.0 <= vy <= 55.0) or (tnet in so_nets):
            items_to_remove.append(trk)
            removed_vias += 1
    elif tnet in so_nets:
        items_to_remove.append(trk)
        removed_segs += 1

for it in items_to_remove:
    board.Remove(it)

# Remove any prior U6/Y1 keepout rule areas so re-runs are idempotent
zones_to_remove = []
for z in list(board.Zones()):
    if not z.GetIsRuleArea():
        continue
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
    if 90.0 <= min_x and max_x <= 120.0 and 35.0 <= min_y and max_y <= 53.0:
        zones_to_remove.append(z)

for z in zones_to_remove:
    board.Remove(z)
removed_zones = len(zones_to_remove)


# 2. Optimise placement & silkscreen refdes of components around U6 (110.0, 44.0)
# Format: (ref, x, y, rot_deg, ref_dx, ref_dy, ref_angle)
POSES = [
    # West of U6 (clear of West R2 fanout vias at x = 99.30 mm)
    ("C85", 96.40, 38.30, 180.0, 0.00, -0.95, 0.0),
    ("Y1",  96.80, 41.70, -90.0, 0.00, -2.45, 0.0),
    ("C83", 93.60, 40.50,   0.0, 0.00, -1.05, 0.0),
    ("C84", 93.60, 42.90,   0.0, 0.00,  0.95, 0.0),
    ("C86", 96.40, 44.70, 180.0,  1.45, 0.00, 0.0),
    ("C92", 96.40, 47.10, 180.0, -1.85, 0.00, 0.0),
    ("C93", 96.40, 48.90, 180.0, -1.85, 0.00, 0.0),
    # Current-sense ADC RC filter caps & testpoints (ordered matching U6 pins 8, 9, 10, 11)
    ("C6",   90.20, 43.40,  0.0, 0.00, -1.05, 0.0),
    ("C7",   90.20, 45.20,  0.0, 0.00, -1.05, 0.0),
    ("C28",  90.20, 47.00,  0.0, 0.00, -1.05, 0.0),
    ("C27",  90.20, 48.80,  0.0, 0.00,  1.05, 0.0),
    ("TP8",  85.80, 42.60,  0.0, -2.75, 0.00, 0.0),
    ("TP9",  85.80, 45.00,  0.0, -2.75, 0.00, 0.0),
    ("TP11", 85.80, 47.40,  0.0, -2.75, 0.00, 0.0),
    ("TP10", 85.80, 49.80,  0.0, -2.75, 0.00, 0.0),
    # North of U6 (clear of North R2 fanout vias at y = 33.30 mm)
    ("C89", 104.30, 30.80, 90.0, -1.15, 0.00, 0.0),
    ("TP6", 111.90, 30.50,  0.0,  0.00, -1.55, 0.0),
    # South of U6 (clear of South R2 fanout vias at y = 54.20 mm and D2/Q13 at y >= 59.65 mm)
    ("C82", 105.82, 56.50, -90.0, -1.15, 0.00, 0.0),
    ("C43", 108.40, 56.50, -90.0,  1.15, 0.00, 0.0),
    ("C88", 114.20, 56.50, -90.0, -1.15, 0.00, 0.0),
    ("C87", 116.80, 56.50, -90.0,  1.15, 0.00, 0.0),
    # East of U6 (clear of East R2 fanout vias at x = 120.70 mm)
    ("C91",  123.60, 37.40,  0.0, 0.00, -0.95, 0.0),
    ("C90",  123.60, 39.20,  0.0, 0.00,  0.95, 0.0),
    ("D3",   122.60, 52.80,  0.0, 0.00, -0.95, 0.0),
    ("R50",  122.60, 54.60,  0.0, 0.00,  0.95, 0.0),
    ("TP2",  125.60, 50.50,  0.0, 0.00, -1.45, 0.0),
    ("TP3",  125.60, 53.20,  0.0, 0.00, -1.45, 0.0),
    ("TP12", 125.60, 55.90,  0.0, 0.00,  1.45, 0.0),
]

for ref, x, y, rot, rdx, rdy, rang in POSES:
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise RuntimeError(f"Footprint not found: {ref}")
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    fp.SetOrientationDegrees(rot)
    rtxt = fp.Reference()
    rtxt.SetTextAngleDegrees(rang)
    rtxt.SetPosition(pcbnew.VECTOR2I_MM(round(x + rdx, 4), round(y + rdy, 4)))

# Also fix C63 silk_over_copper in the adjacent LDO bank
fp_c63 = board.FindFootprintByReference("C63")
if fp_c63 is not None:
    p63 = fp_c63.GetPosition()
    fp_c63.Reference().SetTextAngleDegrees(0.0)
    fp_c63.Reference().SetPosition(pcbnew.VECTOR2I_MM(round(pcbnew.ToMM(p63.x) - 1.25, 4), round(pcbnew.ToMM(p63.y), 4)))


# 3. Add under-U6 and under-Y1 keepout rule areas
def add_keepout(layers, pts, no_tracks=True, no_vias=True):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(no_tracks)
    z.SetDoNotAllowVias(no_vias)
    z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    lset = pcbnew.LSET()
    for lname in layers:
        lset.AddLayer(board.GetLayerID(lname))
    z.SetLayerSet(lset)
    outline = z.Outline()
    outline.NewOutline()
    for px, py in pts:
        outline.Append(pcbnew.FromMM(round(px, 4)), pcbnew.FromMM(round(py, 4)))
    board.Add(z)
    return z


# Under U6 F.Cu interior (0.25 mm inside inner pad edges [105.10..114.90, 39.10..48.90])
for nt, nv in ((True, False), (False, True)):
    add_keepout(
        ["F.Cu"],
        [(105.35, 39.35), (114.65, 39.35), (114.65, 48.65), (105.35, 48.65)],
        no_tracks=nt,
        no_vias=nv,
    )
# Under full U6 courtyard on B.Cu / In1.Cu / In2.Cu (zero bottom/inner tracks & zero vias under U6)
for nt, nv in ((True, False), (False, True)):
    add_keepout(
        ["B.Cu", "In1.Cu", "In2.Cu"],
        [(103.30, 37.30), (116.70, 37.30), (116.70, 50.70), (103.30, 50.70)],
        no_tracks=nt,
        no_vias=nv,
    )
# Under Y1 + C83/C84 oscillator block on B.Cu (prevent other signals crossing under crystal)
for nt, nv in ((True, False), (False, True)):
    add_keepout(
        ["B.Cu"],
        [(92.90, 39.75), (98.20, 39.75), (98.20, 43.65), (92.90, 43.65)],
        no_tracks=nt,
        no_vias=nv,
    )


# 4. Place all 64 outward staggered fanout vias (0.60 mm / 0.30 mm) around U6
u6_fp = board.FindFootprintByReference("U6")
pad_by_num = {str(p.GetNumber()): p for p in u6_fp.Pads()}

fanout_specs = []
# West: pins 1..16
for k in range(16):
    pin = 1 + k
    xv = 100.80 if (k % 2 == 0) else 99.30
    yv = round(44.00 + (k - 7.5) * 0.76, 3)
    fanout_specs.append((pin, xv, yv))

# South: pins 17..32
for k in range(16):
    pin = 17 + k
    xv = round(110.00 + (k - 7.5) * 0.76, 3)
    yv = 52.80 if (k % 2 == 0) else 54.20
    fanout_specs.append((pin, xv, yv))

# East: pins 33..48 (coupled symmetric differential pair on 44=USB_DN & 45=USB_DP)
for k in range(16):
    pin = 33 + k
    if pin <= 43:
        xv = 119.20 if (k % 2 == 0) else 120.70
        yv = round(50.00 - k * 0.76, 3)
    elif pin == 44:
        xv, yv = 120.20, 41.30
    elif pin == 45:
        xv, yv = 120.20, 40.25
    elif pin == 46:
        xv, yv = 120.70, 38.90
    elif pin == 47:
        xv, yv = 119.20, 38.90
    elif pin == 48:
        xv, yv = 120.70, 37.40
    fanout_specs.append((pin, xv, yv))

# North: pins 49..64
for k in range(16):
    pin = 49 + k
    xv = round(110.00 + (7.5 - k) * 0.76, 3)
    yv = 34.80 if (k % 2 == 0) else 33.30
    fanout_specs.append((pin, xv, yv))

placed_vias = []
for pin, vx, vy in fanout_specs:
    pad = pad_by_num[str(pin)]
    net_name = pad.GetNetname()
    if not net_name:
        raise RuntimeError(f"U6 pad {pin} has empty net!")
    if 103.30 <= vx <= 116.70 and 37.30 <= vy <= 50.70:
        raise RuntimeError(f"Via for pin {pin} inside U6 courtyard: {(vx, vy)}")
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(vx, vy))
    v.SetWidth(pcbnew.FromMM(0.60))
    v.SetDrill(pcbnew.FromMM(0.30))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(board.GetLayerID("F.Cu"), board.GetLayerID("B.Cu"))
    v.SetIsFree(True)
    board.Add(v)
    assign_net(v, net_name)
    px, py = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
    placed_vias.append((pin, net_name, px, py, vx, vy, round(math.hypot(vx - px, vy - py), 2)))

pcbnew.SaveBoard(PCB_PATH, board)
print(
    f"Removed {removed_vias} old vias, {removed_segs} SO segments, {removed_zones} old keepouts; "
    f"optimised {len(POSES)} components; placed {len(placed_vias)} outward U6 vias "
    f"(dist range {min(x[6] for x in placed_vias):.2f}..{max(x[6] for x in placed_vias):.2f} mm)."
)
sys.stdout.flush()
import os
os._exit(0)
