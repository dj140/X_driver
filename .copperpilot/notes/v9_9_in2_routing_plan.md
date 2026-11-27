# `bldc_motor_cntroller_v9_9` `In2.Cu`-Focused Routing Plan

## Scope & Constraints
- **Target**: `bldc_motor_cntroller_v9_9/bldc_motor_cntroller_v9_9.kicad_pcb` via staged candidate `.copperpilot/tmp/staging/v9_9_in2_route/candidate/bldc_motor_cntroller_v9_9/`. (`v9_8` and earlier untouched.)
- **Planes preserved**:
  - `In1.Cu` (`GND`, `0.11 mm` below `F.Cu`): locked `power` plane, 0 signal tracks.
  - Lower `In2.Cu` (`VDC`, `y >= 61.8 mm`, East `y >= 54.8 mm` for `x >= 195.2 mm`): protected by `tracks not_allowed` rule area, 0 signal tracks.
  - Upper `In2.Cu` (`y = 15.6..61.5 mm`, `+3.3V` mixed plane): primary routing relief layer for upper-board digital signals, driver control/status, and `+5V`/`+3.3VA`/`GVDD` trunks; `+3.3V` copper zone refills around `In2.Cu` tracks after routing.
- **Rules**: All approved `v9` netclasses, clearances, and `2 oz` outer / `1 oz` inner fab minimums unchanged.
- **Budget**: Max `3` attempts per net group, max `12` FreeRouting runs total.

## Ordered Net Groups
1. **Group 1 (`OVP_IN_LI` cleanup + `GPIO_4`, `GPIO_7`)**: Unroute `OVP_IN_LI` (clears `4` of `5` baseline clearance errors at `U11`/`C136`), then route `OVP_IN_LI`, `GPIO_4`, `GPIO_7` using upper `In2.Cu`.
2. **Group 2 (`DEBUG_SWCLK`, `ENC0_Z`)**: Route remaining two upper-board STM32 (`U6`) digital nets through upper `In2.Cu`.
3. **Group 3 (`/Microcontroller Interface/nFAULT`, `/Motor_Driver2/nOCTW`)**: Close `U2.5`/`U2.6` driver status taps using upper `In2.Cu`.
4. **Group 4 (`+5V`)**: Close all `6` upper-board `+5V` supply gaps (`y < 58.5 mm`) using upper `In2.Cu` trunks.
5. **Group 5 (`+3.3VA`)**: Close all `9` `+3.3VA` analog/thermistor supply gaps using upper `In2.Cu` trunks (`TH1`/`TH5` drop to `F.Cu`/`B.Cu` outside the lower `VDC` keepout).
6. **Group 6 (`GVDD`, `VDC` `R66.1 -> U1/C36`)**: Close `U1.13`/`U2.13` `GVDD` taps and `R66.1`/`C36.1` `VDC` taps.
7. **Group 7 (`/Motor Driver/SH_C`, `/Power Management/HS`)**: Close `C15.1` `SH_C` tap and `F.Cu`/`B.Cu` `HS` tie.
8. **Group 8 (`+3.3V` plane ties, `29` items)**: Tie remaining `+3.3V` SMD pads via short dogbones into `In2.Cu` `+3.3V` pour.
9. **Group 9 (`GND` plane ties, `64` items)**: Tie remaining `GND` SMD pads via short dogbones into `In1.Cu` `GND` plane.
10. **Reserve (`3` runs)**: Targeted retry / `USB_J4_DP` (`J4.A6`) + `USB_J4_DN` clearance cleanup (`F.Cu`/`B.Cu` over `In1.Cu` `GND`, `--no-in2`).
