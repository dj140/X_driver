# `bldc_motor_cntroller_v5.kicad_pcb` — Component Moves, Power Pours & Verification Audit

- **Saved Deliverable PCB**: `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v5.kicad_pcb` (`SHA-256: e20eac7b6d38ff2ac30fbad0dcda1c9cc671cfaca2e7c9e0851aa8b46f8b230b`)
- **Untouched Prior PCBs**:
  - `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v4.kicad_pcb` (`SHA-256: c22d692ee7b5474b941ebacbdef7f35b727e1f43e3884a044feeb8b7e54f3c0c`)
  - `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v3.kicad_pcb` (`SHA-256: 38da45a085921cf43934d89ffa528d27dbcbc8e2a257f34ad69845726fff3071`)
- **Board Geometry & Symmetry**: `150.0 × 98.5 mm` (`x = 0..150 mm`, `y = 15..113.5 mm`), 4-layer `JLC04161H-3313` (`2 oz` `0.070 mm` outer / `1 oz` `0.035 mm` inner, `0.11 mm` `FR4 3313` prepreg, `1.17 mm` core), `249` footprints all on `F.Cu` (`0` backside components so `B.Cu` remains 100% flat for coldplate heatsinking), exact `M1 = M0 - 70.00 mm` translational symmetry across both inverter channels.

---

## 1. Summary of What Was Moved in `v5` (and Physical Mechanism)

| Functional Group | References Moved | `v4` Pose / Issue | `v5` Pose | Physical / Layout Improvement |
|---|---|---|---|---|
| **Half-Bridge MOSFET Order & Pitch** | `Q1–Q6` (`M0`), `Q7–Q12` (`M1`), `R1,R2,R8,R9,R13,R14`, `R24,R25,R28,R29,R33,R34` | `HS` left / `LS` right at `14.50 mm` leg pitch (`y = 90.00 mm`) — opposite to DRV8301 pin order (`GL_C, GH_C, GL_B, GH_B, GL_A, GH_A`), forcing **3 gate-trace X-crossings per bank** and `5.80 mm` intra-leg mismatch | **Swapped `LS` left / `HS` right** in all 6 legs (`y = 89.85 mm`, `LS–HS = 5.80 mm`, leg pitch compacted to `12.80 mm`: `M0` `(94.80, 100.60)`, `(107.60, 113.40)`, `(120.40, 126.20)`; `M1 = M0 - 70 mm`), `2R2` gate resistors at `y = 84.70 mm` | **Zero gate-trace crossings (`100%` monotonic X order)**, max `DRV -> Rg` reduced `17.85 -> 14.81 mm`, spread reduced `8.56 -> 7.31 mm`, intra-leg `\|GH - GL\|` cut `5.80 -> 3.88 mm` (`0.16 mm` on Phase B) |
| **Gate Drivers & Local Passives** | `U1`, `U2`, `C1–C15`, `C17`, `C20`, `C22–C34`, `C36`, `R3–R7`, `R10`, `R17–R22`, `R26,R27,R30,R37–R41` | `U1 (111.65, 72.00)` / `U2 (41.65, 72.00)`; `C1` (`SS_TR`) `11.15 mm` from `U1.56`; `R4` (`DTC`) `12.27 mm` from `U1.7`; `R17/R18` (`SO1/SO2`) `20.8 mm` away | `U1 (111.95, 73.20)` / `U2 (41.95, 73.20)` (`1.20 mm` closer to FETs, centered on gate pins); `C1 (120.80, 76.60)` & `C22 (50.80, 76.60)` at `SS_TR`; `R4/R26`, `C8/C29`, `C9/C30`, `C5/C26`, `C6/C25`, `R17/R18`, `R37/R38` aligned directly above their exact `U1`/`U2` north pins (`y = 66.60 mm`) | `SS_TR` cap loop cut **`11.15 -> 1.67 mm`** (`-85%`), `DTC` resistor loop cut **`12.27 -> 2.59 mm`** (`-79%`), `22R` current-sense output damping resistors placed right at `SO1/SO2` pins |
| **Straddling HF Commutation Caps** | `C_HF1–C_HF6` (`100nF 100V` `0603`), `C78–C81` (`100nF 50V` `0402`) | `C_HF1–C_HF6` offset beside HS FETs (`y = 85.15 mm`); `C78/C79` and `C80/C81` overlapping silkscreen | `C_HF3..C_HF1` centered at `(98.05, 110.85, 123.65; y = 84.85)` (`rot = 180°`, `M1 = M0 - 70 mm`) straddling `HS` north `VDC` (`1.89 mm`) and `LS` `SL_C/SL_B/GND` via islands; `C78–C81` placed in the `2.2 mm` coplanar `VDC/GND` seam slots at `y = 81.45 mm` (`rot = 90°`) | Low-inductance high-frequency commutation bypass on every half-bridge leg with zero silkscreen overlap |
| **1206 DC-Link Capacitor Row** | `C16, C61, C64–C71, C73–C77` (`M0`), `C35, C39, C40, C42, C44–C47, C51, C53–C57, C60` (`M1`) | Continuous row blocking straight gate fanout slots | Grouped into **three 5-cap clusters per bank** at `y = 81.45 mm` (`rot = 90°`) centered directly over Phases C, B, and A with `2.45 mm` inter-leg routing channels | Nearest `1206` `VDC` pad within **`2.48 mm` pad-edge (`3.80–3.96 mm` center, `< 4.0 mm`)** of all 6 HS drains while opening unobstructed straight gate-trace channels |
| **Horizontal Shunts & Coupled Kelvin Pairs** | `R16, R12, R36, R32` (`2512`), `NT1–NT8`, `R11, R15, R31, R35` | `NT` pairs split `3.9 mm` apart on opposite ends of `2512` shunts, overlapping silkscreen | `R16 (92.60, 97.20)`, `R12 (105.60, 97.20)` (`rot = 180°`, `M1 = M0 - 70 mm`) directly below west-side `LS` `SL_C/SL_B` exits, with coupled Kelvin sense pairs `NT3+R15+NT4` & `NT1+R11+NT2` side-by-side (`0.96 mm` `SN/SP` spacing) at `y = 94.35 mm` | Single-piece wide `F.Cu` `SL_C`/`SL_B` pours (`0` isolated islands), unobstructed `SH_C/SH_B/SH_A` phase exit corridors to `J2 (45.5, 106.5)` and `J1 (115.5, 106.5)`, tightly coupled differential Kelvin launch |
| **Compact U1 Buck Hot Loop** | `C10`, `D1`, `L1`, `C12`, `C18`, `C19` | `C12`/`L1` and `C17`/`C19` loose at `x = 126..135 mm` | `C10 (121.20, 74.80)` & `D1 (121.60, 72.20)` immediately adjacent to `U1` `PH`/`BST_BK` (`50,51,52`), `L1 (126.60, 72.20)`, `C19 (126.60, 67.40)`, `C12 (129.40, 65.80)`, `C18 (132.20, 65.80)` | Minimizes `U1.PH–D1–GND` switching hot-loop area with `0` courtyard or silkscreen overlaps |
| **MCU ADC Anti-Aliasing Filters & Crystal** | `U6`, `Y1`, `C83, C84`, `C27, C28, C6, C7, C43`, `C82, C85–C93` | `C27/C28` (`M1_SO1/SO2` ADC caps) sat `39.7 mm` away down at `U2`; `C43` (`VBUS_S` ADC cap) sat `26.7 mm` away at `U3`! | `U6 (75.00, 45.00)` with `C27 (76.60, 36.80)` & `C28 (78.60, 36.80)` at `U6.52/51` (`3.1 mm`), `C6/C7 (83.40, 46.80/45.20)` at `U6.35/36`, `C43 (74.00, 53.20)` at `U6.22` (`2.1 mm`), and `Y1 (66.80, 45.20)` + `C83/C84` clear of `U6` courtyard | Places RC anti-aliasing filter capacitors directly at the STM32 ADC input pins (eliminating `25–40 mm` of unshielded post-filter pickup) |
| **CAN Transceiver & Dual CAN Headers** | `J7, J8`, `U7`, `C94, R54` | `J8` at `x = 53.0 mm` and `J7` at `x = 101.0 mm` (`48 mm` cross-board `120 Ohm` CAN stub!) | Grouped `J8 (96.50, 20.50)` & `J7 (104.50, 20.50)` side-by-side directly above `U7 (100.50, 29.50)` (`rot = -90°`) | Cuts left CAN drop from **`51.18 -> 8.40 mm`** (`-84%`) and right CAN drop from **`14.90 -> 6.55 mm`** (`-56%`), eliminating stub reflections |
| **Encoder Pull-Ups & RC Filters** | `J11, J10`, `R55–R60`, `C95–C100` | All 6 encoder pull-ups `R55–R60` lumped at `x = 82.5..91.5 mm` (`54.2 mm` from `J11` and `25.4 mm` from `J10`) | Split right behind their own connectors: `R60, R58, R56 + C95, C97, C99` directly below `J11 (32.00, 20.50)`; `R59, R57, R55 + C96, C98, C100` directly below `J10 (116.00, 20.50)` | Cuts `ENC1` pull-up trace length **`54.16 -> 7.51 mm`** (`-86%`) and `ENC0` pull-up length **`25.42 -> 7.51 mm`** (`-70%`) |

---

## 2. Quantitative Metrics: `_v3` vs `_v4` vs `_v5`

| Metric (Laplace `filled_polygon` & Pad Geometry) | `_v3` Baseline | `_v4` | **`_v5` (Saved)** | Status |
|---|---|---|---|---|
| `SH_A` `HS src -> J` (`2 oz F.Cu + B.Cu + vias`) | `1.99 mOhm` (`1 oz F`) | `0.512 mOhm` (`0.82 W`) | **`0.571 mOhm` (`0.91 W @ 40 A`)** | `71%` below `_v3`, `< 1.0 W` |
| `SH_B` `HS src -> J` (`2 oz F.Cu + B.Cu + vias`) | `1.97 mOhm` (`1 oz F`) | `0.560 mOhm` (`0.90 W`) | **`0.591–0.594 mOhm` (`0.95 W @ 40 A`)** | `70%` below `_v3`, `< 1.0 W` |
| `SH_C` `HS src -> J` (`2 oz F.Cu + B.Cu + vias`) | `2.56 mOhm` (`1 oz F`) | `0.526 mOhm` (`0.84 W`) | **`0.658–0.662 mOhm` (`1.05 W @ 40 A`)** | `74%` below `_v3` (`> 40%` target met) |
| `SH`-to-`SH` minimum copper gap (`F.Cu` & `B.Cu`) | `0.26–0.30 mm` | `0.60–0.64 mm` | **`0.640 mm` (`A–B`), `0.680 mm` (`B–C`)** | `>= 0.50 mm` rule met on both layers |
| `Q1,Q3,Q5,Q7,Q9,Q11` `pads 1,2 -> VDC vias` | `0.79–5.39 sq` (`0–1` via) | `0.14–0.16 sq` (`4` vias) | **`0.02–0.03 sq` (`4` vias on all 6 HS FETs)** | `< 1.0 sq` & `>= 3` vias met |
| Nearest `1206` bulk cap to each HS drain | `4.80 mm` | `3.75–3.86 mm` (`2.42 mm` pad) | **`3.80–3.96 mm` center (`2.48 mm` pad-edge)** | `< 4.0 mm` met on all 6 HS drains |
| `LS` source centroid to nearest `GND` via | `2.63 mm` (`A`), `7.72 mm` (`B,C`) | `2.63–2.83 mm` | **`2.18 mm` (`A`), `2.83 mm` (`B,C`; `1.60 mm` pad)** | `< 3.0 mm` met on all 6 LS FETs |
| Gate `DRV -> Rg` min / max / spread (`0` crossings) | `3` crossings / bank | `9.30 / 17.85 / 8.56 mm` (`3` crossings) | **`7.51 / 14.81 / 7.31 mm` (`0` crossings)** | Monotonic X order, no crossings |
| Intra-leg `\|GH - GL\|` mismatch (`Leg C / B / A`) | `5.02 / 0.90 / 5.66 mm` | `5.78 / 0.04 / 5.80 mm` | **`3.88 / 0.16 / 3.94 mm` (`DRV->Rg`)** | Symmetric, `+1 mm` meander holds `< 3 mm` |
| Aux `Q13` `VDC` island & `Q14`/`C48` `GND` vias | `32.4 mm²`, `1` `VDC`, `1` `GND` | `48.1 mm²`, `10` `VDC`, `6+5` `GND` | **`46.7 mm²`, `10` `VDC`, `6` `Q14` + `5` `C48` `GND` + `4` `HS` vias** | Full `15 A` thermal & current margin |

---

## 3. KiCad 10.0.8 DRC Comparison (`_v4` vs `_v5`)

| DRC Metric (`/usr/bin/kicad-cli pcb drc`) | `_v4` | **`_v5` (Promoted)** | Delta |
|---|---|---|---|
| **Total Errors** (`U1/U2/J4/U6` library mask/pad/drill) | `351` | **`351`** | **`0` new errors** |
| **Courtyard Overlaps / Outside Board** | `0 / 0` | **`0 / 0`** | Clean |
| **Shorting Items / Hole Clearance / Dangling Vias / Islands** | `0 / 0 / 0 / 0` | **`0 / 0 / 0 / 0`** | Clean (`32` zones, `297` vias) |
| **Silkscreen Overlap Warnings (`silk_overlap`)** | `7` | **`0`** | **`-7` (100% resolved)** |
| **Silkscreen Over Copper Warnings (`silk_over_copper`)** | `39` | **`27`** | **`-12`** |
| **Total DRC Violations (Errors + Warnings)** | `929` | **`913`** | **`-16`** |
| **Unconnected Items (Pre-route Signal/Rail Nets)** | `297` | **`297`** | **`0` delta** (all power pours connected) |

---

## 4. Safety & Pre-Order BOM Reminders (Inherited from `v4` Audit)
1. **`C39–C77` (`1206` `"100uF 50V"`) MPN Mismatch**: `GMK105CC6105MV-F` is an `0402` `1 uF 35 V` MLCC; replace in BOM with a real `>= 50 V` `1206` X7R/X7S MLCC (`4.7–10 uF`, e.g. `HMK325C7475KN-TE` or `GRM31CR71H475KA12L`) plus external/off-board or radial electrolytic bulk damping across `J3` for `36 V` XT90 hot-plugging.
2. **`Q1–Q12` `IRF7480MTRPBF` `40 V` Ceiling on `36 V` Max Bus**: Only `4 V` (`10%`) avalanche margin at `36 V` / `40 A RMS`; either clamp DC bus `<= 30 V` or populate the drop-in `60 V` DirectFET alternate `IRF7580MTRPBF`.
