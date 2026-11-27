#!/usr/bin/env python3
"""
Unit B: High-width F.Cu/B.Cu/In1.Cu/In2.Cu power pours, capacitor/trunk stitching vias,
and pour-protecting keepout zones for bldc_motor_cntroller_v9.2 (220.0 x 115.0 mm).
"""
import sys
import uuid
import pcbnew

PCB_PATH = sys.argv[1]
board = pcbnew.LoadBoard(PCB_PATH)

DX = 118.0  # Exact channel symmetry M0 = M1 + 118.0 mm

# Nudge R47 0.4mm West (107.6, 64.4) so F.Cu HS pour has a clean 1.0mm West bridge from U3.6/C52.2 to Q13.1-3
fp_r47 = board.FindFootprintByReference("R47")
if fp_r47:
    fp_r47.SetPosition(pcbnew.VECTOR2I_MM(107.60, 64.40))
for ref_nudge, nx, ny in [("C_HF4", 94.40, 89.50), ("C_HF1", 94.40+DX, 89.50), ("R25", 92.55, 84.60), ("R2", 92.55+DX, 84.60), ("R33", 37.55, 84.60), ("R13", 37.55+DX, 84.60), ("R29", 49.85, 84.60), ("R9", 49.85+DX, 84.60)]:
    fp_n = board.FindFootprintByReference(ref_nudge)
    if fp_n:
        fp_n.SetPosition(pcbnew.VECTOR2I_MM(nx, ny))

net_map = {n: code for n, code in board.GetNetcodeFromNetnameMap().items()} if hasattr(board, "GetNetcodeFromNetnameMap") else {}
def get_net(name):
    ni = board.FindNet(name)
    if ni is None:
        raise RuntimeError(f"Net not found: {name}")
    return ni

def add_copper_zone(net_name, layers, pts, priority=1, clearance=0.20, min_thick=0.25, solid_pads=False):
    z = pcbnew.ZONE(board)
    z.SetNet(get_net(net_name))
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
        outline.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(z)
    return z

def add_keepout(layers, pts, no_tracks=True, no_vias=False, no_pours=False):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(no_tracks)
    z.SetDoNotAllowVias(no_vias)
    z.SetDoNotAllowZoneFills(no_pours)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    lset = pcbnew.LSET()
    for l in layers:
        lset.AddLayer(board.GetLayerID(l))
    z.SetLayerSet(lset)
    outline = z.Outline()
    outline.NewOutline()
    for x, y in pts:
        outline.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(z)
    return z

def add_via(x, y, net_name, size=0.60, drill=0.30):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    v.SetWidth(pcbnew.FromMM(size))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(board.GetLayerID("F.Cu"), board.GetLayerID("B.Cu"))
    v.SetNet(get_net(net_name))
    board.Add(v)
    return v

# ==============================================================================
# 1. INNER PLANES: In1.Cu (Solid GND) & In2.Cu (+3.3V Digital / VDC Power)
# ==============================================================================
add_copper_zone("GND", ["In1.Cu"], [(1.0, 16.0), (219.0, 16.0), (219.0, 129.0), (1.0, 129.0)],
                priority=0, clearance=0.20, min_thick=0.25, solid_pads=False)

# In2.Cu +3.3V covers upper digital + U1/U2 North pullup rows (y=16.0..62.4), stepping around brake chopper VDC (x=111..124, y>=59.5)
add_copper_zone("+3.3V", ["In2.Cu"], [
    (1.0, 16.0), (219.0, 16.0), (219.0, 62.4),
    (124.5, 62.4), (124.5, 59.2), (110.5, 59.2), (110.5, 62.4),
    (1.0, 62.4)
], priority=0, clearance=0.25, min_thick=0.25, solid_pads=False)

# In2.Cu VDC covers lower power stage + brake chopper Q13/C48/C_AUX1
add_copper_zone("VDC", ["In2.Cu"], [
    (1.0, 63.2), (111.2, 63.2), (111.2, 60.0), (123.8, 60.0), (123.8, 63.2),
    (219.0, 63.2), (219.0, 129.0), (1.0, 129.0)
], priority=0, clearance=0.25, min_thick=0.25, solid_pads=False)

# ==============================================================================
# 2. SYMMETRIC POWER STAGE POURS (M1 dx=0, M0 dx=+118.0)
# ==============================================================================
for ch_idx, dx in enumerate([0.0, DX]):
    ns = "/Motor_Driver2" if ch_idx == 0 else "/Motor Driver"

    # --- SL_C (Q12/Q6 Source -> R36/R16.2): 7.35 mm trunk + 5.10 mm Source tongue ---
    add_copper_zone(f"{ns}/SL_C", ["F.Cu"], [
        (10.80+dx, 89.85), (17.30+dx, 89.85), (17.30+dx, 90.45),
        (23.60+dx, 90.45), (23.60+dx, 95.30), (18.15+dx, 95.30),
        (18.15+dx, 103.50), (10.80+dx, 103.50)
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone(f"{ns}/SL_C", ["B.Cu"], [
        (10.80+dx, 98.00), (18.15+dx, 98.00), (18.15+dx, 103.50), (10.80+dx, 103.50)
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    # SL_C stitching vias (strictly South of y=97.6!)
    for vx in [11.80, 13.60, 15.40, 17.20]:
        for vy in [98.55, 99.65]:
            add_via(vx+dx, vy, f"{ns}/SL_C", 0.60, 0.30)

    # --- SL_B (Q10/Q4 Source -> R32/R12.2): 7.00 mm trunk + 5.10 mm Source tongue ---
    add_copper_zone(f"{ns}/SL_B", ["F.Cu"], [
        (43.15+dx, 89.85), (49.25+dx, 89.85), (49.25+dx, 90.45),
        (55.60+dx, 90.45), (55.60+dx, 95.30), (50.15+dx, 95.30),
        (50.15+dx, 103.50), (43.15+dx, 103.50)
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    add_copper_zone(f"{ns}/SL_B", ["B.Cu"], [
        (43.15+dx, 98.00), (50.15+dx, 98.00), (50.15+dx, 103.50), (43.15+dx, 103.50)
    ], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

    for vx in [44.10, 45.85, 47.65, 49.40]:
        for vy in [98.55, 99.65]:
            add_via(vx+dx, vy, f"{ns}/SL_B", 0.60, 0.30)

    # --- SH_C (Q12/Q6 Drain + Q11/Q5 Source -> J2.3 / J1.3 at 51.5+dx, 123.0): 7.48 -> 12.70 mm wide! ---
    sh_c_fcu = [
        (18.40+dx, 86.45), (31.15+dx, 86.45),
        (31.15+dx, 90.50), (36.60+dx, 90.50), (36.60+dx, 95.30), (31.15+dx, 95.30),
        (31.15+dx, 105.50), (50.00+dx, 115.20), (54.15+dx, 119.50),
        (54.15+dx, 126.40), (45.00+dx, 126.40), (18.45+dx, 111.50),
        (18.45+dx, 95.60), (23.90+dx, 95.60), (23.90+dx, 88.45), (18.40+dx, 88.45)
    ]
    add_copper_zone(f"{ns}/SH_C", ["F.Cu"], sh_c_fcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    sh_c_bcu = [
        (18.45+dx, 86.45), (31.15+dx, 86.45),
        (31.15+dx, 105.50), (50.00+dx, 115.20), (54.15+dx, 119.50),
        (54.15+dx, 126.40), (45.00+dx, 126.40), (18.45+dx, 111.50)
    ]
    add_copper_zone(f"{ns}/SH_C", ["B.Cu"], sh_c_bcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    for vx in [19.8, 22.5, 25.2, 27.9, 30.2]:
        for vy in [98.55, 102.50, 107.00]:
            add_via(vx+dx, vy, f"{ns}/SH_C", 0.60, 0.30)

    # --- SH_B (Q10/Q4 Drain + Q9/Q3 Source -> J2.2 / J1.2 at 57.0+dx, 123.0): 7.48 -> 12.70 mm wide! ---
    sh_b_fcu = [
        (50.40+dx, 86.45), (63.15+dx, 86.45),
        (63.15+dx, 90.50), (68.60+dx, 90.50), (68.60+dx, 95.30), (63.15+dx, 95.30),
        (63.15+dx, 114.80), (59.65+dx, 119.50), (59.65+dx, 124.20),
        (54.35+dx, 124.20), (54.35+dx, 119.50), (50.65+dx, 114.80),
        (50.65+dx, 95.60), (55.90+dx, 95.60), (55.90+dx, 88.45), (50.40+dx, 88.45)
    ]
    add_copper_zone(f"{ns}/SH_B", ["F.Cu"], sh_b_fcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    sh_b_bcu = [
        (50.65+dx, 86.45), (63.15+dx, 86.45),
        (63.15+dx, 114.80), (59.65+dx, 119.50), (59.65+dx, 124.20),
        (54.35+dx, 124.20), (54.35+dx, 119.50), (50.65+dx, 114.80)
    ]
    add_copper_zone(f"{ns}/SH_B", ["B.Cu"], sh_b_bcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    for vx in [52.0, 54.6, 57.0, 59.4, 61.8]:
        for vy in [98.55, 103.00, 108.50, 113.50]:
            add_via(vx+dx, vy, f"{ns}/SH_B", 0.60, 0.30)

    # --- SH_A (Q7/Q1 Source + Q8/Q2 Drain -> J2.1 / J1.1 at 62.5+dx, 123.0): 7.48 -> 12.25 mm wide! ---
    sh_a_fcu = [
        (79.25+dx, 86.45), (92.00+dx, 86.45),
        (92.00+dx, 88.45), (86.50+dx, 88.45), (86.50+dx, 95.60),
        (91.50+dx, 95.60), (91.50+dx, 111.50), (69.00+dx, 126.40),
        (59.85+dx, 126.40), (59.85+dx, 119.50), (64.00+dx, 115.20),
        (79.25+dx, 105.50), (79.25+dx, 95.30), (73.80+dx, 95.30),
        (73.80+dx, 90.50), (79.25+dx, 90.50)
    ]
    add_copper_zone(f"{ns}/SH_A", ["F.Cu"], sh_a_fcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    sh_a_bcu = [
        (79.25+dx, 86.45), (91.50+dx, 86.45),
        (91.50+dx, 111.50), (69.00+dx, 126.40),
        (59.85+dx, 126.40), (59.85+dx, 119.50), (64.00+dx, 115.20),
        (79.25+dx, 105.50)
    ]
    add_copper_zone(f"{ns}/SH_A", ["B.Cu"], sh_a_bcu, priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)

    for vx in [80.6, 83.2, 85.8, 88.4, 90.4]:
        for vy in [98.55, 102.50, 107.00]:
            add_via(vx+dx, vy, f"{ns}/SH_A", 0.60, 0.30)

    # --- F.Cu Fast Commutation VDC Bus (priority 3; automatically clears higher-priority SH/SL and gate resistors!) ---
    # Wait: let's shape VDC cleanly so it connects:
    #   1) North 1206 capacitor row (y=80.8..85.8 across x=10.8..95.5, notched around U2/U1 South fanout x=48.0..63.0 at y<83.5? Wait: at y=80.8..83.5, x=48.0..63.0 is South of U2/U1 where GL/GH/SH/SL fan out to R_gates!)
    #   YES! Leaving x=48.0..63.2 OPEN above y=85.8 lets ALL 6 gate/sense traces fan out on F.Cu without cutting VDC!
    #   Let's check: West VDC bus covers C78..C55 (x=10.8..47.8, y=80.8..85.8) + C_HF6.1 (x=13.5..15.5, y=85.8..89.3) + Q11 North Drain (31.4..37.0, y=85.8..88.5) + Q11 East VDC strap (38.15..41.35, y=80.8..97.4) + Q11 South Drain (31.4..41.35, y=95.6..99.2) + C_HF5.1 (45.8..47.8, y=85.8..89.3)!
    add_copper_zone("VDC", ["F.Cu"], [
        (10.80+dx, 80.30), (47.80+dx, 80.30), (47.80+dx, 89.35), (45.70+dx, 89.35),
        (45.70+dx, 85.80), (41.35+dx, 85.80), (41.35+dx, 99.20), (31.40+dx, 99.20),
        (31.40+dx, 95.55), (38.30+dx, 95.55), (38.30+dx, 83.60), (36.95+dx, 83.60),
        (36.95+dx, 88.45), (31.40+dx, 88.45), (31.40+dx, 85.80), (18.80+dx, 85.80),
        (18.80+dx, 83.60), (17.00+dx, 83.60), (17.00+dx, 89.35), (13.40+dx, 89.35),
        (13.40+dx, 85.80), (10.80+dx, 85.80)
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    #   East VDC bus covers C57..C79 (x=63.6..95.6, y=80.3..85.8) + Q9 North Drain (63.4..69.0, y=85.8..88.45) + shared Q9-Q7 VDC pillar (70.15..72.25 at y=83.6..90.2, widening to 68.85..73.55 at y=90.2..95.55, and 63.4..79.0 at y=95.55..99.2!) + Q7 North Drain (73.4..79.0, y=85.8..88.45) + C_HF4.1 (93.2..95.5, y=85.8..89.35)!
    add_copper_zone("VDC", ["F.Cu"], [
        (63.40+dx, 80.30), (81.20+dx, 80.30), (81.20+dx, 83.40), (95.50+dx, 83.40),
        (95.50+dx, 89.35), (93.40+dx, 89.35), (93.15+dx, 85.80),
        (79.00+dx, 85.80), (79.00+dx, 88.45), (73.55+dx, 88.45), (73.55+dx, 83.60),
        (72.25+dx, 83.60), (72.25+dx, 90.25), (73.55+dx, 90.25), (73.55+dx, 95.55),
        (79.00+dx, 95.55), (79.00+dx, 99.20), (63.40+dx, 99.20), (63.40+dx, 95.55),
        (68.85+dx, 95.55), (68.85+dx, 90.25), (70.15+dx, 90.25), (70.15+dx, 83.60),
        (68.85+dx, 83.60), (68.85+dx, 88.45), (63.40+dx, 88.45)
    ], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    # B.Cu VDC strips under 1206 cap rows & South HS Drain bridges (for DC sharing with In2.Cu VDC)
    add_copper_zone("VDC", ["B.Cu"], [(10.80+dx, 80.30), (47.80+dx, 80.30), (47.80+dx, 83.60), (10.80+dx, 83.60)],
                    priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)
    add_copper_zone("VDC", ["B.Cu"], [(63.40+dx, 80.30), (81.20+dx, 80.30), (81.20+dx, 83.60), (63.40+dx, 83.60)],
                    priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)
    add_copper_zone("VDC", ["B.Cu"], [(31.40+dx, 98.00), (41.35+dx, 98.00), (41.35+dx, 99.30), (31.40+dx, 99.30)],
                    priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)
    add_copper_zone("VDC", ["B.Cu"], [(63.40+dx, 98.00), (79.00+dx, 98.00), (79.00+dx, 99.30), (63.40+dx, 99.30)],
                    priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

    # Stitch EVERY SINGLE 1206 & 0402 VDC bus capacitor on both channels (VDC vias at y=82.8 -> In2.Cu/B.Cu, GND vias at y=78.0 -> In1.Cu)!
    cap_xs = [11.30, 13.30, 15.70, 20.20, 22.70, 25.20, 27.70, 30.20, 32.70, 35.20, 44.60, 47.00, 64.50, 67.00, 75.50, 78.00, 80.20]
    for cx in cap_xs:
        add_via(cx+dx, 82.85, "VDC", 0.60, 0.30)
        add_via(cx+dx, 78.00, "GND", 0.60, 0.30)

    # Also stitch South HS Drain VDC islands at y=98.55 (strictly South of y=97.6!)
    for vx in [32.6, 35.4, 38.2, 40.4, 64.8, 67.8, 71.2, 74.6, 77.6]:
        add_via(vx+dx, 98.55, "VDC", 0.60, 0.30)

    # North GND strip on F.Cu bonding all 17 capacitor GND pads + vias together (priority 3)
    add_copper_zone("GND", ["F.Cu"], [(10.60+dx, 77.20), (47.80+dx, 77.20), (47.80+dx, 79.90), (10.60+dx, 79.90)],
                    priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
    add_copper_zone("GND", ["F.Cu"], [(63.60+dx, 77.20), (81.00+dx, 77.20), (81.00+dx, 79.90), (63.60+dx, 79.90)],
                    priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)

    # Shunt GND return pads (R36.1 / R16.1 at 14.5+dx, 107.4 and R32.1 / R12.1 at 46.75+dx, 107.4):
    add_copper_zone("GND", ["F.Cu", "B.Cu"], [(10.80+dx, 105.60), (18.10+dx, 105.60), (18.10+dx, 113.50), (10.80+dx, 113.50)],
                    priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)
    for vx in [12.0, 13.7, 15.4, 17.1]:
        for vy in [109.80, 111.80]:
            add_via(vx+dx, vy, "GND", 0.60, 0.30)

    add_copper_zone("GND", ["F.Cu", "B.Cu"], [(43.15+dx, 105.60), (50.15+dx, 105.60), (50.15+dx, 114.20), (43.15+dx, 114.20)],
                    priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)
    for vx in [44.2, 45.9, 47.6, 49.3]:
        for vy in [109.80, 112.00]:
            add_via(vx+dx, vy, "GND", 0.60, 0.30)

# ==============================================================================
# 3. CENTRAL BATTERY SPINE (J3 XT90: GND=104.55, VDC=115.45) & EDGE GND SPINES
# ==============================================================================
# Central GND spine (connects Q8.3 GND Source + C_HF4.2 straight down into J3.1 GND!)
add_copper_zone("GND", ["F.Cu"], [
    (86.90, 90.45), (93.20, 90.45), (93.20, 89.85), (109.55, 89.85),
    (109.55, 128.60), (92.20, 128.60), (92.20, 95.30), (86.90, 95.30)
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["B.Cu"], [
    (92.20, 89.85), (109.55, 89.85), (109.55, 128.60), (92.20, 128.60)
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

# Q8.3 + C_HF4.2 direct commutation return GND vias (bonding F.Cu GND 0.11mm down to In1.Cu GND!)
for vx, vy in [(93.2, 91.2), (93.2, 93.8), (95.5, 91.2), (95.5, 93.8), (98.0, 95.0), (98.0, 105.0), (104.5, 112.0), (98.0, 118.0)]:
    add_via(vx, vy, "GND", 0.60, 0.30)

# Right-Edge GND spine (connects Q2.3 GND Source + C_HF1.2 + H8/H3/H4/H10!)
add_copper_zone("GND", ["F.Cu"], [
    (86.90+DX, 90.45), (93.20+DX, 90.45), (93.20+DX, 89.85), (210.50, 89.85),
    (210.50, 16.00), (219.00, 16.00), (219.00, 129.00), (92.20+DX, 129.00),
    (92.20+DX, 95.30), (86.90+DX, 95.30)
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["B.Cu"], [
    (92.20+DX, 89.85), (210.50, 89.85), (210.50, 16.00),
    (219.00, 16.00), (219.00, 129.00), (92.20+DX, 129.00)
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

for vx, vy in [(93.2+DX, 91.2), (93.2+DX, 93.8), (95.5+DX, 91.2), (95.5+DX, 93.8), (214.5, 50.0), (214.5, 68.0), (214.5, 114.0)]:
    add_via(vx, vy, "GND", 0.60, 0.30)

# Left-Edge GND spine (H7, H1, H2, H9; notched around J4 USB-C cutout y=30..42)
add_copper_zone("GND", ["F.Cu", "B.Cu"], [(1.00, 16.00), (8.60, 16.00), (8.60, 29.80), (1.00, 29.80)],
                priority=3, clearance=0.25, min_thick=0.25, solid_pads=False)
add_copper_zone("GND", ["F.Cu", "B.Cu"], [(1.00, 42.20), (8.60, 42.20), (8.60, 86.80), (6.80, 86.80), (6.80, 129.00), (1.00, 129.00)],
                priority=3, clearance=0.25, min_thick=0.25, solid_pads=False)
for vy in [26.0, 52.0, 68.0, 114.0]:
    add_via(4.50, vy, "GND", 0.60, 0.30)

# Central VDC Battery Input Spine (J3.2 at 115.45, 123.0 -> In2.Cu/F.Cu/B.Cu VDC!)
add_copper_zone("VDC", ["F.Cu", "B.Cu"], [
    (110.30, 80.50), (124.20, 80.50), (124.20, 128.60), (110.30, 128.60)
], priority=3, clearance=0.25, min_thick=0.25, solid_pads=True)

for vx in [112.0, 115.5, 119.0, 122.5]:
    for vy in [83.0, 92.0, 102.0, 112.0, 127.0]:
        add_via(vx, vy, "VDC", 0.70, 0.35)

# ==============================================================================
# 4. BRAKE CHOPPER (U3 / Q13 / Q14 / H5 / H6) UNIFIED POURS
# ==============================================================================
# Q13.5 (114.55, 62.5) + C48.1 (119.5, 63.9) + C_AUX1.1 (122.2, 63.28):
add_copper_zone("VDC", ["F.Cu"], [
    (112.10, 60.20), (123.50, 60.20), (123.50, 64.80), (112.10, 64.80)
], priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)
for vx in [114.5, 117.0, 119.5, 122.2]:
    add_via(vx, 64.20, "VDC", 0.60, 0.30)
# R45.1 (98.68, 69.5) VDC via straight to In2.Cu VDC!
add_via(99.60, 69.50, "VDC", 0.60, 0.30)

# UNIFIED SINGLE-POLYGON /Power Management/HS pour on F.Cu & B.Cu!
# Connects U3.6 (104.9, 66.4) + C52.2 (106.8, 61.68) + Q13.1-3 (110.6, 60.6..63.1) + Q14.5 (114.55, 69.5) + H6 (121.0, 68.4)
# Passing West of R47 (107.6, 64.4) along x=[105.7..106.55] and East between Q13/Q14 along y=[65.25..66.95]!
add_copper_zone("/Power Management/HS", ["F.Cu"], [
    (104.60, 66.05), (105.75, 66.05), (105.75, 61.35), (111.20, 61.35),
    (111.20, 60.25), (111.55, 60.25), (111.55, 63.55), (106.55, 63.55),
    (106.55, 65.25), (123.20, 65.25), (123.20, 70.60), (116.85, 70.60),
    (116.85, 71.75), (112.15, 71.75), (112.15, 66.85), (104.60, 66.85)
], priority=5, clearance=0.22, min_thick=0.22, solid_pads=True)

add_copper_zone("/Power Management/HS", ["B.Cu"], [
    (105.75, 61.35), (111.55, 61.35), (111.55, 65.25), (123.20, 65.25),
    (123.20, 71.75), (112.15, 71.75), (112.15, 66.85), (105.75, 66.85)
], priority=5, clearance=0.25, min_thick=0.25, solid_pads=True)

for vx, vy in [(106.2, 62.5), (109.5, 62.5), (109.5, 66.0), (114.5, 66.0), (118.0, 68.4)]:
    add_via(vx, vy, "/Power Management/HS", 0.60, 0.30)

# Brake Chopper GND pour (Q14.1-3 at 110.6, 67.6..70.1 + H5 at 121.0, 73.2):
add_copper_zone("GND", ["F.Cu"], [
    (109.50, 67.20), (111.30, 67.20), (111.30, 70.50), (109.50, 70.50)
], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(109.90, 68.85, "GND", 0.60, 0.30)

add_copper_zone("GND", ["F.Cu", "B.Cu"], [
    (117.50, 71.95), (123.50, 71.95), (123.50, 74.80), (117.50, 74.80)
], priority=4, clearance=0.25, min_thick=0.25, solid_pads=True)
for vx in [118.5, 123.0]:
    add_via(vx, 73.20, "GND", 0.60, 0.30)

# ==============================================================================
# 5. DEDICATED DECOUPLING / BUCK / DRIVER LOCAL VIA STITCHING (NO DANGLING VIAS!)
# ==============================================================================
# U2 (55.0, 68.5) & U1 (173.0, 68.5) PVDD1 (pin 29, 53, 54) local VDC padlets + vias:
add_copper_zone("VDC", ["F.Cu"], [(46.20, 73.00), (47.40, 73.00), (47.40, 74.50), (46.20, 74.50)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(46.80, 74.05, "VDC", 0.60, 0.30)
add_copper_zone("VDC", ["F.Cu"], [(164.20, 73.00), (165.40, 73.00), (165.40, 74.50), (164.20, 74.50)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(164.80, 74.05, "VDC", 0.60, 0.30)
add_copper_zone("VDC", ["F.Cu"], [(179.45, 74.85), (180.25, 74.85), (180.25, 76.60), (179.45, 76.60)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(179.85, 76.25, "VDC", 0.60, 0.30)
# R45.1 (98.68, 69.50) VDC padlet + via:
add_copper_zone("VDC", ["F.Cu"], [(98.45, 69.00), (100.10, 69.00), (100.10, 70.00), (98.45, 70.00)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)

# U4 LDO +3.3V output padlet + via (energizes In2.Cu +3.3V plane cleanly!):
add_copper_zone("+3.3V", ["F.Cu"], [(128.00, 46.10), (131.40, 46.10), (131.40, 49.60), (129.00, 49.60), (129.00, 50.60), (128.00, 50.60)], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(129.80, 47.40, "+3.3V", 0.60, 0.30)

# U1 Buck output +5V & GND local pours:
add_copper_zone("+5V", ["F.Cu"], [
    (192.00, 67.40), (202.40, 67.40), (202.40, 69.25), (195.20, 69.25),
    (195.20, 70.30), (192.00, 70.30)
], priority=4, clearance=0.20, min_thick=0.25, solid_pads=True)

add_copper_zone("GND", ["F.Cu"], [
    (184.20, 73.30), (186.20, 73.30), (186.20, 70.40), (202.40, 70.40),
    (202.40, 74.80), (184.20, 74.80)
], priority=3, clearance=0.20, min_thick=0.25, solid_pads=True)
add_via(185.0, 74.10, "GND", 0.60, 0.30)
for vx in [196.2, 198.6, 201.4]:
    add_via(vx, 72.20, "GND", 0.60, 0.30)

# ==============================================================================
# 6. KEEPOUT RULE AREAS TO PROTECT SOLID In1.Cu GND & FULL PHASE/SHUNT WIDTHS
# ==============================================================================
for dx in [0.0, DX]:
    # 6A. Prevent FreeRouting from placing ANY via inside the FET commutation strip y=[85.8..97.6]
    # (Ends at x=92.4+dx so our intentional Q8/Q2 East GND return vias at x=93.2..95.5+dx are outside!)
    add_keepout(["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"], [
        (10.80+dx, 85.80), (92.40+dx, 85.80), (92.40+dx, 97.60), (10.80+dx, 97.60)
    ], no_tracks=False, no_vias=True, no_pours=False)

    # 6B. Prevent FreeRouting signal traces from slicing across SL_C, SL_B, SH_C, SH_B, SH_A trunks!
    # Leave y <= 88.6 open on SH_C/SH_B/SH_A North Drain tips and y=90.3..91.5 tip on SL_C/SL_B so U1/U2 sense taps can connect cleanly at the top edge without ever cutting a trunk!
    add_keepout(["F.Cu", "B.Cu"], [(11.35+dx, 91.50), (18.15+dx, 91.50), (18.15+dx, 103.50), (11.35+dx, 103.50)],
                no_tracks=True, no_vias=False, no_pours=False)
    add_keepout(["F.Cu", "B.Cu"], [(43.65+dx, 91.50), (50.15+dx, 91.50), (50.15+dx, 103.50), (43.65+dx, 103.50)],
                no_tracks=True, no_vias=False, no_pours=False)
    add_keepout(["F.Cu", "B.Cu"], [(18.60+dx, 90.50), (31.00+dx, 90.50), (31.00+dx, 111.50), (18.60+dx, 111.50)],
                no_tracks=True, no_vias=False, no_pours=False)
    add_keepout(["F.Cu", "B.Cu"], [(50.80+dx, 90.50), (63.00+dx, 90.50), (63.00+dx, 118.00), (50.80+dx, 118.00)],
                no_tracks=True, no_vias=False, no_pours=False)
    add_keepout(["F.Cu", "B.Cu"], [(79.40+dx, 90.50), (91.30+dx, 90.50), (91.30+dx, 111.50), (79.40+dx, 111.50)],
                no_tracks=True, no_vias=False, no_pours=False)

pcbnew.SaveBoard(PCB_PATH, board)
print("Saved Unit B pours & vias successfully.")
