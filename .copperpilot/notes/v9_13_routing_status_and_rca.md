# v9_13 Promotion & Routing Status / RCA

- **Promoted primary (`bldc_motor_cntroller_v9_13/`):** Git checkpoint `10f17f2` (`0` ERC errors, `0` overlaps, `61` unconnected items, `5` minor clearance errors; `bldc_motor_cntroller_v9_12/` untouched).
- **Staged routing candidate (`.copperpilot/tmp/staging/v9_13_complete/candidate/bldc_motor_cntroller_v9_13/`):** Reached the 12-run per-board FreeRouting cap with `51` unconnected items (`-10` from promoted `v9_13`, `-20` from `v9_12`), `1,648` segments (`F.Cu`: `1,227`, `B.Cu`: `276`, `In2.Cu`: `145`, `In1.Cu`: `0`), `677` vias, `124` refilled zones, `0` courtyard/outline overlaps, `6` minor clearance errors (`0.1513–0.1790 mm`), `9` `via_dangling` (down from `19`), and `145` pre-existing `1210` footprint-prefix/MPN schematic-parity warnings.

## Completed in Staged `v9_13_complete`

| Item | Result |
|---|---|
| `USB_J4_DP` / `USB_J4_DN` / `USB_DP` | `USB_J4_DP` routed (`1.98 mm` skew vs `USB_J4_DN`); `USB_DP/DN` skew `7.60 mm` (`USB_DP` `U9.45` and `USB_J4_DN` `J5.A7` still pinched by `0.179 mm` pad-entry clearance) |
| `DEBUG_SWCLK` + `GPIO_7` co-route | `DEBUG_SWCLK` 100% routed (`0` new errors); `GPIO_7` still blocked at `U9.50` by `SPI_SCK` |
| `+3.3V` (`r10_v33`) | Reduced `15 -> 7` unconnected items (`+16` `F.Cu`, `+2` `In2.Cu`, `+4` vias, `0` new errors) |
| `OVP_IN_HI` / `OVP_IN_LI` | Local Upper-East legs routed; cross-board `U9.29/30` exits blocked by `GPIO_6`/`VCAP_1`/`M1_BH` |
| Stitching vias | Added `2x` `GND` (`(68.82, 67.70)`, `(138.69, 56.24)`) and `2x` `VDC` (`(32.75, 84.55)`, `(75.75, 82.95)`) vias |

## Remaining 51 Unconnected Items & Root Causes

| Cluster | Open Nets | Count | Blocking Obstacle / Root Cause |
|---|---|---|---|
| `U7` (M0 DRV8301) | `GH_B`, `SH_C`, `SL_B`, `SL_C` (zone split), `VSENSE`, `VDC` (`U7.29/53/54`, `C63`) | 9 | Locked neighbor vias `1.1–1.2 mm` directly in front of `0.50 mm`-pitch pads (`GL_B` via at `170.92, 64.45`, `PWRGD` via at `178.48, 56.78`) |
| `U8` (M1 DRV8301) | `SH_C`, `SL_B`, `SL_C` (pad + zone split), `nOCTW`, `VDC` (`U8.29`, `C108`) | 8 | Locked `GL_C`/`GH_C` vias (`50.98/51.78, 64.45`) and `nFAULT`/`SPI_MISO` north tracks (`y = 54.8`) |
| `U9` (STM32F405) | `M0_SO1`, `ENC1_Z`, `GPIO_2`, `GPIO_7`, `OVP_IN_HI`, `OVP_IN_LI`, `USB_DP` | 8 | Locked neighbor vias/tracks at `U9` perimeter (`GPIO_1/3` vias at `102.77/103.31`, `SPI_SCK` north of `U9.50`, `GPIO_6`/`M1_BH` south of `U9.29/30`) |
| Supply rails | `+3.3V` (7), `+3.3VA` (5), `GVDD` (4), `+5V` (2), `VDC` (1 island) | 19 | Tight `0.30/0.50 mm` pad-entry throats (`U7.13`, `U8.13`, `C148/149`, `U3`) and `~90 s` FreeRouting DSN load overhead per run |
| USB / Brake / Pour splits | `USB_J4_DN` (1), `/Power Management/HS` (1), `GND` F.Cu slivers (4), `SL_C` corner slivers (2 — counted above) | 7 | `J5.A7` `0.179 mm` pad clearance pinch (`USB` `0.18 mm` rule); `F.Cu` `GND`/`SL_C` sliver islands needing local vias or zone-trim |

## Remaining 6 Physical Clearance Errors (`0.1513–0.1790 mm` vs `0.1600/0.1800 mm`)

| Ref / Location | Nets | Actual vs Required |
|---|---|---|
| `U7.5` `(177.75, 55.68)` | `nFAULT` vs `nOCTW` | `0.1513 mm` vs `0.1600 mm` |
| `J5.A7` `(10.55, 36.25)` | `USB_J4_DP` vs `USB_J4_DN` | `0.1790 mm` vs `0.1800 mm` |
| `TH5.2` `(43.99, 55.50)` | `+3.3VA` vs `M1_TEMP` | `0.1720 mm` vs `0.1800 mm` |
| `TH2.2` `(162.01, 55.50)` | `+3.3VA` vs `TEMP_SENSE_2` | `0.1770 mm` vs `0.1800 mm` |
| `C68.1` `(180.40, 67.09)` | `Net-(D6-K)` vs `VDC` | `0.1770 mm` vs `0.1800 mm` |
| `U3.2` `(132.00, 48.60)` | `+5V` vs `GND` | `0.1595 mm` vs `0.1800 mm` |

## Options Forward

1. **Promote staged `v9_13` (`51` unconnected) and run a targeted co-route pass:** Unroute the `~8` specific blocking neighbor nets at `U7`, `U8`, and `U9` so FreeRouting can co-route each IC edge cleanly, and stitch/trim the `4` `F.Cu` `GND` + `2` `SL_C` pour slivers.
2. **Promote staged `v9_13` (`51` unconnected) and stop:** Inspect or hand-finish the remaining `51` connections and `6` minor clearances in KiCad.
3. **Keep `bldc_motor_cntroller_v9_13/` at `10f17f2` (`61` unconnected)** and discard the staged pass.
