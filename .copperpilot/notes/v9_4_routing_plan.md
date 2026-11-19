# `bldc_motor_cntroller_v9_4` Surgical FreeRouting Plan (Units 3 & 4)

## 1. Constraints & Copper Protection Rules
- **Stackup**: 4-layer `1.6 mm` (`F.Cu` `70 µm`, `0.11 mm` `3313` prepreg `er = 4.1`, `In1.Cu` `35 µm` solid `GND`, `1.17 mm` core, `In2.Cu` `35 µm` `+3.3V`/`VDC`, `0.11 mm` `3313` prepreg, `B.Cu` `70 µm`).
- **Netclasses (`bldc_motor_cntroller_v9_4.kicad_pro` + `.kicad_dru`)**:
  - `Gate_FET`: `0.50 mm` width, `0.18 mm` clearance (`0` vias, lateral `F.Cu` exit `Q1–Q12` Pad 2 -> `R_gate.2`).
  - `Gate_Drv`: `0.20 mm` width, `0.18 mm` clearance (`GH_A..GL_C`, `BST_A..C`, `Q13/Q14-G`, `U3-HO/LO`).
  - `Power`: `0.20 mm` width for driver/sense taps (`0.18 mm` clearance inside `U1`/`U2` courtyards, `0.25 mm` outside via `.kicad_dru`); bulk phase/bus current carried in `6–12.7 mm` `F.Cu + B.Cu` pours.
  - `Sense`: `0.16 mm` width, `0.16 mm` clearance (`SP1/SN1`, `SP2/SN2`, `NT1/3/5/7`, `SO1/SO2`, `M0/M1_SO1/2`).
  - `USB`: `0.155 mm` width, `0.220 mm` diff gap (`90.2 Ω` masked on `70 µm` `F.Cu` over `0.11 mm` `In1.Cu`), `0.18 mm` clearance.
  - `CAN`: `0.20 mm` width, `0.25 mm` diff gap, `0.18 mm` clearance.
  - `Supply_5V`: `0.50 mm` width, `0.18 mm` clearance (`+5V`, `Net-(F1-Pad1)`).
  - `Supply`: `0.30 mm` width, `0.18 mm` clearance (`GVDD`, `+3.3V`, `+3.3VA`, `AVDD`, `DVDD`, `Net-(D1-K)`, `Net-(D2-K)`).
  - `Default`: `0.16 mm` width, `0.16 mm` clearance, `0.60 / 0.30 mm` vias.
- **Commutation Plane & Heatsink Protection**:
  - `vias not_allowed` in `[10.8, 81.6]..[92.8, 97.6]` and `[128.8, 81.6]..[210.8, 97.6]` (`100%` solid `In1.Cu` `GND` under `Q1–Q12`).
  - `footprints not_allowed` in `y = [81.60 .. 97.40]` (`>= 5.42 mm` North + inter-FET heatsink envelope).
  - `F.Cu` pour-neck `tracks not_allowed` keepouts over the `6` HS `VDC` necks and `4` `SL_B/SL_C` `C_HF` return strips so signal traces cannot split any power pour.

## 2. Net-Group Routing Order (Max 12 Runs Total)
### Unit 3 — Power-Stage Critical Groups (4 Runs)
1. **Group 3.1 (`Sense`, 20 nets)**: `Net-(NT1,3,5,7-Pad1)`, `/Motor Driver/SP1,SN1,SP2,SN2`, `/Motor_Driver2/SP1,SN1,SP2,SN2`, `Net-(U1/U2-SO1,SO2)`, `/Microcontroller Interface/M0_SO1,M0_SO2,M1_SO1,M1_SO2` (+ `lengths` skew check on `SP/SN` pairs).
2. **Group 3.2 (`Gate_FET`, 12 nets)**: `Net-(Q1-G)` .. `Net-(Q12-G)` (`0.50 mm`, `0` vias on `F.Cu`).
3. **Group 3.3 (`Gate_Drv` + `Power` taps, 28 nets)**: `/Motor Driver/GH_A..GL_C`, `/Motor_Driver2/GH_A..GL_C`, `Net-(U1/U2-BST_A..C)`, `/Motor Driver/SH_A..SL_C`, `/Motor_Driver2/SH_A..SL_C`.
4. **Group 3.4 (`DRV8301` Power/Buck/Config, 23 nets)**: `VDC`, `GVDD`, `/Motor Driver/AVDD,DVDD`, `/Motor_Driver2/AVDD,DVDD`, `Net-(U1/U2-CP1,CP2,DTC,DC_CAL,SS_TR)`, `Net-(D1-K)`, `Net-(U1-BST_BK,RT_CLK,COMP,VSENSE)`, `Net-(C20-Pad1)`, `+5V`.

### Unit 4 — Upper-Board High-Speed, Control, Brake Chopper & GND Ties (3 Runs)
5. **Group 4.1 (`USB` + `CAN`, 12 nets)**: `/I{slash}O Interface/USB_J4_DP,USB_J4_DN,USB_DP,USB_DN,USB_CC1,USB_CC2`, `Net-(F1-Pad1)`, `Net-(D4-A)`, `CAN_H,CAN_L`, `/I{slash}O Interface/CAN_D,CAN_R` (+ `lengths` skew check on USB & CAN pairs).
6. **Group 4.2 (`MCU Core` + `LDOs` + `Brake Chopper`, 18 nets)**: `Net-(U6-PH0,PH1,NRST,VCAP_1,VCAP_2)`, `/I{slash}O Interface/BOOT0`, `Net-(D3-A)`, `+3.3V`, `+3.3VA`, `Net-(Q13-G,Q14-G,U3-HO,U3-LO)`, `Net-(D2-K)`, `/Power Management/HS`, `/Microcontroller Interface/AUX_H,AUX_L,VBUS_S`.
7. **Group 4.3 (`PWM` + `SPI3` + `Encoders/GPIO/SWD/NTC` + `GND` Ties, 38 nets)**: All remaining digital/analog signals and `GND` pad return ties.
