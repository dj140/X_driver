# `bldc_motor_cntroller_v9_6` Selective `In2.Cu` Finish-Routing Plan

## Layer Policy
- `F.Cu` (`70 µm`, `signal`): Primary routing for high-speed/sensitive signals (`USB`, `CAN`, `SPI3`, `Y1`, Kelvin `SP/SN`) and power pours.
- `In1.Cu` (`35 µm`, `power`, `GND`): 100% unbroken solid ground plane (0 tracks).
- `In2.Cu` (`35 µm`, `mixed`):
  - Upper digital zone (`y = 15.6..59.5 mm`, `+3.3V` pour): Selectively open for slow/medium-speed signals (SWD, GPIO, thermistors, `VBUS_S`, `AUX_H/L`, status pull-ups). High-speed `USB` and `CAN` stay on `F.Cu`/`B.Cu` only.
  - Lower power stage (`y >= 59.5 mm`, `VDC` pour): Protected by `In2.Cu` `tracks=not_allowed` keepout (0 tracks).
- `B.Cu` (`70 µm`, `signal`): Secondary signal routing and DC power-stage current-sharing pours.
- Under `U6` (`[105.0..115.0, 39.0..49.0]`): Keep `0` tracks and `0` vias on all layers.

## Ordered Net Groups (Headless FreeRouting)
1. **Group 1 — USB-C Entry & CAN (`F.Cu`/`B.Cu` only)**: `/I{slash}O Interface/USB_J4_DN`, `/I{slash}O Interface/USB_J4_DP`, `/I{slash}O Interface/USB_CC1`, `/I{slash}O Interface/USB_CC2`, `Net-(F1-Pad1)`, `Net-(D4-A)`, `CAN_H`, `CAN_L`.
2. **Group 2 — Remaining `U6` North/West/East Slow Digital & SWD (upper `In2.Cu` allowed)**: `/I{slash}O Interface/DEBUG_SWCLK`, `/I{slash}O Interface/DEBUG_SWDIO`, `/I{slash}O Interface/GPIO_3`, `/I{slash}O Interface/GPIO_4`, `/I{slash}O Interface/GPIO_7`, `/I{slash}O Interface/ENC0_Z` (re-routed cleanly to clear `R55.1` clearance error).
3. **Group 3 — Remaining `U6` South Analog, Thermistors & Brake Control (upper `In2.Cu` allowed)**: `/Microcontroller Interface/AUX_H`, `/Microcontroller Interface/AUX_L`, `/Microcontroller Interface/VBUS_S`, `/Microcontroller Interface/AUX_TEMP`, `/Microcontroller Interface/M1_TEMP`.
4. **Group 4 — Brake Chopper Local, Driver Pull-ups, Local Thermistors & LED**: `Net-(U3-HO)`, `Net-(U3-LO)`, `Net-(Q13-G)`, `Net-(Q14-G)`, `Net-(D2-K)`, `/Motor Driver/PWRGD`, `/Motor Driver/nOCTW`, `/Motor_Driver2/nOCTW`, `/Motor Driver/TEMP_SENSE_2`, `/Motor_Driver2/TEMP_SENSE_2`, `Net-(D3-A)`.
5. **Group 5 — Power & Driver Rail Ties**: `/Motor Driver/SH_C`, `/Power Management/HS`, `VDC`, `GVDD`, `+5V`, `+3.3VA` (after clearing `U4.2`/`U5.4` clearance stubs).
6. **Group 6 — `+3.3V` Plane Ties**: `+3.3V` (verify `+3.3V` `In2.Cu` continuity and `0` isolated copper after refill).
7. **Group 7 — `GND` Plane Ties**: `GND` (all remaining SMD pad-to-`In1.Cu` ties).
