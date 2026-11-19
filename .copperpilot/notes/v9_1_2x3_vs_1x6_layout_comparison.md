# 2x3 Stacked Rows vs. 1x6 Single Row for `DirectFET_L8` (`IRF7759L2TRPBF`) on `v9.1`

## 1. Why the Original Board (`fa25dca`) Used `2x3`

In the original `bldc_motor_cntroller` (`fa25dca`) and `ODrive` layouts, `Q1-Q12` used single-ended `5 x 6 mm` `MG-WDSON-8` / `TDSON-8` MOSFETs (one Drain tab on one edge, Source + Gate on the opposite edge) combined with **double-sided assembly**:
- `Q1-Q6` (and `Q7-Q12`) were stacked in two rows (`y = 82.35 mm` LS, `y = 88.35 mm` HS) across just `16.6 mm` center-to-center width (`22.6 mm` courtyard span).
- `2512` shunts (`R12, R16, R32, R36`) and half of the `1206` bulk capacitors (`C39, C40, C61, C64`) were mounted on **`B.Cu` directly underneath the LS FET row** (`y = 82.3 mm`).

Upgrading to **`Package_DirectFET:DirectFET_L8`** (`9.15 x 7.10 mm` body, `10.60 x 7.46 mm` courtyard) on a **single-sided (`F.Cu`)** board with **`0.11 mm` `F.Cu`-to-`In1.Cu` (`GND`) prepreg and `1.17 mm` core** changes the package geometry and return-loop physics fundamentally:
- **Dual-End Drain Flanges**: `Pad 1` (Drain) sits at **both** ends of the can (`-4.50 mm` and `+4.50 mm`, `6` pads total, `(duplicate_pad_numbers_are_jumpers no)`), trapping `Pad 3` (Source, `8` pads) and `Pad 2` (Gate, offset at `-2.25 mm`) in the center so they can only exit laterally.
- **Top-Side Fast Loop Requirement**: Because `In1.Cu` (`GND`) is `0.11 mm` beneath `F.Cu` while `In2.Cu` (`VDC`) is `1.28 mm` beneath `F.Cu`, `B.Cu` only shares DC current; the fast switching commutation loop (`C_VDC -> HS_D -> HS_S/LS_D -> LS_S -> In1.Cu GND`) must stay tight on `F.Cu` over unperforated `In1.Cu`.

---

## 2. Quantitative Comparison (`v9.1` `180 x 115 mm`, Single-Sided `F.Cu`)

| Metric | `1x6` Single Row (Current `v9.1`) | `1x6` + `U1/U2` Shifted `-5 mm` Y (Recommended Tweak) | `2x3` Vertical Cans (`rot = +/-90 deg`, HS over LS) | `2x3` Horizontal Cans (`rot = 0/180 deg`, HS over LS) |
|---|---|---|---|---|
| **3-Phase Channel X-Width** | `53.7 mm` (`x = 113.1..166.7`) | `53.7 mm` (`x = 113.1..166.7`) | **`29.5-32.5 mm`** (`3` cols @ `11-12 mm` pitch) | **`34.6-37.6 mm`** (`3` cols @ `12-13.5 mm` pitch) |
| **Power-Stage Y-Depth (Caps to Shunts)** | **`27.0 mm`** (`y = 81.3..108.3`) | **`27.0 mm`** (`y = 81.3..108.3`) | `40.0 mm` (`y = 76.3..116.3`) | `34.5 mm` (`y = 81.3..115.8`) |
| **Fast `F.Cu` Commutation Loop Path** | **`~9-12 mm`** side-by-side HS/LS (`<= 2.5 mm` at `C_HF1-6`) | **`~9-12 mm`** side-by-side HS/LS (`<= 2.5 mm` at `C_HF1-6`) | `~32-37 mm` vertical (`C_VDC -> HS -> LS -> Shunt -> GND`) | `~28-33 mm` vertical (`C_VDC -> HS -> LS -> Shunt -> GND`) |
| **Zero-Via `F.Cu` Gate Escape (`Q1-Q12`)** | **Yes (`12/12` FETs)** — `5 mm` straight North into `R_gate` | **Yes (`12/12` FETs)** — `5 mm` straight North into `R_gate` | Partial — `3` LS gates must thread `20 mm` between switching HS FETs | **No** — bridging both HS Drain ends on `F.Cu` rings HS Gate `360 deg` (`VDC` + `SH_x`), forcing gate vias |
| **`In1.Cu` `GND` Solidity Under FETs** | **`99.95%`** (`0` `VDC`/`SH`/`SL` vias in `y = 86..97.5`) | **`99.95%`** (`0` `VDC`/`SH`/`SL` vias in `y = 86..97.5`) | Degraded (`~85-90%`) — HS South Drain (`VDC`) is trapped above LS (`SH_x`), forcing mid-bridge `VDC` vias through `In1.Cu` | **`~92-95%`** — gate vias & inter-row transitions perforate `In1.Cu` between HS and LS |
| **Max `DRV8301` -> `R_gate` Fanout** | `26-29 mm` (`1.2 mm` cramped gap above `VDC` bar) | `24-27 mm` (**`6.2 mm` open `F.Cu`/`B.Cu` fanout highway**) | **`13-16 mm`** (`GH_x`), `22-25 mm` (`GL_x` past HS row) | `14-18 mm` (`GH_x`), `20-24 mm` (`GL_x` with vias) |
| **Inline `2512` Shunt Path (`SL_B`, `SL_C`)** | **`5 mm` straight South** under `Q4/Q6` (`0` crossings) | **`5 mm` straight South** under `Q4/Q6` (`0` crossings) | **`5 mm` straight South** under LS cols B/C (`0` crossings) | **`5 mm` straight South** under LS cols B/C (`0` crossings) |
| **Thermal Footprint per 6-FET Bridge** | **`~54 x 11 mm` (`594 mm^2`)** — zero upstream FET heating | **`~54 x 11 mm` (`594 mm^2`)** — zero upstream FET heating | `~31 x 23 mm` (`713 mm^2` box, HS/LS thermally coupled) | `~36 x 17.5 mm` (`630 mm^2` box, HS/LS thermally coupled) |

---

## 3. Core Engineering Tradeoff

1. **Where `2x3` Wins**:
   - Cuts horizontal channel width by **`~40%`** (`~31 mm` vs. `53.7 mm`), aligning the 3 phase columns directly above the 3 pins of `J1`/`J2` (`MR60PB-M`) and halving the lateral distance from `U1`/`U2` (`DRV8301`) to the outer phase columns.
   - If the primary goal were shrinking the board width back down from `180 mm` toward `~145-150 mm`, `2x3` (vertical cans) is the right geometry.

2. **Where `2x3` Loses Specifically with `DirectFET_L8` on Single-Sided `F.Cu`**:
   - **Trapped Mid-Bridge `VDC` Flange (`In1.Cu` Perforation)**: In `2x3` vertical cans, each HS FET's South Drain flange (`VDC`) sits trapped between HS Source (`SH_x`) and LS North Drain (`SH_x`). Connecting that `VDC` flange requires dropping `VDC` vias right between HS and LS — punching antipads into `In1.Cu` (`GND`) directly under the highest-`di/dt` switching loop (re-creating Fault #3).
   - **Gate-Ring Trap in Horizontal `2x3`**: Rotating the cans `90 deg` so `VDC` bridges across the top on `F.Cu` traps the HS Gate pad (`Pad 2`) inside a closed `F.Cu` ring of `VDC` (North/West) and `SH_x` (East/South), forcing vias into the MOSFET gate path.
   - **`2.5x` Longer `F.Cu` Switching Loop & `dV/dt` Gate Coupling**: Stacking HS above LS plus single-sided `2512` shunts below LS stretches the `F.Cu` high-frequency commutation path to `~32-37 mm` and forces low-side gate traces (`GL_A/B/C`) to run `~20 mm` through `3.5 mm` slots right beside the switching HS FET cans.

3. **Why Current `1x6` Felt Tight Around `U1`/`U2` — and the Low-Risk Fix**:
   - On `v9.1` (`180 x 115 mm`), the `53.7 mm` `1x6` width already fits with comfortable margin, preserves **`99.95%` solid `In1.Cu` `GND`**, keeps **`<= 2.5 mm` `C_HF` side-by-side half-bridge loops**, and gives **zero-via `5 mm` `F.Cu` gate stubs** on all 12 MOSFETs.
   - The only routing pinch point in Unit 4 is that `U1`/`U2` (`y = 76.45 mm`, south pads at `y = 80.1 mm`) sit just `1.2 mm` above the `F.Cu` `VDC` bus (`y = 81.3 mm`), while `y = 40..65 mm` directly North of `U1`/`U2` is empty board space.
   - Moving **`U1`/`U2` and their local driver/buck passives North by `5.0 mm` (`y = 76.45 -> 71.45 mm`)** opens a **`6.2 mm` tall horizontal fanout corridor** (`y = 75.1..81.3 mm`) above the `VDC` strips over continuous `In1.Cu` `GND`, eliminating the `GH/GL/BST/SP/SN` congestion without sacrificing `1x6` loop inductance or `In1.Cu` plane integrity.
