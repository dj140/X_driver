# v9_13 Finish Routing Pass — Status & Root-Cause Analysis

- **Promoted primary (`bldc_motor_cntroller_v9_13/`):** Git checkpoint `12b1fdd` (`56` unconnected items across `25` nets, `0` courtyard/outline overlaps, `1,552` segments, `658` vias, `124` zones).
- **Staged candidate (`.copperpilot/tmp/staging/v9_13_finish/candidate/bldc_motor_cntroller_v9_13/`):** Reached the **12-run per-board FreeRouting cap** at **`50` unconnected items** (`-6` from `12b1fdd`, `-11` from `10f17f2`), `1,599` segments (`F.Cu`: `1,232`, `B.Cu`: `241`, `In2.Cu`: `126`, `In1.Cu`: `0`), `664` vias, `125` refilled zones (including restored `In2_VDC_Track_Keepout` with `0` `items_not_allowed` errors), `0` courtyard/outline overlaps, `7` unchanged minor `0.1595–0.1790 mm` clearance errors, `8` `via_dangling`, `23` `track_dangling`, and `145` pre-existing `1210` footprint-prefix/MPN schematic-parity warnings.

## Completed in Staged `v9_13_finish`

| Run | Group | Elapsed | Outcome |
|---|---|---:|---|
| 1 | `USB_DP`, `DEBUG_SWDIO` (`F.Cu`/`B.Cu`) | 65.1 s | Blocked at `U9.45/46` by locked `USB_DN` / `VCAP_2` |
| 2–3 | `SPI_SCK`, `nFAULT` | 212.9 s | Partial `nFAULT` (`+12` `F.Cu`, `+4` `In2.Cu`, `+2` vias, `0` new errors) |
| 4 | `M0_SO1`, `ENC1_Z`, `GPIO_2`, `GPIO_3` | 94.7 s | Partial (`+2` `F.Cu`, `0` new errors); boxed in by `GPIO_1` / `M0_SO2` |
| 5 | `OVP_IN_HI`, `OVP_IN_LI`, `/Power Management/HS` | 82.0 s | Blocked at `U9.29/30` by locked `GPIO_6` / `VCAP_1` |
| 6 | `+3.3V`, `+5V` | 76.3 s | Reduced `+3.3V` (`+2` `F.Cu`, `+1` via, `0` new errors) |
| 7 | `+3.3VA`, `GVDD` | 83.8 s | Added `+7` `F.Cu`, `+7` `In2.Cu`, `+1` via (`0` new errors) |
| 8 | `U7/U8` `GH_B`, `SH_C`, `SL_B`, `SL_C` | 83.0 s | **`/Motor Driver/GH_B` 100% routed** (`+10` `F.Cu`, `+3` `B.Cu`, `+2` vias, `0` new errors) |
| 9 | `VDC` driver/bypass taps | 97.6 s | Blocked by `U7`/`U8` south-pin gate traces (`0` new errors) |
| 10 | Co-route `SPI_SCK`, `nFAULT`, `GPIO_7`, `GPIO_8` | 117.6 s | **`nFAULT`, `GPIO_7`, `GPIO_8` 100% routed** (`+33` `F.Cu`, `+17` `In2.Cu`, `+8` vias, `0` new errors) |
| 11 | Co-route `GPIO_1`, `GPIO_2`, `GPIO_3`, `ENC1_Z` | 107.1 s | Reverted to pre-Run-11 checkpoint (`GPIO_1` regressed) |
| 12 | Co-route `OVP_IN_HI`, `OVP_IN_LI`, `GPIO_6` | 143.0 s | Reverted (`1` new DRC error); restored pre-Run-11 checkpoint |

## Remaining 50 Unconnected Items by Root Cause

| Category | Count | Nets / Locations | Primary Obstacle |
|---|---:|---|---|
| `U9` (STM32) `0.50 mm`-pitch pad box-in | 12 | `USB_DP` (1), `DEBUG_SWDIO` (1), `SPI_SCK` (2), `M0_SO1` (2), `ENC1_Z` (1), `GPIO_2` (1), `GPIO_3` (1), `OVP_IN_HI` (1), `OVP_IN_LI` (1), `USB_J4_DN` (1) | Locked neighbor tracks at `0.50 mm` pitch (`USB_DN`/`VCAP_2`, `SPI_MISO`, `GPIO_1`/`M0_SO2`, `GPIO_6`/`VCAP_1`) + `0.18 mm` clearance pinch (`J5.A7` = `0.179 mm`) |
| `U7`/`U8` (`DRV8301`) south-pin & `VDC` taps | 12 | `VDC` (`U7.29/C63`, `U8.29/C108`, `U7.53-54/C68/R1`, 7), `U7.39` `SL_B` (1), `Q7` `SH_C` (1), `U8.36` `SH_C` (1), `U8.39` `SL_B` (1), `U8.34` `SL_C` (1) | Locked `GH_x`/`GL_x`/`BST_x` fanout tracks filling the `F.Cu` corridor south of `U7`/`U8` |
| Supply rails (`+3.3V`, `+3.3VA`, `GVDD`, `+5V`) | 18 | `+3.3V` (9), `+3.3VA` (4), `GVDD` (3), `+5V` (2) | `Supply` `0.30 mm` width + `0.18 mm` clearance (`0.66 mm` throat) cannot squeeze past locked `0.50 mm`-pitch IC neighbors (`U7.13`, `U8.13`, `U9.19`, `U9.13`) |
| Pour islands / layer ties | 8 | `GND` `F.Cu` priority-0 islands (5), `SL_C` `C_HF3`/`C_HF6` `F.Cu` islands (2), `/Power Management/HS` `F.Cu`-`B.Cu` tie (1) | Fragmented `F.Cu` priority-0 `GND` fill (`remove_islands=0`) and `SL_C` gate-track splits |

## Protected-Lever / Structural Options to Reach 0 Unconnected

1. **Promote staged `v9_13_finish` (`50` unconnected, `0` overlaps) now** and leave the remaining 50 local connections for interactive push-and-shove finishing in KiCad.
2. **Promote staged `v9_13_finish` + relax `0.50 mm`-pitch pad-entry rules (requires approval):** Lower `Supply` pad-entry width `0.30 -> 0.20 mm` and `USB`/`Supply`/`Gate_Drv` clearance `0.18 -> 0.15 mm` (JLCPCB `2 oz` outer minimum, clearing the `7` minor `0.1595–0.1790 mm` clearance errors as well), plus enable `remove_islands=below_area_limit` on the `F.Cu` priority-0 `GND` pour, then run a fresh pass.
3. **Promote staged `v9_13_finish` + upgrade stackup to 6 layers (requires approval):** Adds two inner signal layers (`In2.Cu`/`In3.Cu`), giving clean escape capacity for `U9` and `U7`/`U8` without relaxing `0.18 mm` clearances.
