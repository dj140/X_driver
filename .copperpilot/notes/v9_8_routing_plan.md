# `bldc_motor_cntroller_v9_8` Selective-`In2.Cu` Surgical Routing Plan

## Layer & Plane Policy
- **`F.Cu` (`70 µm`) / `B.Cu` (`70 µm`)**: Primary signal and high-current pour layers.
- **`In1.Cu` (`35 µm`, `power`)**: Unbroken full-board `GND` reference plane (`>95%` solid under `Q1–Q12` and `C_HF1–C_HF6`). No signal tracks allowed.
- **`In2.Cu` (`35 µm`, `mixed`)**: Lower `VDC` plane (`y >= 61.8 mm`, plus `x >= 195.2, y >= 54.8 mm`) protected by `In2_VDC_Track_Keepout` (`tracks not_allowed`). Upper `In2.Cu` (`+3.3V` zone) selectively open for slow/medium-speed signals while keeping `+3.3V` continuous to all decoupling vias.

## Ordered Net Groups (`route --nets`)
1. **Group 1 — USB-C Entry & CAN**: `/I{slash}O Interface/USB_J4_DP`, `/I{slash}O Interface/USB_J4_DN`, `/I{slash}O Interface/USB_CC1`, `/I{slash}O Interface/USB_CC2`, `Net-(F1-Pad1)`, `Net-(D4-A)`, `CAN_H`, `CAN_L`.
2. **Group 2 — Brake Chopper & OVP Signals**: `/Power Management/HS`, `OVP_IN_HI`, `OVP_IN_LI`, `/Microcontroller Interface/AUX_TEMP`, `/Motor Driver/SH_C` (`C15.1` tap).
3. **Group 3 — Driver Status, LED, Bus-Sense & Thermistors**: `/Motor Driver/PWRGD`, `/Motor Driver/nOCTW`, `/Motor_Driver2/nOCTW`, `/Motor Driver/TEMP_SENSE_2`, `/Motor_Driver2/TEMP_SENSE_2`, `Net-(D3-A)`, `/Microcontroller Interface/VBUS_S`, `/Microcontroller Interface/M1_TEMP`.
4. **Group 4 — Remaining STM32 (`U6`) Digital Signals**: `/I{slash}O Interface/GPIO_3`, `/I{slash}O Interface/GPIO_4`, `/I{slash}O Interface/GPIO_7`, `/I{slash}O Interface/DEBUG_SWDIO`, `/I{slash}O Interface/DEBUG_SWCLK`.
5. **Group 5 — Power Rails (`GVDD`, `+5V`, `+3.3VA`, `+3.3V`, `VDC` taps)**: Close remaining supply/power taps and fix minor `U4`/`U5`/`R55` clearance pinches.
6. **Group 6 — `GND` Plane Ties & Final Clearance Cleanup**: Connect remaining `F.Cu` `GND` pads to `In1.Cu`, resolve any remaining minor clearance pinches, refill all zones, verify `0` DRC errors, `0` unconnected items, `0` parity errors, `0` overlaps, and promote to `bldc_motor_cntroller_v9_8/`.
