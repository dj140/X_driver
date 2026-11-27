# `bldc_motor_cntroller_v9_9` `In2.Cu`-Focused Routing Summary & RCA

## Verified Progress (Staged Candidate, 12/12 FreeRouting Runs)
- **Staged Candidate**: `.copperpilot/tmp/staging/v9_9_in2_route/candidate/bldc_motor_cntroller_v9_9/bldc_motor_cntroller_v9_9.kicad_pcb` (`bldc_motor_cntroller_v9_9/` primary untouched pending decision).
- **Copper & Planes**:
  - `In2.Cu` routed segments more than doubled: **`52 -> 107`** (`+55` `In2.Cu` segments across upper `y = 15.6..61.5 mm`; `+3.3V` zone refilled cleanly around all `In2.Cu` tracks).
  - `In1.Cu` (`GND`) and lower `In2.Cu` (`VDC`, `y >= 61.8 mm`, East `y >= 54.8 mm`) remained **100% unbroken** (`0` signal tracks).
  - Board totals: `1,565` segments (`F.Cu`: `1,165`, `B.Cu`: `293`, `In2.Cu`: `107`), `671` vias, `107` refilled zones.
- **Connectivity Improvement (`121 -> 84` unconnected items, `-37` closed)**:
  - **`+3.3VA`**: `9 -> 0` (**100% routed** via upper `In2.Cu`, `+25` `In2.Cu` segments, `0` new errors).
  - **`/Microcontroller Interface/nFAULT`**: `1 -> 0` (**100% routed** via upper `In2.Cu`, `+17` `In2.Cu` segments, `0` new errors).
  - **`+5V`**: `6 -> 1` (`+13` `In2.Cu` segments; `U4`, `U5`, `U8`, `J9`, `J10`, `J11`, `D4`, `C49`, `C50`, `TP1` connected; only `R6.2` remains).
  - **`+3.3V` plane ties**: `29 -> 8` (`+22` vias into `In2.Cu` `+3.3V`, `0` new errors).
- **DRC & Geometry (`run_drc` + `query_design(what="overlaps")`)**:
  - `0` schematic-parity errors, `0` courtyard/outline overlaps, `0` `zones_intersect` errors.
  - `7` minor clearance errors (`0.1570–0.1790 mm` vs `0.1600/0.1800 mm`: `4` on `OVP_IN_LI` at `U11`/`C136`, `1` on `USB_J4_DN` at `J4.A6`, `2` on `+5V` at `U4.2`/`U5.5`).

## Remaining `84` Unconnected Items & Root Cause

| Bucket | Count | Exact Nets | Root Cause / Blocking Copper |
|---|---|---|---|
| Plane ties | `71` | `GND` (`63`), `+3.3V` (`8`) | Local `F.Cu` pad-to-via dogbones into `In1.Cu` (`GND`) and `In2.Cu` (`+3.3V`); `GND` timed out at `63 -> 57` when routed all at once due to full-board plane triangulation |
| Trapped `U6` `F.Cu` pin exits | `4` | `GPIO_4`, `GPIO_7`, `DEBUG_SWCLK`, `ENC0_Z` | `U6.17` (`GPIO_4`) boxed by `F.Cu` `GND` stub at `y = 51.14`; `U6.49/50` (`SWCLK`/`GPIO_7`) boxed `1.05 mm` north by `F.Cu` `SPI_SCK`/`SPI_MISO`; must unroute those blocking `F.Cu` segments and re-route them on `In2.Cu` together |
| `0.50 mm`-pitch `Supply` / `VDC` / `+5V` pinches | `5` | `GVDD` (`2`: `U1.13`, `U2.13`), `VDC` (`2`: `R66.1`, `C36.1`), `+5V` (`1`: `R6.2`) | `Supply` (`0.30 mm` width, `0.18 mm` clearance) and `Supply_5V` (`0.50 mm` width) leave minimal pad-entry margin at `U1`/`U2` (`0.50 mm` pitch) and `R6.2` |
| Local taps | `4` | `/Motor_Driver2/nOCTW` (`U2.5`), `USB_J4_DP` (`J4.A6`), `/Motor Driver/SH_C` (`C15.1`), `/Power Management/HS` (zone tie) | `nOCTW` open once `nFAULT` moved to `In2.Cu` (needs 1 run); `J4.A6` interleaved on `0.50 mm` column with `USB` `0.18 mm` clearance; `SH_C`/`HS` pour taps |

## Options
1. **Promote staged `v9_9` as-is**: Save the `121 -> 84` (`+55` `In2.Cu` tracks, 100% `+3.3VA` and `nFAULT`) progress into `bldc_motor_cntroller_v9_9/` now.
2. **Promote `v9_9` + continue another `In2.Cu` pass (unrouting the `F.Cu` `SPI_SCK`/`SPI_MISO`/`GND` blockers at `U6` + routing `nOCTW`, `R6.2`, `U6` signals, and `GND`/`+3.3V` ties)**: Keeps 4 layers and all current design rules unchanged.
3. **Authorize `Supply` pad-entry width `0.25 mm` & `USB` clearance `0.16 mm` (both `>= 0.15 mm` JLCPCB `2 oz` outer min) + continue**: Unblocks `GVDD` (`U1.13`/`U2.13`), `U4`/`U5` `+5V` clearance, and `J4.A6` `USB_J4_DP`.
4. **Switch to 6 layers (`JLC06161H-3313`, `2 oz` outer / `1 oz` inner)**: Adds two dedicated `1 oz` (`0.127 mm` min) inner signal layers so all planes remain completely solid.
