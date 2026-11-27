# V9.2 Symmetrical 3-Leg Power Stage & North-Edge Connector Alignment (`220 × 115 mm`)

## 1. Fixes Applied to `bldc_motor_cntroller_v9.2`

### A. Symmetrical 3-Leg Half-Bridge & Motor Connector (`J1` / `J2`) Alignment
- **Root Cause Fixed**:
  1. `AMASS_MR60PB-M_1x03_P5.50mm_Vertical` (`J1`, `J2`) anchors at `Pad 1` (`0, 0`), with `Pad 2` at `(5.5, 0)` and `Pad 3` at `(11.0, 0)`. Placing `J2` at `x = 57.0` and `J1` at `x = 175.0` (`rot = 180°`) shifted the three connector pins `-5.5 mm` West of the phase-pour centers, leaving `Pad 2` (`SH_B`) unconnected while `SH_B` and `SH_A` converged on the East leg.
  2. On the `VDC` bus side, `Q9`/`Q7` (M1) and `Q3`/`Q1` (M0) previously shared one merged `VDC` pour (`10.0 mm` center-to-center) while two `1206` bus capacitors + `C_HF5`/`C_HF2` dropped an isolated `VDC` finger with no High-Side FET attached.
- **Verified `v9.2` Geometry (`+118.00 mm` exact M1-to-M0 translation)**:

| Phase Leg | M1 FETs (`y = 92.0, -90°`) | M0 FETs (`y = 92.0, -90°`) | Dedicated `VDC` Bank (`y = 80.5`) & `C_HF` (`y = 89.5`) | Phase Trunk Width (`F.Cu + B.Cu`) | `J2` / `J1` Pin Center (`y = 123.0`) |
|---|---|---|---|---|---|
| **Phase C** | `Q12` (`19.5`), `Q11` (`32.0`) | `Q6` (`137.5`), `Q5` (`150.0`) | `5× 1206` + `100 nF` + `C_HF6` (`13.8`) / `C_HF3` (`131.8`) | `12.50 mm` (`SH_C`), `6.30 mm` (`SL_C` -> `R36`/`R16`) | `J2.3 = 51.50` / `J1.3 = 169.50` (`100%` connected) |
| **Phase B** | `Q10` (`49.5`), `Q9` (`62.0`) | `Q4` (`167.5`), `Q3` (`180.0`) | `5× 1206` + `C_HF5` (`43.5`) / `C_HF2` (`161.5`) | `12.30–12.50 mm` (`SH_B`), `6.30 mm` (`SL_B` -> `R32`/`R12`) | `J2.2 = 57.00` / `J1.2 = 175.00` (`100%` connected) |
| **Phase A** | `Q7` (`76.5`), `Q8` (`89.0`) | `Q1` (`194.5`), `Q2` (`207.0`) | `5× 1206` + `100 nF` + `C_HF4` (`94.4`) / `C_HF1` (`212.4`) | `12.50 mm` (`SH_A`) | `J2.1 = 62.50` / `J1.1 = 180.50` (`100%` connected) |

### B. North-Edge Connectors Moved to Actual North Edge (`y = 15.00 mm`)

| Reference(s) | Function / Package | Prior `Y` (mm) | New `Y` (mm) | Courtyard North Edge (mm) | SMD Pad North Edge (mm) | Clearance to `y = 15.00 mm` `Edge.Cuts` |
|---|---|---|---|---|---|---|
| `J11`, `J10` | `ENC1`, `ENC0` (`JST_SH_SM05B-SRSS-TB`, `180°`) | `20.50` | **`18.30`** | `15.020` | `15.525` (`MP` pad) | `0.525 mm` (`>= 0.50 mm` rule, `0` DRC errors) |
| `J5`, `J9`, `J6`, `J8`, `J7` | GPIO / SWD / CAN / Thermistor (`JST_SH_SMxxB-SRSS-TB`, `180°`) | `20.50` | **`18.30`** | `15.020` | `15.525` (`MP` pad) | `0.525 mm` (`>= 0.50 mm` rule, `0` DRC errors) |
| `SW1` | DFU / `BOOT0` tactile switch (`SW_SPST_B3U-1000P`, `180°`) | `20.50` | **`16.70`** | `15.050` | `15.850` | `0.850 mm` (`>= 0.50 mm` rule, `0` DRC errors) |
| `C95–C100`, `R55–R61` | Local encoder RC filters & `BOOT0` resistor | `25.50 / 29.20 / 25.00` | **`23.30 / 26.80 / 21.50`** | Inside board | Inside board | Shifted `-2.20 mm` North behind `J10`/`J11`/`SW1` |

---

## 2. Post-Promotion Verification Summary (`bldc_motor_cntroller_v9.2`)

- **Copper DRC & Parity (`run_drc`)**: `0` errors, `0` schematic-parity errors, `0` `copper_edge_clearance` errors, `0` `zones_intersect` errors, `0` `via_dangling` warnings, `0` `hole_to_hole` warnings (`391` unrouted signal/tie items remain for the signal-routing phase; `0` unconnected items on `J1`, `J2`, `C_HF1–C_HF6`, `R12`, `R16`, `R32`, `R36`, or any power/phase pour).
- **Courtyard & Boundary Audit (`query_design(what="overlaps")`)**: `0` courtyard overlaps, `0` components outside `Edge.Cuts`.
- **`In1.Cu` Commutation Return Plane Solidity**: `100.00%` solid `In1.Cu` `GND` under both FET commutation zones (`y = 85.8 .. 97.6 mm`) and within `3.5 mm` of `C_HF1–C_HF6` (`0` non-`GND` vias in the commutation zone).
- **3D Model Verification**: Top-side 3D raytraced verification completed via `kicad-cli pcb render`; per-package `review_pcb_footprint_3d_model` remains scheduled for final sign-off after signal routing.
