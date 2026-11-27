# V9_10 Unit 5 Routing Status, 3D Audit & Root-Cause Analysis

## 1. Current Verified State
- **Promoted on disk (`bldc_motor_cntroller_v9_10/`):**
  - Units 1–2 schematics (`f3cffd3`): `0` ERC errors, `319` components (`61×` `1210` `4.7 µF 100 V` MLCCs, `12×` per-half-bridge `100 V` HF caps, `4×` `DRV8301` `VDD_SPI`/`REF` caps, `4×` `J3` `100 µF 100 V` bulk cans, `3×` USB `J4` VBUS protection/decoupling).
  - Units 3–4 PCB (`8d51170`): `0` DRC errors, `0` courtyard overlaps, `0` schematic-parity errors, `0` tracks/vias under `U6` (`[105..115, 39..49]`), `0` non-FET components inside shifted heatsink keepout (`y = 85.6..101.4 mm`).
- **Staged Unit 5 candidate (`.copperpilot/tmp/staging/v9_10_u5/candidate/bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_10.kicad_pcb`):**
  - **Group 1 (USB 90-Ohm Diff Pair, USB VBUS & U6 VCAP — 8 nets):** 100% routed on `F.Cu` over unbroken `In1.Cu` `GND` (`0` new DRC errors). `USB_DP/DN` = `120.32 / 122.56 mm` (skew `2.24 mm`, well inside USB 2.0 FS `±150 mm`); `USB_J4_DP/DN` = `9.25 / 11.24 mm` (skew `1.98 mm`).
  - **Group 2 (`Net-(Q1-G)`..`Net-(Q12-G)` — 12 nets):** All 12 `0.50 mm` MOSFET gate traces 100% zero-via routed on `F.Cu` (`0` new DRC errors).
  - **Group 3 (Kelvin Current-Sense & Net-Tie Bridges — 14 nets):** `12/14` nets routed on `F.Cu` (`0` new DRC errors; `/Motor Driver/SP2` and `/Motor_Driver2/SP2` remain open).
  - **Staged DRC & Overlaps (after zone refill):** `1,246` segments (`F.Cu`: `972`, `B.Cu`: `203`, `In2.Cu`: `71`), `580` vias, `113` refilled zones, `0` courtyard/outline overlaps, `0` schematic-parity errors, `2` minor clearance errors (`0.1538 mm` vs `0.1600 mm`, `0.1790 mm` vs `0.1800 mm`), `233` remaining `unconnected_items` across `58` nets (`109` `GND`, `15` `+3.3VA`, `12` `+3.3V`, `12` `VDC`, `4` `+5V`, `3` `GVDD`, `78` power-stage/upper-board signal taps).
  - **3D Model Alignment Audit (KiCad 10 `kicad-cli pcb render`):** `C154` (`CP_Elec_10x10.5.step`), `D8` (`D_SOD-123F.step`), and `C103` (`C_1210_3225Metric.step`) all resolve and align cleanly to their pads.

## 2. Root-Cause Analysis (12-Run FreeRouting Cap Reached)
| Blocker | Mechanism | Evidence |
|---|---|---|
| `U1`/`U2` south fanout pinch (`GH_A..GL_C`, `DVDD`, `BST`) | Placing Row 1 of the `2×5` `1210` `VDC` banks at `y = 73.60 mm` (pour north edge `y = 71.30 mm`) compressed the `U1`/`U2` south corridor (`y = 67.32..71.30 mm`) to `3.98 mm`, which holds both the `0402` bypass row (`y = 70.40 mm`), `C144`/`C152` (`y = 68.80 mm`), and `39` existing tracks/vias, leaving insufficient room for `0.60/0.30 mm` fanout vias on the 6 `0.50 mm`-pitch `GH_A..GL_C` pins. | `g4_drv_pwr` and `g4a_drv_gate` (both `--max-passes 6` and `--max-passes 4`) timed out at `150–180 s` with `0` completed passes. |
| Large multi-net upper-board & global supply batches | Group 5 (`22` nets) and Group 6 (`+5V`, `+3.3VA`, `GVDD` global supplies with pinched `U1`/`U2`/`U4`/`U5` entries) exceeded the `150 s` timeout when routed together instead of 3–5 net sub-batches. | `g5_upper_dig` and `g6_supplies` timed out at `150 s`. |

## 3. Recommended Options
1. **Shift `U1`/`U2` + local passives `2.0 mm` North (`y = 63.50 -> 61.50 mm`) and continue routing** in smaller 4–6 net batches (opens a `6.0 mm` south fanout corridor for `GH_A..GL_C` without changing any design rules or board outline).
2. **Promote staged `v9_10` as-is** (`233` unconnected items, `2` minor clearance errors, `0` parity/overlaps, USB/Q1–Q12 gates/Kelvin routed) to `bldc_motor_cntroller_v9_10/` so you can inspect or finish routing in KiCad.
3. **Shift `U1`/`U2` `2.0 mm` North + relax `Supply` pad-entry width to `0.25 mm`** (still `>= 0.15 mm` JLCPCB `2 oz` min) to clear the `0.50 mm`-pitch `GVDD`/`+5V` pinches at `U1`/`U2`/`U4`/`U5`, then continue routing.
