# V9_10 Unit 5 Surgical FreeRouting Plan

Target: `.copperpilot/tmp/staging/v9_10_u5/candidate/bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_10.kicad_pcb`
Baseline: `0` DRC errors, `0` courtyard overlaps, `0` schematic-parity errors, `270` unconnected items across `89` nets.
Layer policy: `In1.Cu` locked as solid `GND` plane; lower `In2.Cu` (`y >= 61.8 mm`, `y >= 54.8 mm` east of `x = 195.2 mm`) locked as `VDC` plane; upper `In2.Cu` open for slow/medium digital & supply routing; `F.Cu`/`B.Cu` open.

## Ordered Net Groups (8 planned runs, max 12 board cap)

1. **Group 1 — USB 90-Ohm Diff Pair, USB VBUS & U6 Core VCAP (7 nets)**
   - `/I{slash}O Interface/USB_DP`, `/I{slash}O Interface/USB_DN`, `/I{slash}O Interface/USB_J4_DP`, `/I{slash}O Interface/USB_J4_DN`, `/I{slash}O Interface/USB_VBUS_RAW`, `/I{slash}O Interface/USB_VBUS_PROT`, `Net-(U6-VCAP_1)`, `Net-(U6-VCAP_2)`
   - Constraint: USB routed on `F.Cu` over unbroken `In1.Cu` `GND` (`0.155/0.220 mm`), check skew with `lengths`.
2. **Group 2 — Power-Stage Q1–Q12 Gates (12 nets)**
   - `Net-(Q1-G)` .. `Net-(Q12-G)` (`0.50 mm` zero-via `F.Cu` gate traces from shifted gate resistors to shifted DirectFET L8 gate pads).
3. **Group 3 — Kelvin Current-Sense Pairs & Net-Tie Bridges (14 nets)**
   - `/Motor Driver/SP1`, `SN1`, `SP2`, `SN2`, `/Motor_Driver2/SP1`, `SN1`, `SP2`, `SN2`, `Net-(NT1-Pad1)`, `Net-(NT3-Pad1)`, `Net-(NT5-Pad1)`, `Net-(NT7-Pad1)`, `Net-(U1-SO1)`, `Net-(U2-SO1)`.
4. **Group 4 — DRV8301 Gate-Drive & Bootstrap/Phase Sense Taps (24 nets)**
   - `/Motor Driver/GH_A..GL_C`, `/Motor_Driver2/GH_A..GL_C`, `Net-(U1-BST_BK)`, `Net-(U2-BST_A)`, `/Motor Driver/DVDD`, `/Motor_Driver2/DVDD`, `/Motor Driver/SH_A..SL_C`, `/Motor_Driver2/SH_A..SL_C`, `/Power Management/HS`.
5. **Group 5 — Upper Digital, SPI, PWM, OVP, Thermistor & IO Signals (21 nets)**
   - `OVP_IN_HI`, `OVP_IN_LI`, `/Microcontroller Interface/EN_GATE`, `M0_CL`, `SPI_M0_nCS`, `SPI_M1_nCS`, `M0_TEMP`, `M1_TEMP`, `AUX_TEMP`, `/Motor_Driver2/TEMP_SENSE_2`, `/Motor_Driver2/nOCTW`, `/I{slash}O Interface/CAN_D`, `DEBUG_SWDIO`, `DEBUG_SWCLK`, `ENC0_Z`, `ENC1_Z`, `GPIO_1`, `GPIO_2`, `GPIO_3`, `GPIO_4`, `GPIO_5`, `GPIO_7`.
6. **Group 6 — Supply Rails (`+5V`, `+3.3VA`, `GVDD`) (3 nets)**
   - `+5V`, `+3.3VA`, `GVDD` (including new `U1.24`/`U2.24` `REF` caps and relocated `U6.13` `VDDA` caps).
7. **Group 7 — `+3.3V` & `VDC` Local Ties (2 nets)**
   - `+3.3V` (including relocated `U6` bypass caps and new `U1.49`/`U2.49` `VDD_SPI` caps) and `VDC` (including `C138–C143`, `C146–C151`, `C154–C157`).
8. **Group 8 — `GND` Plane-Tie Stubs (1 net)**
   - `GND` (all remaining SMD pad-to-via ties to `In1.Cu`).
