import os
import pcbnew

CAND = ".copperpilot/tmp/staging/v8_3_power_stage/candidate/bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_pcb"

# Rebuild clean stage-2 geometry first, then remove vias & add temporary Rule Area keepouts for FreeRouting
os.system("/usr/bin/python3 .copperpilot/tmp/staging/v8_3_power_stage/build_v8_3_stage2.py --no-vias >/dev/null 2>&1")

import pathlib, re
txt = pathlib.Path(CAND).read_text()
txt = re.sub(r"\n?\t*\(via\s+(?:\([^\(\)]*\)|[^\(\)])*\((?:\([^\(\)]*\)|[^\(\)])*\)[^\(\)]*\)", "", txt)
pathlib.Path(CAND).write_text(txt)

board = pcbnew.LoadBoard(CAND)

def add_keepout(pts, layers=("F.Cu", "B.Cu")):
    z = pcbnew.ZONE(board)
    ls = pcbnew.LSET()
    for ln in layers:
        ls.addLayer(board.GetLayerID(ln))
    z.SetLayerSet(ls)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowZoneFills(False)
    z.SetZoneName("CP_TEMP_SENSE_GUIDE")
    ol = z.Outline()
    ol.NewOutline()
    for (px, py) in pts:
        ol.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
    board.Add(z)

# 1. Block B.Cu across entire y=74..112 so SP/SN + Temp routes stay 100% on F.Cu with 0 vias!
add_keepout([(10.0, 74.0), (140.0, 74.0), (140.0, 112.5), (10.0, 112.5)], layers=("B.Cu",))

# 2. Per-motor >=1.05mm keepout around ALL SH/Gate/Power regions so SP/SN MUST use the clean coupled Kelvin corridor:
#    West corridor: x = 89.75 .. 91.10 (M0) and x = 19.75 .. 21.10 (M1)
#    North corridor: y = 76.20 .. 77.55 across x = 89.75 .. 107.60 (M0) and x = 19.75 .. 37.60 (M1)
#    DRV entry: x = 103.70 .. 107.60, y = 76.20 .. 82.25 (M0) and x = 33.70 .. 37.60, y = 76.20 .. 82.25 (M1)
#    Kelvin bay: x = 89.75 .. 96.10, y = 100.95 .. 104.95 (M0) and x = 19.75 .. 26.10, y = 100.95 .. 104.95 (M1)
for dx in [0.0, -70.0]:
    def S(pts): return [(round(x + dx, 3), round(y, 3)) for (x, y) in pts]

    # Inner block between West corridor (x<=91.10), North corridor (y<=77.55), DRV entry (x>=103.70,y<=82.25), and Kelvin bay (y>=100.95):
    add_keepout(S([
        (91.12, 77.58), (103.68, 77.58), (103.68, 82.30), (107.80, 82.30),
        (107.80, 79.80), (132.00, 79.80), (132.00, 112.00), (96.05, 112.00),
        (96.05, 100.95), (91.12, 100.95)
    ]), layers=("F.Cu",))

    # South of Kelvin bay (keep SP1/SN1 from looping south into Shunt GND):
    add_keepout(S([
        (89.50, 104.90), (96.05, 104.90), (96.05, 112.00), (89.50, 112.00)
    ]), layers=("F.Cu",))

    # Between the two shunt pads at y=98.2..100.95 (x=91.12..96.05 already covered above)
    # West outer boundary of West corridor (so SP1 doesn't wander to x=87.1 into TH1!):
    add_keepout(S([
        (89.20, 75.80), (89.72, 75.80), (89.72, 105.00), (89.20, 105.00)
    ]), layers=("F.Cu",))

    # North outer boundary of North corridor (y = 75.60..76.18) so pairs stay tightly coupled in 1.35mm band!
    add_keepout(S([
        (89.70, 75.50), (107.80, 75.50), (107.80, 76.18), (89.70, 76.18)
    ]), layers=("F.Cu",))

pcbnew.SaveBoard(CAND, board)
print("Prepared guided FreeRouting candidate.")
os._exit(0)
