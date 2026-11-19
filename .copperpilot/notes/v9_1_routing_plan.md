# V9.1 Surgical FreeRouting Plan (Units 4 & 5 — Split Original Track Hierarchy)

## Approved Netclass Track Widths (`2 oz` / `70 um` Outer Copper)
- **`Gate_FET` (`0.50 mm`, clr `0.18 mm`)**: `Net-(Q1-G)` .. `Net-(Q12-G)` (`0` vias, lateral `F.Cu` exit from `DirectFET_L8` Pad 2 to `R_gate.2`).
- **`Gate_Drv` (`0.20 mm`, clr `0.18 mm`)**: `GH_A..GL_C`, `Net-(U1/U2-BST_A..C)`, `Net-(Q13/Q14-G)`, `Net-(U3-HO/LO)`.
- **`Power` (`0.20 mm` driver/bootstrap taps, clr `0.18 mm` inside `U1/U2` / `0.25 mm` outside via DRU)**: `VDC`, `SH_A..C`, `SL_B..C`, `HS` (bulk current carried in `6.5–8.5 mm` `F.Cu+B.Cu` pours).
- **`Sense` (`0.16 mm`, clr `0.16 mm`, diff `0.16/0.16 mm`)**: `SP1/SN1`, `SP2/SN2`, `Net-(NT1,3,5,7-Pad1)`, `Net-(U1/U2-SO1,SO2)`, `M0_SO1..M1_SO2`.
- **`Supply_5V` (`0.50 mm`, clr `0.18 mm`, via `0.70/0.35 mm`)**: `+5V`, `Net-(F1-Pad1)`.
- **`Supply` (`0.30 mm`, clr `0.18 mm`)**: `GVDD`, `+3.3V`, `+3.3VA`, `AVDD`, `DVDD`, `Net-(C20-Pad1)`, `Net-(D1-K)`, `Net-(D2-K)`.
- **`USB` (`0.155 mm`, clr `0.18 mm`, diff `0.155/0.220 mm`)**: `USB_DP`, `USB_DN`, `USB_J4_DP`, `USB_J4_DN`.
- **`CAN` (`0.20 mm`, clr `0.18 mm`, diff `0.20/0.25 mm`)**: `CAN_H`, `CAN_L`, `CAN_D`, `CAN_R`.
- **`Default` (`0.16 mm`, clr `0.16 mm`)**: PWM, SPI, GPIO, ENC, SWD, TEMP, status/control, `CP1/CP2`, local `GND` pad ties.

## Unit 4 — Power-Stage Differential Kelvin Sense, Gates, and DRV8301 Power/Buck Groups (4 Route Runs)
1. **Run 4.1 — Differential Kelvin Shunt Sense & Amplifier Outputs (`Sense`, `0.16 mm`, 20 nets)**:
   - `Net-(NT1,3,5,7-Pad1)`, `/Motor Driver/SP1,SN1,SP2,SN2`, `/Motor_Driver2/SP1,SN1,SP2,SN2`, `Net-(U1/U2-SO1,SO2)`, `/Microcontroller Interface/M0_SO1,M0_SO2,M1_SO1,M1_SO2`
2. **Run 4.2 — Post-Resistor `Q1–Q12` Lateral `F.Cu` FET Gates (`Gate_FET`, `0.50 mm`, 12 nets)**:
   - `Net-(Q1-G)` .. `Net-(Q12-G)` (`0` vias on gate nets)
3. **Run 4.3 — `DRV8301` Pre-Resistor Gates, Bootstrap Caps, and Phase/Shunt Sense Taps (`Gate_Drv` + `Power`, `0.20 mm`, 28 nets)**:
   - `/Motor Driver/GH_A..GL_C`, `/Motor_Driver2/GH_A..GL_C`, `Net-(U1/U2-BST_A..C)`, `/Motor Driver/SH_A..SL_C`, `/Motor_Driver2/SH_A..SL_C`
4. **Run 4.4 — `DRV8301` `VDC`/`PVDD`, `GVDD`, `AVDD/DVDD`, `CP1/CP2`, Config Passives, & `U1` `+5V` Buck (`0.16–0.50 mm`, 23 nets)**:
   - `VDC`, `GVDD`, `/Motor Driver/AVDD,DVDD`, `/Motor_Driver2/AVDD,DVDD`, `Net-(U1/U2-CP1,CP2,DTC,DC_CAL,SS_TR)`, `Net-(D1-K)`, `Net-(U1-BST_BK,RT_CLK,COMP,VSENSE)`, `Net-(C20-Pad1)`, `+5V`

## Unit 5 — Upper-Board High-Speed, Digital Buses, Brake Chopper, and GND Tie Completion (3–4 Route Runs)
1. **Run 5.1 — `USB 90-Ohm` Differential Pair + `CAN` Differential Bus (`0.155 mm` / `0.20 mm`)**:
   - `USB_J4_DP,USB_J4_DN,USB_DP,USB_DN,USB_CC1,USB_CC2`, `Net-(F1-Pad1)`, `Net-(D4-A)`, `CAN_H,CAN_L,CAN_D,CAN_R` (followed by `lengths` skew check on USB pair).
2. **Run 5.2 — `STM32` Clock/Reset/VCAP, `+3.3V`/`+3.3VA` LDOs, & `LM5109B` Brake Chopper (`U3/Q13/Q14`)**:
   - `Net-(U6-PH0,PH1,NRST,VCAP_1,VCAP_2)`, `BOOT0`, `Net-(D3-A)`, `+3.3V`, `+3.3VA`, `Net-(Q13-G,Q14-G,U3-HO,U3-LO)`, `Net-(D2-K)`, `/Power Management/HS`, `AUX_H,AUX_L,VBUS_S`.
3. **Run 5.3 — `M0/M1` 6-PWM, `SPI3`, Status/Enable, Encoders, `SWD`, `GPIO1–8`, Thermistors, & Local `GND` Pad Ties**.
