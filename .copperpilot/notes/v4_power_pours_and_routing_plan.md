# `bldc_motor_cntroller_v4.kicad_pcb` — Updated Placement, Power Pours, Schematic Sync & Routing Plan

- **Saved Deliverable PCB**: `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v4.kicad_pcb` (`SHA-256: ec047cd7af41a1f90d603aef72351e4e33bd0f5a93cb6468fc32ad4e2c2d4307`)
- **Untouched Baseline PCB**: `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v3.kicad_pcb` (`SHA-256: 38da45a085921cf43934d89ffa528d27dbcbc8e2a257f34ad69845726fff3071`)
- **Saved Schematic Sheets (Synced)**:
  - `/home/sam/Open_drive/bldc_motor_cntroller/io_interface.kicad_sch` (`U8` `USBLC6-2SC6` flow-through `USB_J4_DN`/`USB_J4_DP` -> `R52`/`R53` -> `USB_DN`/`USB_DP` to `U6`, plus `5.1k 1%` `0402` `CC1`/`CC2` pull-downs `R64`, `R65` `CRCW04025K10FKED`)
  - `/home/sam/Open_drive/bldc_motor_cntroller/microcontroller_interface.kicad_sch` (`U6` `VSSA` `pin 12` tied to `GND`)
  - `/home/sam/Open_drive/bldc_motor_cntroller/motor_driver.kicad_sch` (`C_HF1` `VDC–GND`, `C_HF2` `VDC–SL_B`, `C_HF3` `VDC–SL_C`, `100nF 100V` `0603` `GCM188R72A104KA64D`)
  - `/home/sam/Open_drive/bldc_motor_cntroller/motor_driver2.kicad_sch` (`C_HF4` `VDC–GND`, `C_HF5` `VDC–SL_B`, `C_HF6` `VDC–SL_C`, `100nF 100V` `0603` `GCM188R72A104KA64D`)
  - `/home/sam/Open_drive/bldc_motor_cntroller/power_management.kicad_sch` (`C_AUX1` `VDC–GND`, `100nF 100V` `0603` `GCM188R72A104KA64D`)
- **Stackup (`JLC04161H-3313` in `(stackup ...)` block)**: `2 oz` (`0.070 mm`) `F.Cu` & `B.Cu`, `1 oz` (`0.035 mm`) `In1.Cu` (`GND`) & `In2.Cu` (`VDC` for `y >= 58 mm`), `0.11 mm` `FR4 3313` outer prepregs, `1.17 mm` `FR4` core.

---

## 1. Summary of Applied Review & Netlist Fixes

| Review Finding | Applied Fix & Exact Coordinates (`M1 = M0 - 70.00 mm`) | Before -> After |
|---|---|---|
| **1. HF decoupling (`C_HF1..C_HF6`) `10.7–11 mm` from LS source (`"TBD"` `board_only`)** | Synced `C_HF1..C_HF6` (`100nF 100V` `X7R` `0603` `GCM188R72A104KA64D`) from schematic and placed straddling each half-bridge at `(95.85, 85.15)`, `(110.35, 85.15)`, `(124.85, 85.15)` (and `-70.00 mm` on M1) | HS drain dist `3.57–3.87 mm` -> **`2.79 mm`**; LS source dist `10.48–10.78 mm` -> **`3.81 mm`**; `0` `board_only` parts |
| **2. Gate paths long (`9.8–21.9 mm`) & unequal (`12.1 mm` spread), threading `100 µF` row** | Tightened leg pitch `16.75 -> 14.50 mm` (`HS–LS = 6.20 mm`), rebalanced `U1` to `(111.65, 72.00)` & `U2` to `(41.65, 72.00)`, and opened three `4.1 mm` gate channels in the `y = 81.65 mm` `1206` row | Driver-pad -> gate-resistor max `21.91 mm` -> **`17.85 mm`** (`C_HS = 17.77` vs `A_LS = 17.85 mm`, `0.08 mm` L/R symmetry); spread `12.1 mm` -> **`8.5 mm`** |
| **3. Current sense exposed (`~20+ mm` unfiltered run)** | Placed `120 Ω` source-damping resistors `R11 (114.10, 94.75)`, `R15 (99.60, 94.75)`, `R31 (44.10, 94.75)`, `R35 (29.60, 94.75)` alongside Kelvin net-ties `NT1..NT8` right above shunts while keeping `2.2 nF` differential caps `C2, C3, C23, C24` at `U1`/`U2` (`y = 78.15 mm`) | Sense pair shortened by `~3.5 mm` and RC source-terminated (`120 Ω` at shunt + `2.2 nF` differential at `DRV8301`) |
| **4. Shunts in commutation loop on Phases B & C only** | Connected `C_HF2/C_HF5` across `VDC–SL_B` and `C_HF3/C_HF6` across `VDC–SL_C` with dedicated `Priority 4` `B.Cu` return straps + `3` `0.8/0.4 mm` `SL` vias directly to `Q4/Q6/Q10/Q12` source | HF commutation loop bypasses `R12/R16/R32/R36` on Phases B & C, matching unshunted Phase A |
| **5. Shunts (`R16, R12`) & connectors (`J1, J2`) obstruct phase routes (`y ≈ 102` corridor ~`0 mm`)** | Rotated `2512` shunts horizontal (`rot = 180°`) at `y = 97.35 mm` (`R16 100.80`, `R12 115.30`, `R36 30.80`, `R32 45.30`) and moved `J1 (115.50, 106.50)`, `J2 (45.50, 106.50)`, `J3 (75.00, 106.50)` | Phase exit corridor widened from `~0 mm` to **`4.55 mm` copper (`3.12 mm` courtyard)**; unobstructed `B.Cu` `SH` mirrors |
| **6. Smaller PCB issues (`Q14` pad 5 `0` vias; `+5V` `75 mm` run; `J1–J3` `0.6 mm` edge margin; `U8` `8 mm` from `J4`)** | Added `4` `HS` vias `(76.6..78.4, 67.6..69.3)` + `B.Cu` `HS` island to `H6`; moved `U4/U5` LDO cluster to `(96.0, 49.5..54.5)`; `J1–J3` at `y = 106.50`; `U8` adjacent to `J4` at `(14.20, 36.00)` | `Q14` `HS` vias `0 -> 4`; `L1 -> U4/U5` `+5V` run `75 mm -> 31 mm`; `J1–J3` edge margin `0.56 -> 1.56 mm`; `U8 -> J4` pad dist `8.5 -> 2.55 mm` |
| **7. Netlist errors (`U8` unconnected, `J4` `CC1/CC2` unconnected, `U6` `VSSA` unconnected)** | Wired `U8` flow-through (`USB_J4_DN`/`DP` -> `R52/R53` -> `USB_DN/DP` to `U6.44/45`), added `R64 (14.20, 32.30)` & `R65 (14.20, 39.70)` (`5.1k 1%`), tied `U6.12` (`VSSA`) to `GND` | Primary schematic ERC errors `44 -> 31` (`-13` errors, `-6` warnings); all USB & `VSSA` nets valid |

---

## 2. Before (`_v3`) vs Updated (`_v4`) Power-Stage Metrics

| Metric | `_v3` Baseline | Updated `_v4` | Target / Status |
|---|---|---|---|
| `SH_A` (`HS src -> J`, `1 oz F.Cu` / `2 oz F+B+vias` @ `40 A`) | `1.99 mOhm` / `0.99 mOhm` (`1.59 W`) | `1.64 mOhm` / **`0.547 mOhm` (`0.87 W`)** | `< 1.0 W` (**PASS**) |
| `SH_B` (`HS src -> J`, `1 oz F.Cu` / `2 oz F+B+vias` @ `40 A`) | `1.97 mOhm` / `0.98 mOhm` (`1.57 W`) | `2.40 mOhm` / **`0.568 mOhm` (`0.91 W`)** | `< 1.0 W` (**PASS**) |
| `SH_C` (`HS src -> J`, `1 oz F.Cu` / `2 oz F+B+vias` @ `40 A`) | `2.56 mOhm` / `1.28 mOhm` (`2.05 W`) | `2.44 mOhm` / **`0.545 mOhm` (`0.87 W`)** | `< 1.0 W` (**PASS**) |
| `SH` Phase Balance (`A / B / C` spread, `2 oz F+B+vias`) | `29.5 %` | **`4.2 %` (`M0`), `4.8 %` (`M1`)** | `<= 10 %` (**PASS**) |
| `SH_A / B / C` (`LS drn -> J`, `2 oz F+B+vias`) | `0.57 / 0.61 / 0.91 mOhm` | **`0.320 / 0.461 / 0.446 mOhm` (`0.51–0.74 W`)** | `< 1.0 W` (**PASS**) |
| `SH_B` neck (`y = 104.5–109`) & `SH_C` neck (`y = 98–103`) | `4.70 mm` & `6.85 mm` | **`5.05 mm`** & **`12.75 mm` mean (`5.15 mm` min)** | Widened (**PASS**) |
| `SH`-to-`SH` copper gap (`F.Cu` & `B.Cu`) | `0.26–0.33 mm` | **`0.680 mm`** | `>= 0.50 mm` (**PASS**) |
| HS lower drain `pads 1,2 -> VDC vias` (`Q1,Q3,Q5,Q7,Q9,Q11`) | `5.39 sq` (`0` vias on `Q1,3,7,9`) | **`0.03 sq` (`4` `VDC` vias beside `pads 1,2` each)** | `< 1.0 sq`, `>= 3` vias (**PASS**) |
| HS upper drain `pads 9,10 -> VDC vias` | `0.54 sq` | **`0.38–0.39 sq`** | `< 1.0 sq` (**PASS**) |
| Nearest `1206` `VDC` cap to each HS drain | `3.99 mm` | **`3.86–3.92 mm` center (`2.42 mm` pad-edge)** | `< 4.0 mm` (**PASS**) |
| `C_HF1..C_HF6` distance to HS drain / LS source | N/A (`10.8 mm` to LS in rev1) | **`2.79 mm` (HS drain) / `3.81 mm` (LS source)** | Straddles leg (**PASS**) |
| LS source centroid -> nearest `GND` via (`Q4,6,10,12`) | `7.72 mm` | **`2.92 mm` (`1.88 mm` pad; `Q2/Q8 = 3.17 mm` / `2.18 mm` pad)** | `<= 3.0 mm` (**PASS**) |
| Aux `Q13` `VDC` island & vias / `Q14` `GND` vias / `C48` `GND` vias / `Q14` `HS` vias | `32.4 mm²`, `1` / `1` / `0` / `0` | **`48.05 mm²`, `10` `VDC` / `6` `Q14 GND` / `5` `C48 GND` / `4` `Q14 HS`** | `15 A` rated (**PASS**) |
| DRC Errors / Warnings / Courtyard Overlaps | `351` / `571` / `0` | **`351` (`0` new errors) / `576` (`silk_overlap 7->5`) / `0` overlaps** | `0` new errors (**PASS**) |

---

## 3. Verification & Safety Reminders Before Routing / Fab
1. **BOM Flag (`C39–C77` `1206` caps)**: Replace legacy schematic MPN `GMK105CC6105MV-F` (`0402 1 µF 35 V`) with a valid `>= 50 V` `1206` MLCC (e.g. `10 µF 50 V X7R` `GRM31CR71H106KA12L` or `4.7 µF 50 V X7S` `HMK325C7475KN-TE`) plus external/radial bulk capacitance if hot-plugging `36 V` batteries without pre-charge.
2. **MOSFET Voltage Margin (`Q1–Q12` `IRF7480MTRPBF`)**: `40 V` $V_{\text{(BR)DSS}}$ provides only `4 V` (`10 %`) margin at `36 V` max bus; populate drop-in `60 V` `IRF7580MTRPBF` if bus transients/regen can exceed `32 V`.
3. **Routing Rules (Unchanged from Step 5 + Updated Corridors)**:
   - Route gate pairs (`GH_x`/`SH_x` and `GL_x`/`SL_x`, `0.50 mm` / `0.20 mm` spacing) from `U1`/`U2` through the three `4.1 mm` wide `1206`-row corridors (`x = 96.6..100.6`, `110.8..114.8`, `125.0..129.4` on M0 and `-70 mm` on M1) with intra-leg length matching `|L(GH_x) - L(GL_x)| <= 3.0 mm` (`+2.2 mm` trombone on `GH_A`/`GL_C`).
   - Route differential Kelvin sense pairs (`SN1/SP1`, `SN2/SP2`, `0.25 mm` width / `0.20 mm` edge gap) from `R11/NT2` & `R15/NT4` (`y = 94.75 mm`) straight north on `B.Cu` (shielded outside `SH` mirrors with `GND` guard vias) up to `C2, C3, C23, C24` (`y = 78.15 mm`) -> `U1`/`U2` pins `30–33`.
   - Split `In2.Cu` cleanly at `y = 58.0 mm` (`VDC` south `y = 58.0..112.5`, `+3.3V` / `+5V` north `y = 16.0..57.2` with `>= 0.8 mm` split gap) and place return `GND` vias within `1.5 mm` of any `F.Cu <-> B.Cu` signal transition.
