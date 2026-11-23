# `bldc_motor_cntroller_v9_12` Surgical Routing Plan

- **Board:** `bldc_motor_cntroller_v9_12/bldc_motor_cntroller_v9_12.kicad_pcb` (routed in `.copperpilot/tmp/staging/v9_12_route/candidate/`).
- **Stackup / Plane Policy:** `F.Cu` & `B.Cu` signal (`70 µm`), `In1.Cu` solid `GND` plane (`35 µm`, locked), `In2.Cu` selective upper-digital routing (`y < 54.80 mm`) with `In2_VDC_Track_Keepout` protecting the lower `VDC` plane (`35 µm`).
- **Baseline:** `1,101` segments, `574` vias, `111` zones, `1` pre-existing clearance error (`J5.A6` `0.1790 mm`), `0` courtyard overlaps, `298` unconnected items across `89` nets.
- **Budget:** `<= 3` attempts per group, `<= 12` FreeRouting runs total.

## Ordered Net Groups

1. **Group 1 (High-speed USB, VCAP_2 & FET Gates):** `/I/O Interface/USB_DP`, `/I/O Interface/USB_J4_DP`, `Net-(U9-VCAP_2)`, `Net-(Q13-G)`, `Net-(Q14-G)` (verify USB skew with `lengths`).
2. **Group 2 (Kelvin Sense & CSA Outputs):** `/Motor Driver/SP1`, `SN1`, `SP2`, `SN2`; `/Motor_Driver2/SP1`, `SN1`, `SP2`, `SN2`; `/Microcontroller Interface/M0_SO1`, `M0_SO2`, `M1_SO1`, `M1_SO2`.
3. **Group 3 (M0 Driver Gates, Phase/Shunt Taps, DVDD & Buck):** `/Motor Driver/GH_A..GL_C`, `SH_A..C`, `SL_B/C`, `DVDD`, `Net-(U7-RT_CLK)`, `Net-(U7-VSENSE)`, `Net-(D6-K)`.
4. **Group 4 (M1 Driver Gates, Phase/Shunt Taps, DVDD & Status):** `/Motor_Driver2/GH_A..GL_C`, `SH_A..C`, `SL_B/C`, `DVDD`, `nOCTW`, `TEMP_SENSE_2`.
5. **Group 5 (M0 & M1 6-PWM + `EN_GATE`):** `M0_AH..M0_CL`, `M1_AH..M1_CL`, `EN_GATE`.
6. **Group 6 (SPI3, `nFAULT`, CAN_D & OVP/Brake):** `SPI_SCK`, `SPI_MISO`, `SPI_MOSI`, `SPI_M0_nCS`, `SPI_M1_nCS`, `nFAULT`, `CAN_D`, `OVP_IN_HI`, `OVP_IN_LI`, `U3_LI_DRV`, `/Power Management/HS`.
7. **Group 7 (GPIO, Encoders, SWD & Thermistors):** `DEBUG_SWCLK`, `DEBUG_SWDIO`, `ENC0_Z`, `ENC1_Z`, `GPIO_1..5`, `GPIO_7`, `AUX_TEMP`, `M0_TEMP`, `M1_TEMP`.
8. **Group 8 (Supply Rails):** `+5V`, `GVDD`, `+3.3VA`, `VDC`.
9. **Group 9 (`+3.3V` Plane Ties):** `+3.3V`.
10. **Group 10 (`GND` Plane Ties):** `GND`.
