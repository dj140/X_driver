#!/usr/bin/env python3
import sys
from pathlib import Path

p = Path(sys.argv[1])
txt = p.read_text()
if "(stackup" not in txt:
    stackup_block = """\t(setup
\t\t(stackup
\t\t\t(layer "F.SilkS"
\t\t\t\t(type "Top Silk Screen")
\t\t\t)
\t\t\t(layer "F.Paste"
\t\t\t\t(type "Top Solder Paste")
\t\t\t)
\t\t\t(layer "F.Mask"
\t\t\t\t(type "Top Solder Mask")
\t\t\t\t(thickness 0.0152)
\t\t\t)
\t\t\t(layer "F.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.07)
\t\t\t)
\t\t\t(layer "dielectric 1"
\t\t\t\t(type "prepreg")
\t\t\t\t(thickness 0.11)
\t\t\t\t(material "FR4 3313")
\t\t\t\t(epsilon_r 4.1)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In1.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 2"
\t\t\t\t(type "core")
\t\t\t\t(thickness 1.17)
\t\t\t\t(material "FR4")
\t\t\t\t(epsilon_r 4.6)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In2.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 3"
\t\t\t\t(type "prepreg")
\t\t\t\t(thickness 0.11)
\t\t\t\t(material "FR4 3313")
\t\t\t\t(epsilon_r 4.1)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "B.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.07)
\t\t\t)
\t\t\t(layer "B.Mask"
\t\t\t\t(type "Bottom Solder Mask")
\t\t\t\t(thickness 0.0152)
\t\t\t)
\t\t\t(layer "B.Paste"
\t\t\t\t(type "Bottom Solder Paste")
\t\t\t)
\t\t\t(layer "B.SilkS"
\t\t\t\t(type "Bottom Silk Screen")
\t\t\t)
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints yes)
\t\t)"""
    idx = txt.find("(setup")
    assert idx != -1
    # preserve indentation before (setup
    line_start = txt.rfind("\n", 0, idx) + 1
    indent = txt[line_start:idx]
    txt = txt[:line_start] + stackup_block + txt[idx + len("(setup"):]
    p.write_text(txt)
print("Verified (stackup ...) present:", "(stackup" in p.read_text())
