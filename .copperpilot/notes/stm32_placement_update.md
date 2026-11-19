# STM32 (`U6`) Optimal Single-Sided Placement Update

## Overview
- **Target File**: `bldc_motor_cntroller/bldc_motor_cntroller.kicad_pcb` (SHA-256 `02e37eea7993ac575f5557b33cb2126e3536616485132cfc7c236ab81a35a0ad`)
- **Assembly Side**: Single-sided (`240 / 240` footprints on `F.Cu`, `0` on `B.Cu`).
- **Geometric Rationale**:
  - Moving `U1` (`106.0, 73.3`) and `U2` (`44.0, 73.3`) down by `+11.3 mm` (to shorten the gate-drive loops to the `y = 89.5 mm` MOSFET row) and relocating the brake chopper (`U3`/`Q13`/`Q14`) down to `J3` opened the central vertical band (`y = 44..68 mm`).
  - Shifting `U6` (`STM32F405RGTx`) and its local crystal/decoupling cluster down by `+11.0 mm` from `(75.0, 37.0)` to `(75.0, 48.0)`:
    1. Restores the symmetric `40.01 mm` (`|dx| = 31.0 mm`, `|dy| = 25.3 mm`) equidistant spacing from `U6` to both `U1` and `U2` (matching the original `39.8 mm` distance).
    2. Centers `U6` vertically between the top JST-SH connector passives (`y = 25.5 mm`) and the DRV8301 control pads (`y = 69.48 mm`), opening a `13.5 mm` routing corridor above `U6` (`y = 26.0..39.5 mm`) and shortening the 31 southbound motor-control, SPI, current-sense, and thermistor nets by `~11.0 mm` each (`~165 mm` net ratsnest reduction).
    3. Maintains `> 27.5 mm` separation from `U3` (`73.5, 75.5`) and `> 35.5 mm` separation from the `HS` switching node (`Q13`/`Q14` at `y = 83.5..89.5 mm`).

## Updated Coordinates (`F.Cu`)

| Reference | Part / Value | Previous `(x, y, rot)` | New `(x, y, rot)` | Function |
|---|---|---|---|---|
| `U6` | `STM32F405RGTx` (`LQFP-64`) | `(75.0, 37.0, 0°)` | `(75.0, 48.0, 0°)` | Main MCU |
| `Y1` | `CSTCE8M00G55-R0` | `(63.5, 37.0, -90°)` | `(63.5, 48.0, -90°)` | HSE Crystal (`PC3`/`PC4`) |
| `C83` | `12pF` | `(63.5, 33.5, 0°)` | `(63.5, 44.5, 0°)` | Crystal Load Cap |
| `C84` | `12pF` | `(63.5, 40.5, 0°)` | `(63.5, 51.5, 0°)` | Crystal Load Cap |
| `C85` | `100nF` | `(66.0, 42.5, -90°)` | `(66.0, 53.5, -90°)` | `+3.3V` Decoupling (Left) |
| `C86` | `100nF 16V` | `(66.0, 44.5, 180°)` | `(66.0, 55.5, 180°)` | `NRST` Filter Cap |
| `C87` | `100nF` | `(70.0, 28.5, -90°)` | `(70.0, 39.5, -90°)` | `+3.3V` Decoupling (Top-Left) |
| `C89` | `100nF` | `(72.5, 28.5, 0°)` | `(72.5, 39.5, 0°)` | `+3.3V` Decoupling (Top) |
| `C91` | `100nF` | `(81.0, 29.5, 0°)` | `(81.0, 40.5, 0°)` | `+3.3V` Decoupling (Top-Right) |
| `C90` | `2.2uF 16V` | `(84.0, 36.0, -90°)` | `(84.0, 47.0, -90°)` | `VCAP_2` (`PH1`) |
| `C82` | `100nF` | `(71.0, 46.5, -90°)` | `(71.0, 57.5, -90°)` | `+3.3V` Decoupling (Bottom-Left) |
| `C88` | `2.2uF 16V` | `(73.5, 46.5, -90°)` | `(73.5, 57.5, -90°)` | `VCAP_1` (`PH0`) |
| `C92` | `100nF` | `(76.5, 46.5, -90°)` | `(76.5, 57.5, -90°)` | `+3.3VA` Decoupling |
| `C93` | `1uF 25V` | `(79.0, 46.5, -90°)` | `(79.0, 57.5, -90°)` | `+3.3VA` Bulk Decoupling |
| `TP2` | `TestPoint` | `(81.5, 48.0, 0°)` | `(81.5, 57.5, 0°)` | `+3.3V` Test Point |
| `TP3` | `TestPoint` | `(84.0, 48.0, 0°)` | `(84.0, 57.5, 0°)` | `+3.3VA` Test Point |
| `D3` | `GREEN` LED | `(81.5, 56.0, 0°)` | `(84.0, 51.5, 0°)` | `+3.3V` Status LED |
| `R50` | `1k` | `(81.5, 58.0, 0°)` | `(84.0, 53.5, 0°)` | `+3.3V` LED Resistor |

## Verification Summary
- **Courtyard & Boundary Overlaps (`query_design(what="overlaps")`)**: `0` courtyard overlaps, `0` out-of-board footprints.
- **DRC (`run_drc`)**: `0` new DRC errors or warnings relative to baseline (`659` errors / `578` warnings / `499` unconnected items on the unrouted board).
