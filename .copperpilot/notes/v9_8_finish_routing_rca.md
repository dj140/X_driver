# `bldc_motor_cntroller_v9_8` Finish-Routing RCA & Options

## Status
- **Primary (`bldc_motor_cntroller_v9_8/`)**: Untouched (`8` clearance errors, `121` unconnected items, `0` parity errors, `0` overlaps).
- **Staged Candidate (`.copperpilot/tmp/staging/v9_8_finish/candidate/bldc_motor_cntroller_v9_8/`)**: Reached the **12-run per-board FreeRouting cap** after completing `USB_J4_DN`, `USB_CC1/2`, `Net-(F1-Pad1)`, `Net-(D2-K)` + `Net-(U3-HO)` (after rotating `C52` 180° to uncross `HB`/`HS`), `Net-(U2-DC_CAL)`, `VBUS_S`, and `AUX_TEMP`.
- **Staged DRC**: `5` minor clearance errors (`0.1570–0.1790 mm` vs `0.1600/0.1800 mm`: `4` on `OVP_IN_LI` at `U11`/`C136`, `1` on `USB_J4_DN` at `J4.A6`), `0` schematic parity errors, `0` courtyard overlaps, `121` unconnected items (`64` `GND`, `29` `+3.3V`, `28` signal/supply).

## Root-Cause Breakdown of Remaining `121` Unconnected Items

| Bucket | Count | Exact Nets | Blocking Copper / Cause |
|---|---|---|---|
| Plane-tie SMD pads | `93` | `GND` (`64`), `+3.3V` (`29`) | Local `F.Cu` pad-to-via dogbones into `In1.Cu` (`GND`) and `In2.Cu` (`+3.3V`) deferred until all signal/supply routes complete |
| Supply rails (`0.30/0.50 mm` into `0.50 mm`-pitch pins) | `19` | `+3.3VA` (`9`), `+5V` (`6`), `GVDD` (`2`), `VDC` (`2`) | `Supply` (`0.30 mm` width, `0.18 mm` clearance) entering `0.50 mm`-pitch `U1`/`U2` pads (`0.3048 mm` pad) leaves only `0.0176 mm` margin (caused `0.1787 mm` vs `0.1800 mm` DRC flapping on `U1.14/U1.15`); `+3.3VA` and `+5V` span all 4 quadrants across dense `F.Cu`/`B.Cu` traffic |
| Upper-board digital signals | `4` | `GPIO_4`, `GPIO_7`, `DEBUG_SWCLK`, `ENC0_Z` | Timed out in Pass 0 when bundled 6-at-a-time (`total_passes: 0, final_unrouted: 5` at 120 s); need 1–2 net groups or additional routing layer |
| Local pin-entry / pour taps | `5` | `USB_J4_DP` (`J4.A6`), `/Motor_Driver2/nOCTW` (`U2.5`), `/Microcontroller Interface/nFAULT` (`U2.6`), `/Motor Driver/SH_C` (`C15.1`), `/Power Management/HS` (`C52.2`) | `J4.A6` interleaved on `0.50 mm` column with `USB` `0.18 mm` clearance (`0.1790 mm` actual); `U2.5`/`U2.6` boxed by `R39`/`R40` north of `U2`; `SH_C`/`HS` pour polygons slow FreeRouting triangulation |

## Decision Options (DFM-Backed for JLCPCB `2 oz` Outer / `1 oz` Inner)

1. **6-layer stackup (`JLC06161H-3313` / 6L `2 oz` outer, `1 oz` inner)**: Adds two dedicated inner signal layers (`In3.Cu`/`In4.Cu`, `0.127 mm` min trace/space on `1 oz`), keeping `In1.Cu` `GND` and `In2.Cu` `VDC`/`+3.3V` completely unbroken and resolving all cross-board congestion (`+3.3VA`, `+5V`, `GPIO`/`SWD`/`ENC0_Z`) cleanly without relaxing clearances.
2. **Keep 4 layers + authorize `Supply` pad-entry width neck-down to `0.25 mm` and `USB` clearance to `0.16 mm` (still `>= 0.15 mm` JLCPCB `70 µm` outer minimum) + shift `R39`/`R40` (`U2.5/6`) and `U8` (`+1.5 mm` East)**: Clears the `0.50 mm`-pitch `U1`/`U2`/`J4` pad-entry pinches and runs one fresh budgeted pass for the `28` signal/supply items and `93` `GND`/`+3.3V` plane ties.
3. **Keep 4 layers & all current rules unchanged + promote staged improvements or stop here**: Keep `bldc_motor_cntroller_v9_8` at current rules and finish the remaining `28` signal/supply items + `93` plane ties manually in KiCad (or in a separate targeted routing pass).
