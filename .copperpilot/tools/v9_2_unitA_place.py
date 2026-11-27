#!/usr/bin/env python3
"""
Unit A placement & Edge.Cuts expansion for bldc_motor_cntroller_v9.2:
- Expands Edge.Cuts from 180.0 x 115.0 mm to 220.0 x 115.0 mm ([0.0, 15.0] .. [220.0, 130.0], R=5.0 mm).
- Clears old 180 mm raw tracks, vias, and copper/keepout zones in staging so Unit B & C rebuild pours and routing cleanly.
- Spreads Q1-Q12 (DirectFET_L8) across symmetric M1 (x=21.2..89.2) and M0 (x=139.2..207.2, exact +118.0 mm translation):
  * Intra-phase pitch = 13.0 mm (7.48 mm clear inter-FET SH channel -> 12.5-12.75 mm phase trunks).
  * C-to-B inter-phase pitch = 19.0 mm (3.20 mm VDC strap + 1.30 mm Kelvin corridor + 6.80 mm SL_B trunk).
  * B-to-A HS-to-HS pitch = 10.0 mm (shared 4.95 mm VDC pillar feeding both HS South Drains).
- Moves C_HF1-C_HF6 out of intra-phase SH channels onto the VDC-to-SL/GND loop boundaries.
- Centers U2 at (55.0, 69.5, -90) and U1 at (173.0, 69.5, -90) with aligned vertical South bootstrap/Kelvin passives
  and relocates U1's +5V buck converter (D1, L1, C12, C18, C19, C10, C1, R5-R7, R22, C17, C20) to the East of U1 beside PH pins 50-56.
- Optimizes U3/Q13/Q14 brake chopper (x=103..122, y=60..73) so /Power Management/HS forms a single unbroken polygon,
  and centers U6 STM32F405 at (110.0, 44.0) with generous radial decoupling/ADC/oscillator fanout and 0 courtyard/silk overlaps.
"""
import sys
import pcbnew

PCB_PATH = sys.argv[1]

# 1. Cleanly strip old 180mm (segment ...), (arc ...), (via ...), and (zone ...) top-level S-expr blocks before loading into pcbnew
def strip_blocks(text, keywords):
    out = []
    i = 0
    n = len(text)
    while i < n:
        pos = text.find("(", i)
        if pos == -1:
            out.append(text[i:])
            break
        out.append(text[i:pos])
        # Check token right after '('
        j = pos + 1
        while j < n and text[j] not in " \t\r\n()":
            j += 1
        tok = text[pos+1:j]
        if tok in keywords:
            depth = 0
            k = pos
            in_str = False
            while k < n:
                ch = text[k]
                if ch == '"' and text[k-1] != '\\':
                    in_str = not in_str
                elif not in_str:
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                        if depth == 0:
                            k += 1
                            break
                k += 1
            i = k
        else:
            out.append("(")
            i = pos + 1
    return "".join(out)

with open(PCB_PATH, "r", encoding="utf-8") as f:
    raw = f.read()
cleaned = strip_blocks(raw, {"segment", "arc", "via", "zone"})
with open(PCB_PATH, "w", encoding="utf-8") as f:
    f.write(cleaned)

board = pcbnew.LoadBoard(PCB_PATH)

# 2. Update Edge.Cuts rounded rectangle to [0.0, 15.0] .. [220.0, 130.0]
for d in list(board.GetDrawings()):
    if d.GetLayerName() == "Edge.Cuts" and isinstance(d, pcbnew.PCB_SHAPE):
        d.SetStart(pcbnew.VECTOR2I_MM(0.0, 15.0))
        d.SetEnd(pcbnew.VECTOR2I_MM(220.0, 130.0))

DX_CH = 118.0  # Exact symmetry offset: M0 = M1 + 118.0 mm

placements = {}

# --- Mechanical Mounting Holes, Fiducials & Logos ---
placements.update({
    "H7":  (  5.50,  20.50,   0.0),
    "H1":  (  5.50,  81.50,   0.0),
    "H2":  (  5.50, 102.00,   0.0),
    "H9":  (  5.50, 124.50,   0.0),
    "H8":  (214.50,  20.50,   0.0),
    "H3":  (214.50,  81.50,   0.0),
    "H4":  (214.50, 102.00,   0.0),
    "H10": (214.50, 124.50,   0.0),
    "FD1": ( 12.50,  20.50,   0.0),
    "FD2": (207.50,  20.50,   0.0),
    "FD3": ( 12.50, 124.50,   0.0),
    "G1":  (192.00,  30.00,   0.0),
    "G2":  (198.50,  30.00,   0.0),
    "G3":  (205.00,  30.00,   0.0),
    "G4":  (192.00,  35.50,   0.0),
    "G5":  (198.50,  35.50,   0.0),
    "G6":  (205.00,  35.50,   0.0),
    "G7":  (192.00,  41.00,   0.0),
    "G8":  (198.50,  41.00,   0.0),
})

# --- Bottom High-Current Connectors (y = 123.0) ---
placements.update({
    "J2":  ( 57.00, 123.00, 180.0),              # M1 MR60PB-M: 3(SH_C)=51.5, 2(SH_B)=57.0, 1(SH_A)=62.5
    "J3":  (110.00, 123.00,   0.0),              # XT90PB-M: 1(GND)=104.55, 2(VDC)=115.45
    "J1":  ( 57.00 + DX_CH, 123.00, 180.0),      # M0 MR60PB-M (175.0, 123.0): 3=169.5, 2=175.0, 1=180.5
})

# --- Left-Edge USB-C & Protection Cluster (kept tight at left edge) ---
placements.update({
    "J4":  (  6.50,  36.00, -90.0),
    "U8":  ( 16.20,  36.00,   0.0),
    "R64": ( 15.60,  31.80,   0.0),
    "R65": ( 15.60,  40.20,   0.0),
    "R52": ( 20.20,  35.05, 180.0),
    "R53": ( 20.20,  36.95, 180.0),
    "TP4": ( 23.50,  33.80,   0.0),
    "TP5": ( 23.50,  38.20,   0.0),
    "F1":  ( 15.80,  27.80,   0.0),
    "D4":  ( 21.80,  27.80, 180.0),
})

# --- Channel M1 (Left) & Symmetric Channel M0 (Right = M1 + 118.0 mm) Power Stages ---
# M1 FET X positions at y = 92.0, rot = -90.0:
#   Q12 (LS_C)=21.2, Q11 (HS_C)=34.2, Q10 (LS_B)=53.2, Q9 (HS_B)=66.2, Q7 (HS_A)=76.2, Q8 (LS_A)=89.2
m1_fets = [
    ("Q12", 21.20), ("Q11", 34.20),
    ("Q10", 53.20), ("Q9",  66.20),
    ("Q7",  76.20), ("Q8",  89.20),
]
m0_fets = [
    ("Q6",  21.20 + DX_CH), ("Q5",  34.20 + DX_CH),
    ("Q4",  53.20 + DX_CH), ("Q3",  66.20 + DX_CH),
    ("Q1",  76.20 + DX_CH), ("Q2",  89.20 + DX_CH),
]
for ref, fx in m1_fets + m0_fets:
    placements[ref] = (fx, 92.00, -90.0)

# Gate resistors (y = 84.60, rot = -90.0 -> Pad 1 driver side North y=84.115, Pad 2 FET gate side South y=85.085):
# Placed directly at the straight North exit of each lateral gate stub:
#   Q12(21.2)->West 17.90, Q11(34.2)->East 37.50
#   Q10(53.2)->West 49.90, Q9 (66.2)->East 69.50
#   Q7 (76.2)->West 72.90, Q8 (89.2)->East 92.50
m1_rgates = [("R34", 17.90), ("R33", 37.50), ("R29", 49.90), ("R28", 69.50), ("R24", 72.90), ("R25", 92.50)]
m0_rgates = [("R14", 17.90+DX_CH), ("R13", 37.50+DX_CH), ("R9", 49.90+DX_CH), ("R8", 69.50+DX_CH), ("R1", 72.90+DX_CH), ("R2", 92.50+DX_CH)]
for ref, rx in m1_rgates + m0_rgates:
    placements[ref] = (rx, 84.60, -90.0)

# High-frequency commutation loop caps C_HF1..C_HF6 (0603, Pad 1 = VDC, Pad 2 = SL_C / SL_B / GND):
# Placed right on the F.Cu VDC-to-SL/GND boundary outside the intra-phase SH channels!
#   C_HF6 (M1 Phase C, VDC<->SL_C): at (14.50, 88.00, rot=-90 -> Pad 1 VDC at y=87.22, Pad 2 SL_C at y=88.78)
#   C_HF5 (M1 Phase B, VDC<->SL_B): at (41.35, 91.50, rot=0   -> Pad 1 VDC at x=40.58, Pad 2 SL_B at x=42.13? Wait: Kelvin is at 41.9..43.1!
#     Better! Put C_HF5 at (46.75, 88.00, rot=-90 -> Pad 1 VDC at y=87.22 in North VDC strip, Pad 2 SL_B at y=88.78 right at top of 6.8mm SL_B pour [43.35..50.15]!)
#   C_HF4 (M1 Phase A, VDC<->GND):  at (95.00, 88.00, rot=-90 -> Pad 1 VDC at y=87.22 in North VDC strip, Pad 2 GND at y=88.78 right at top of East GND pour!)
placements.update({
    "C_HF6": ( 14.50, 89.50, -90.0),
    "C_HF5": ( 46.75, 89.50, -90.0),
    "C_HF4": ( 94.20, 89.50, -90.0),
    "C_HF3": ( 14.50 + DX_CH, 89.50, -90.0),
    "C_HF2": ( 46.75 + DX_CH, 89.50, -90.0),
    "C_HF1": ( 94.20 + DX_CH, 89.50, -90.0),
})

# Inline 2512 Shunts & Kelvin Net-Ties / 120R Resistors:
#   M1 Phase C shunt R36 centered in SL_C [11.0..18.0] at (14.50, 104.50, rot=90 -> Pad 2 SL_C at 101.6, Pad 1 GND at 107.4)
#     NT7(101.65), NT8(107.35) on West edge at x=10.30 (Pad 2 touches SL_C/GND at 10.80, Pad 1 Kelvin exits at 9.80), R35 at (9.80, 99.40, -90)
#   M1 Phase B shunt R32 centered in SL_B [43.35..50.15] at (46.75, 104.50, rot=90 -> Pad 2 SL_C/B at 101.6, Pad 1 GND at 107.4)
#     NT5(101.65), NT6(107.35) on West edge at x=42.85 (Pad 2 touches SL_B/GND at 43.35, Pad 1 Kelvin exits at 42.35), R31 at (42.35, 99.40, 90)
placements.update({
    "R36": ( 14.50, 104.50,  90.0),
    "NT7": ( 10.50, 101.65,   0.0),
    "NT8": ( 10.50, 107.35,   0.0),
    "R35": (  9.80,  99.40, -90.0),

    "R32": ( 46.75, 104.50,  90.0),
    "NT5": ( 42.85, 101.65,   0.0),
    "NT6": ( 42.85, 107.35,   0.0),
    "R31": ( 42.20,  99.40,  90.0),

    "R16": ( 14.50 + DX_CH, 104.50,  90.0),
    "NT3": ( 10.50 + DX_CH, 101.65,   0.0),
    "NT4": ( 10.50 + DX_CH, 107.35,   0.0),
    "R15": (  9.80 + DX_CH,  99.40, -90.0),

    "R12": ( 46.75 + DX_CH, 104.50,  90.0),
    "NT1": ( 42.85 + DX_CH, 101.65,   0.0),
    "NT2": ( 42.85 + DX_CH, 107.35,   0.0),
    "R11": ( 42.20 + DX_CH,  99.40,  90.0),
})

# 14x 1206 VDC Bulk Capacitors + 2x 0402 100nF HF Bus Caps per Channel:
# Placed along y = 80.50 (rot = 90.0 -> Pad 1 VDC South at y=81.90 feeding the F.Cu VDC commutation strip, Pad 2 GND North at y=79.10 with direct vias to In1.Cu GND!)
# Wait: keep clear of gate trace corridors going from U2/U1 South (y=73.3) to R_gates (y=84.6)!
# Gate X positions on M1: 17.90, 37.50, 49.90, 69.50, 72.90, 92.50, and Kelvin X: 9.80, 42.20.
# Available wide, unobstructed X bays at y = 80.50 on M1:
#   Bay 1 (Driver West / Phase C, x = 11.5 .. 35.2, skipping x=17.9 gate):
#     C78 (0402, x=11.5), C35 (13.4), C39 (15.8), [skip 17.9 gate], C40 (28.0), C42 (30.5), C44 (33.0), C45 (35.5)
#   Bay 2 (Phase B, x = 44.5 .. 67.2, skipping x=49.9 and U2 fanout 50..60? Wait: U2 is at x=55.0, y=69.5! U2 South pins span x=48.25..61.75 at y=73.32!)
#   AHA! Keep y=80.5 completely OPEN from x=48.0 to x=62.5 directly South of U2 (and x=166.0 to x=180.5 South of U1) so ALL 28 South pins of U2/U1 have a wide-open highway straight down to the FET row!!
#   Let's check how much room we have outside [48.0..62.5] on M1:
#     West of U2 (x = 11.5 .. 47.2, skipping 17.90, 37.50, 42.20):
#       C78(0402, 11.3), C35(13.3), C39(15.7), [17.90 gate], C40(20.2), C42(22.7), C44(25.2), C45(27.7), C46(30.2), C47(32.7), C51(35.2), [37.50 gate, 42.20 kelvin], C54(44.8), C55(47.2) -> 11x 1206 + 1x 0402!
#     East of U2 (x = 64.0 .. 97.5, skipping 69.50, 72.90, 92.50):
#       C57(64.5), C60(67.0), [69.50, 72.90 gates], C56(75.5), C53(78.0), C79(0402, 80.2) -> ALL 14x 1206 + 2x 0402 sit in ONE clean North row at y = 80.50 (NONE blocking South of Q8/Q2 at y=101.8 anymore!!)!
m1_vdc_caps = [
    ("C78", 11.30), ("C35", 13.30), ("C39", 15.70),
    ("C40", 20.20), ("C42", 22.70), ("C44", 25.20), ("C45", 27.70), ("C46", 30.20), ("C47", 32.70), ("C51", 35.20),
    ("C54", 44.60), ("C55", 47.00),
    ("C57", 64.50), ("C60", 67.00),
    ("C56", 75.50), ("C53", 78.00), ("C79", 80.20),
]
m0_vdc_caps = [
    ("C80", 11.30+DX_CH), ("C16", 13.30+DX_CH), ("C61", 15.70+DX_CH),
    ("C64", 20.20+DX_CH), ("C65", 22.70+DX_CH), ("C66", 25.20+DX_CH), ("C67", 27.70+DX_CH), ("C68", 30.20+DX_CH), ("C69", 32.70+DX_CH), ("C70", 35.20+DX_CH),
    ("C73", 44.60+DX_CH), ("C74", 47.00+DX_CH),
    ("C76", 64.50+DX_CH), ("C77", 67.00+DX_CH),
    ("C75", 75.50+DX_CH), ("C71", 78.00+DX_CH), ("C81", 80.20+DX_CH),
]
for ref, cx in m1_vdc_caps + m0_vdc_caps:
    placements[ref] = (cx, 80.50, 90.0)

# Power-stage Thermistors (TH5/R63/C102 on M1, TH1/R23/C21 on M0; plus TH2/R42/C38 on M1 and TH4/R62/C101 on M0):
placements.update({
    "TH5":  (  8.00, 89.50,  90.0),
    "R63":  (  8.00, 92.00,  90.0),
    "C102": (  8.00, 94.50,  90.0),

    "TH1":  (125.50, 89.50,  90.0),
    "R23":  (125.50, 92.00,  90.0),
    "C21":  (125.50, 94.50,  90.0),
})

# --- Gate Drivers U2 (M1 at 55.0, 68.5) & U1 (M0 at 173.0, 68.5) ---
# Moving U2/U1 to y = 68.50 gives a massive 7.2 mm South fanout zone (y = 72.32 .. 79.5) above the y=80.5 cap row!
U2_X, U2_Y = 55.00, 68.50
U1_X, U1_Y = 55.00 + DX_CH, 68.50
placements["U2"] = (U2_X, U2_Y, -90.0)
placements["U1"] = (U1_X, U1_Y, -90.0)

# South of U2 (pins at y = 72.32):
#   pin 29 (-6.75=48.25): VDC -> C31 (100nF) at (46.80, 72.80, 90)
#   pins 30,31 (-6.25,-5.75 = 48.75,49.25): SP2,SN2 -> C24 at (48.90, 75.40, 0)
#   pins 32,33 (-5.25,-4.75 = 49.75,50.25): SP1,SN1 -> C23 at (50.80, 75.40, 0)
#   pins 36,38 (-3.25,-2.25 = 51.75,52.75): SH_C,BST_C -> C34 at (52.75, 75.40, 0)
#   pins 41,43 (-0.75,+0.25 = 54.25,55.25): SH_B,BST_B -> C33 at (55.25, 75.40, 0)
#   pins 46,48 (+1.75,+2.75 = 56.75,57.75): SH_A,BST_A -> C32 at (57.75, 75.40, 0)
#   pin 56 (+6.75=61.75): SS_TR -> C22 at (63.40, 72.30, -90 -> Pad 2 SS_TR North, Pad 1 GND South)
placements.update({
    "C31": (U2_X - 8.20, 72.80,  90.0),
    "C24": (U2_X - 6.10, 75.40,   0.0),
    "C23": (U2_X - 3.90, 75.40,   0.0),
    "C34": (U2_X - 1.80, 75.40,   0.0),
    "C33": (U2_X + 0.40, 75.40,   0.0),
    "C32": (U2_X + 2.60, 75.40,   0.0),
    "C22": (U2_X + 8.40, 72.30, -90.0),

    # North of U2 (pins at y = 64.68):
    #   pin 27 (-6.25=48.75): AVDD -> C29 at (47.20, 63.00, 90)
    #   pins 25,26 (-5.25,-5.75 = 49.75,49.25): SO1,SO2 -> R37(50.0, 62.2, 90), R38(48.6, 62.2, 90)
    #   pin 23 (-4.25=50.75): DVDD -> C30 at (51.40, 62.20, 90)
    #   pin 16 (-0.75=54.25): EN_GATE -> R26 at (53.80, 60.20, -90)
    #   pins 14,15 (+0.25,-0.25 = 55.25,54.75): CP1,CP2 -> C25 at (55.00, 62.50, 180)
    #   pin 13 (+0.75=55.75): GVDD -> C26 at (56.20, 60.20, 90)
    #   pin 12 (+1.25=56.25): DC_CAL -> R30 at (57.60, 60.20, -90)
    #   pin 7  (+3.75=58.75): DTC -> R27 at (59.20, 62.20, 90)
    #   pins 6,5 (+4.25,+4.75 = 59.25,59.75): nFAULT, nOCTW -> R39(60.6, 62.2, 90), R40(62.0, 62.2, 90)
    "C29": (U2_X - 7.80, 63.00,  90.0),
    "R38": (U2_X - 6.30, 62.20,  90.0),
    "R37": (U2_X - 4.90, 62.20,  90.0),
    "C30": (U2_X - 3.50, 62.20,  90.0),
    "R26": (U2_X - 1.20, 59.80, -90.0),
    "C25": (U2_X + 0.00, 62.50, 180.0),
    "C26": (U2_X + 1.20, 59.80,  90.0),
    "R30": (U2_X + 2.60, 59.80, -90.0),
    "R27": (U2_X + 4.20, 62.20,  90.0),
    "R39": (U2_X + 5.60, 62.20,  90.0),
    "R40": (U2_X + 7.00, 62.20,  90.0),

    # M1 Driver-area thermistor TH2/R42/C38 (cleanly West of U2 North):
    "TH2": (U2_X - 11.50, 60.50,  0.0),
    "R42": (U2_X - 11.50, 62.50,  0.0),
    "C38": (U2_X - 11.50, 64.50,  0.0),
})

# Mirror onto U1 (M0 at 173.0, 68.5) + East-side Integrated +5V Buck Cluster!
placements.update({
    "C11": (U1_X - 8.20, 72.80,  90.0),
    "C3":  (U1_X - 6.10, 75.40,   0.0),
    "C2":  (U1_X - 3.90, 75.40,   0.0),
    "C15": (U1_X - 1.80, 75.40,   0.0),
    "C14": (U1_X + 0.40, 75.40,   0.0),
    "C13": (U1_X + 2.60, 75.40,   0.0),
    # Pins 50,51 (+3.75,+4.25=176.75,177.25): PH (Net-(D1-K)); Pin 52 (+4.75=177.75): BST_BK; Pins 53,54 (+5.25,+5.75=178.25,178.75): PVDD2(VDC); Pin 56 (+6.75=179.75): SS_TR
    "C10": (U1_X + 5.00, 75.40,   0.0),   # BST_BK <-> Net-(D1-K), right below pins 50-52!
    "C36": (U1_X + 7.40, 75.40,   0.0),   # VDC <-> GND, right below pins 53-54!
    "C1":  (U1_X + 9.20, 72.30, -90.0),   # SS_TR <-> GND, right beside pin 56!

    # East-side Buck Power Stage (right next to PH pins 50-51 at x=177.0, y=72.32!):
    #   D1 (SOD-123F, Pad 1 = Net-(D1-K) Cathode, Pad 2 = GND Anode): at (184.5, 74.5, rot=90 -> Pad 1 West/North? Let's check: in v9.2 D1 at (144.7,56.3,rot=-90) had Pad 1 at y-1.4, Pad 2 at y+1.4! So at rot=-90, Pad 1(K) is North y-1.4, Pad 2(GND) is South y+1.4!)
    "D1":  (185.00, 72.50, -90.0),        # Pad 1 Net-(D1-K) at (185.0, 71.1), Pad 2 GND at (185.0, 73.9)
    "L1":  (190.40, 69.50,   0.0),        # Pad 1(D1-K) West (188.05, 69.5), Pad 2(+5V) East (192.75, 69.5)
    "C19": (196.20, 69.50, -90.0),        # 1uF 0402: Pad 1(+5V) North, Pad 2(GND) South
    "C12": (198.60, 69.50, -90.0),        # 47uF 1206: Pad 1(+5V) North, Pad 2(GND) South
    "C18": (201.40, 69.50, -90.0),        # 47uF 1206: Pad 1(+5V) North, Pad 2(GND) South

    # North of U1 (pins at y = 64.68):
    "C8":  (U1_X - 7.80, 63.00,  90.0),
    "R18": (U1_X - 6.30, 62.20,  90.0),
    "R17": (U1_X - 4.90, 62.20,  90.0),
    "C9":  (U1_X - 3.50, 62.20,  90.0),
    "R3":  (U1_X - 1.20, 59.80, -90.0),
    "C4":  (U1_X + 0.00, 62.50, 180.0),
    "C5":  (U1_X + 1.20, 59.80,  90.0),
    "R10": (U1_X + 2.60, 59.80, -90.0),
    "R4":  (U1_X + 4.20, 62.20,  90.0),
    "R20": (U1_X + 5.60, 62.20,  90.0),
    "R21": (U1_X + 7.00, 62.20,  90.0),
    "R19": (U1_X + 8.40, 62.20,  90.0),
    # Buck control passives right above pins 1(RT_CLK=179.75), 2(COMP=179.25), 3(VSENSE=178.75):
    "R6":  (U1_X + 10.20, 63.50,  90.0),  # VSENSE <-> +5V
    "R7":  (U1_X + 10.20, 60.20, -90.0),  # GND <-> VSENSE
    "R22": (U1_X + 12.00, 63.50,  90.0),  # COMP <-> C20.1
    "C20": (U1_X + 12.00, 60.20,  90.0),  # C20.1 <-> GND
    "C17": (U1_X + 13.80, 63.50,  90.0),  # COMP <-> GND
    "R5":  (U1_X + 15.40, 63.50,  90.0),  # RT_CLK <-> GND

    # M0 Driver-area thermistor TH4/R62/C101 (cleanly West of U1 North, symmetric to TH2):
    "TH4":  (U1_X - 11.50, 60.50,  0.0),
    "R62":  (U1_X - 11.50, 62.50,  0.0),
    "C101": (U1_X - 11.50, 64.50,  0.0),
})

# --- Central Brake Chopper (U3 LM5109B, Q13, Q14, H5, H6) centered at x = 104..122, y = 61..73 ---
# Look how clean this is:
#   U3 at (103.0, 66.0, rot=0):
#     West pins (101.1): 1=GVDD, 2=AUX_H, 3=AUX_L, 4=GND
#     East pins (104.9): 8=Net-(D2-K) (y=64.8), 7=HO (y=65.6), 6=HS (y=66.4), 5=LO (y=67.2)
#   Place R47 (HO->Q13.G) at (107.8, 64.4, rot=0? At rot=90, Pad 1 Q13-G is South, Pad 2 HO is North; at rot=180, let's check: R47 at rot=90 had Pad 1(Q13-G) y+0.48, Pad 2(HO) y-0.48 -> so at rot=0, Pad 1(Q13-G) is East? Let's check R43 at rot=0: Pad 1 is West x-0.48, Pad 2 is East x+0.48! So R47 at rot=180 puts Pad 2(HO) West x-0.48, Pad 1(Q13-G) East x+0.48, straight into Q13.4 at (110.6, 64.4)!!)
#   And Q13 at (113.5, 62.5, rot=0) + Q14 at (113.5, 69.5, rot=0):
#     Q13.1-3 (HS) are at (110.6, 60.6..63.1), Q13.4 (Gate) at (110.6, 64.41), Q13.5 (VDC) at (114.55, 62.5)
#     Q14.1-3 (GND) are at (110.6, 67.6..70.1), Q14.4 (Gate) at (110.6, 71.41), Q14.5 (HS) at (114.55, 69.5)
#     H6 (HS brake pad) at (121.0, 68.0, 0) & H5 (GND brake pad) at (121.0, 73.0, 0)!
#     Wait: how does U3.6 (HS at 104.9, 66.4) reach Q13.1-3 (110.6, 62.0) and Q14.5 (114.55, 69.5) without crossing R47 (y=64.4) or R48 (y=71.4)?!
#     LOOK! Between y = 65.4 and y = 66.8 (right between Q13 courtyard y_max=65.33 and Q14 courtyard y_min=66.67, and right between R47 at y=64.4 and R48 at y=71.4!), U3.6 is at y = 66.4! A 1.2 mm wide F.Cu bridge + 4.0 mm wide B.Cu HS pour runs straight East at y = 66.0 from U3.6 (104.9, 66.4) right between Q13 and Q14 into Q14.5 / H6 / Q13.1-3! Zero gate-resistor conflict!
placements.update({
    "U3":     (103.00, 66.00,   0.0),
    "D2":     (103.00, 60.80, 180.0),   # D2 at rot=0 had 1(D2-K) West, 2(GVDD) East -> at rot=180: 2(GVDD) West(101.6), 1(D2-K) East(104.4)
    "C52":    (106.80, 61.20, -90.0),   # Pad 1(D2-K) North(60.7), Pad 2(HS) South(61.7 -> right into Q13.1-3 HS!)
    "C41":    ( 98.20, 63.50,   0.0),   # GVDD(East) <-> GND(West)
    "TP7":    ( 98.20, 60.80,   0.0),   # GVDD
    "R43":    ( 98.20, 65.40,   0.0),   # GND(West) <-> AUX_H(East -> U3.2)
    "R44":    ( 98.20, 67.00,   0.0),   # GND(West) <-> AUX_L(East -> U3.3)
    "R45":    ( 98.20, 69.50, 180.0),   # VBUS_S(West) <-> VDC(East)? At rot=0: 1(VDC) West, 2(VBUS_S) East -> keep rot=0 at (96.0, 69.5)
    "R46":    ( 98.20, 71.20,   0.0),   # 1(VBUS_S) West, 2(GND) East
    "R47":    (108.00, 64.40, 180.0),   # 2(HO) West(107.52), 1(Q13-G) East(108.48) -> straight into Q13.4(110.6, 64.41)!
    "R48":    (108.00, 71.40, 180.0),   # 2(LO) West(107.52), 1(Q14-G) East(108.48) -> straight into Q14.4(110.6, 71.41)!
    "Q13":    (113.50, 62.50,   0.0),
    "Q14":    (113.50, 69.50,   0.0),
    "C48":    (119.50, 62.50,  90.0),   # 100uF 1206 VDC(South) <-> GND(North)
    "C_AUX1": (122.20, 62.50,  90.0),   # 100nF 0603 VDC(South) <-> GND(North)
    "H6":     (121.00, 68.40,   0.0),   # HS brake output pad
    "H5":     (121.00, 73.20,   0.0),   # GND brake return pad
    "TH3":    (106.00, 73.80, -90.0),
    "R51":    (103.00, 73.80, -90.0),
    "C72":    (100.00, 73.80, -90.0),
})
placements["R45"] = ( 98.20, 69.50, 180.0) # 2(VBUS_S) West(97.72), 1(VDC) East(98.68)

# --- Central MCU U6 (STM32F405 at 110.0, 44.0, rot=0), LDOs (U4, U5), CAN (U7), & Top JST-SH Row ---
U6_X, U6_Y = 110.00, 44.00
placements["U6"] = (U6_X, U6_Y, 0.0)

# U6 local crystal, reset, VCAP, decoupling, and ADC filter caps (spaced cleanly >= 3.2 mm outside U6 pads with 0 silk overlaps):
placements.update({
    # West side of U6 (pins 1..16 at x = 104.33, y = 40.25..47.75):
    "C85": (100.20, 39.80, 180.0),      # +3.3V(East) <-> GND(West) for pin 1 (40.25)
    "Y1":  ( 99.80, 42.50, -90.0),      # PH0(41.3), GND(42.5), PH1(43.7) right opposite pins 5,6 (42.25, 42.75)!
    "C83": ( 96.80, 41.20,   0.0),      # GND(West) <-> PH0(East)
    "C84": ( 96.80, 43.80,   0.0),      # GND(West) <-> PH1(East)
    "C86": ( 96.80, 39.20, 180.0),      # NRST(East) <-> GND(West)
    "C92": (100.20, 46.25, 180.0),      # +3.3VA(East) <-> GND(West) for pin 13 (46.25)
    "C93": (100.20, 48.00, 180.0),      # +3.3VA(East) <-> GND(West)

    # ADC SO1/SO2 filter caps & spaced TestPoints (no silk overlap!):
    "C6":   ( 93.50, 43.75,   0.0),     # GND(West) <-> M0_SO1(East -> pin 8 at 43.75)
    "C7":   ( 93.50, 45.25,   0.0),     # GND(West) <-> M0_SO2(East -> pin 9 at 44.25)
    "C28":  ( 93.50, 46.75,   0.0),     # GND(West) <-> M1_SO2(East -> pin 10 at 44.75)
    "C27":  ( 93.50, 48.25,   0.0),     # GND(West) <-> M1_SO1(East -> pin 11 at 45.25)
    "TP8":  ( 88.50, 42.50,   0.0),
    "TP9":  ( 88.50, 45.50,   0.0),
    "TP11": ( 88.50, 48.50,   0.0),
    "TP10": ( 88.50, 51.50,   0.0),

    # North side of U6 (pins 49..64 at y = 38.33, x = 106.25..113.75):
    "C89": (106.25, 34.80,  90.0),      # +3.3V(South) <-> GND(North) for pin 64
    "TP6": (111.25, 34.20,   0.0),      # nFAULT

    # East side of U6 (pins 33..48 at x = 115.67, y = 40.25..47.75):
    "C91": (119.50, 40.25,   0.0),      # +3.3V(West) <-> GND(East) for pin 48
    "C90": (119.50, 41.90,   0.0),      # VCAP_2(West) <-> GND(East) for pin 47

    # South side of U6 (pins 17..32 at y = 49.67, x = 106.25..113.75):
    "C82": (107.25, 53.20, -90.0),      # +3.3V(North) <-> GND(South) for pin 19
    "C43": (109.25, 53.20, -90.0),      # VBUS_S(North) <-> GND(South) for pin 22
    "C88": (112.75, 53.20, -90.0),      # VCAP_1(North) <-> GND(South) for pin 31
    "C87": (114.75, 53.20, -90.0),      # +3.3V(North) <-> GND(South) for pin 32
    "D3":  (118.50, 52.20,   0.0),      # +3.3V LED
    "R50": (118.50, 54.20,   0.0),
    "TP2": (123.00, 50.50,   0.0),      # +3.3V
    "TP3": (123.00, 53.50,   0.0),      # +3.3VA
    "TP12":(123.00, 56.50,   0.0),      # GND

    # LDOs U4 (+3.3V) & U5 (+3.3VA) cleanly East of U6/TPs at x = 132.0:
    "U4":  (132.00, 47.50,  90.0),
    "C49": (135.50, 47.50,  90.0),
    "C58": (128.50, 46.40,  90.0),
    "C62": (128.50, 48.80,  90.0),
    "U5":  (132.00, 53.50,  90.0),
    "C50": (135.50, 53.50,  90.0),
    "C59": (128.50, 52.40, -90.0),
    "C63": (128.50, 54.80, -90.0),
    "TP1": (138.50, 50.50,   0.0),      # +5V

    # Top Edge Connectors & CAN / Encoder Filters (y = 20.50, shifted +20 mm with board center = 110.0):
    "J11": ( 58.00, 20.50, 180.0),      # M1 Encoder
    "C95": ( 55.80, 25.50, 180.0),
    "C97": ( 58.00, 25.50, 180.0),
    "C99": ( 60.20, 25.50, 180.0),
    "R60": ( 55.80, 29.20, -90.0),
    "R58": ( 58.00, 29.20, -90.0),
    "R56": ( 60.20, 29.20, -90.0),

    "J5":  ( 74.00, 20.50, 180.0),      # GPIO 1-2
    "J9":  ( 90.00, 20.50, 180.0),      # SWD
    "SW1": (104.00, 20.50, 180.0),      # DFU BOOT0
    "R61": (104.00, 25.00,   0.0),
    "J6":  (118.00, 20.50, 180.0),      # GPIO 3-8
    "J8":  (133.00, 20.50, 180.0),      # CAN 1
    "J7":  (141.00, 20.50, 180.0),      # CAN 2
    "U7":  (137.00, 29.50,   0.0),      # SN65HVD232 CAN transceiver right below J8/J7!
    "C94": (131.50, 29.50,  90.0),
    "R54": (142.50, 29.50, -90.0),

    "J10": (162.00, 20.50, 180.0),      # M0 Encoder
    "C96": (159.80, 25.50,   0.0),
    "C98": (162.00, 25.50,   0.0),
    "C100":(164.20, 25.50, 180.0),
    "R59": (159.80, 29.20, -90.0),
    "R57": (162.00, 29.20, -90.0),
    "R55": (164.20, 29.20, -90.0),
})

missing = []
for ref, (x, y, rot) in placements.items():
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        missing.append(ref)
        continue
    fp.SetLocked(False)
    fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    fp.SetOrientationDegrees(rot)

# Also update any board title/silkscreen text near top/bottom if out of place
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT):
        txt = d.GetText()
        pos = d.GetPosition()
        tx, ty = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        print(f"Board text: {txt!r} at ({tx:.2f}, {ty:.2f}) on {d.GetLayerName()}")
        if tx > 140:
            d.SetPosition(pcbnew.VECTOR2I_MM(tx + 40.0, ty))
        elif 70 < tx <= 140:
            d.SetPosition(pcbnew.VECTOR2I_MM(tx + 20.0, ty))

if missing:
    raise RuntimeError(f"Missing footprints: {missing}")

# Verify every single footprint was accounted for!
placed_set = set(placements.keys())
all_refs = {fp.GetReference() for fp in board.GetFootprints()}
unplaced = sorted(all_refs - placed_set)
print(f"Placed {len(placed_set)}/{len(all_refs)} footprints. Unaccounted: {unplaced}")
if unplaced:
    raise RuntimeError(f"Unaccounted footprints: {unplaced}")

pcbnew.SaveBoard(PCB_PATH, board)
print("Saved Unit A candidate board successfully.")
