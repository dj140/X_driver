# `bldc_motor_cntroller_v9_12` Routing Status & Root-Cause Analysis (12-Run Cap)

- **Staged candidate:** `.copperpilot/tmp/staging/v9_12_route/candidate/bldc_motor_cntroller_v9_12/bldc_motor_cntroller_v9_12.kicad_pcb` (primary `bldc_motor_cntroller_v9_12/` untouched until approved).
- **Progress (`298 -> 241` unconnected items; `89 -> 55` unconnected nets; `+239` segments `1,101 -> 1,340`; `+17` vias `574 -> 591`):**
  - **100% routed in this pass (`34` nets):**
    - Power-stage FET gates: `Net-(Q13-G)`, `Net-(Q14-G)` (`0.50 mm` zero-via `F.Cu` — all `12` MOSFET gates `Q3–Q14` now complete)
    - Kelvin current-sense pairs (`8/8`): `/Motor Driver/SP1, SN1, SP2, SN2` & `/Motor_Driver2/SP1, SN1, SP2, SN2` (`100%` `F.Cu`, `0` vias)
    - Motor 6-PWM + enable (`13/13`): `M0_AH..M0_CL`, `M1_AH..M1_CL`, `EN_GATE`
    - Current-sense outputs (`4/4`): `M0_SO1`, `M0_SO2`, `M1_SO1`, `M1_SO2`
    - SPI3 (`4/5`): `SPI_SCK`, `SPI_MOSI`, `SPI_M0_nCS`, `SPI_M1_nCS`
    - M0 driver local (`3`): `/Motor Driver/DVDD`, `/Motor Driver/GH_B`, `/Motor Driver/GL_A`
  - **USB differential pair length/skew (`lengths`):**
    - `USB_J4_DP` (`9.253 mm`) vs `USB_J4_DN` (`11.237 mm`): skew **`1.984 mm`** (`<= 5.0 mm` pass)
    - `USB_DP` (`114.963 mm`) vs `USB_DN` (`122.561 mm`): skew **`7.599 mm`** (`> 5.0 mm`; `USB_DP` still has `1` open pad connection)

## Run Log (`12 / 12` Board Budget)

| Run | Tag | Group | Elapsed (s) | Decision | Result |
|---|---|---|---:|---|---|
| 1 | unshielded-1 | USB, VCAP_2, Q13/Q14 gates | 120.2 | timeout | Timed out before Pass 1 (87 unshielded DSN planes) |
| 2 | unshielded-2 | USB, VCAP_2, Q13/Q14 gates | 240.2 | timeout | Timed out before Pass 1 (switched to `via_shield.py` + `chain_pcb_segments.py`) |
| 3 | `g1_usb_gates` | USB_DP/J4_DP, VCAP_2, Q13/Q14 gates (`F/B`) | 94.6 | **kept** | `0` new errors; `Q13/Q14` gates routed; `VCAP_2` open |
| 4 | `g2_kelvin_sense` | 12 Kelvin + SO1/SO2 nets (`F/B`) | 179.7 | timeout | Split into 8-net Kelvin group |
| 5 | `g2a_kelvin` | All 8 M0+M1 `SP1/SN1/SP2/SN2` (`F/B`) | 123.4 | **kept** | **`8/8` 100% routed on `F.Cu`**, `0` vias, `0` new errors |
| 6 | `g3_m0_power` | 15 M0 gate + phase/shunt pour nets (`F/B`) | 170.8 | timeout | Pour-heavy nets (`SH`/`SL`) need separate group |
| 7 | `g3a_drv_gates_dvdd` | 18 M0+M1 gate + DVDD nets (`F/B`) | 179.8 | timeout | Split to `<= 10` nets per run |
| 8 | `g3a_m0_gates` | 9 M0 gate/DVDD/RT_CLK/VSENSE (`F/B`) | 209.3 | timeout | Reduced to 7 nets / 4 passes |
| 9 | `g3a_m0_gates_dvdd` | 7 M0 `GH/GL` + `DVDD` (`F/B`) | 256.2 | **kept** | `0` new errors; `DVDD`, `GH_B`, `GL_A` routed on `F.Cu`; `GH_A/C`, `GL_B/C` open |
| 10 | `g4_upper_pwm_en` | 13 `M0/M1` 6-PWM + `EN_GATE` (`+In2`) | 212.2 | **kept** | **`13/13` 100% routed**, `0` new errors |
| 11 | `g5_spi_so_ovp_drv` | 16 SPI/SO/OVP/M1-local nets (`+In2`) | 237.6 | timeout | Split to 10 nets |
| 12 | `g5a_spi_fault_so` | 10 SPI3, `nFAULT`, `M0/M1 SO1/SO2` (`+In2`) | 209.8 | **kept** | `0` new errors; `8/10` 100% routed (`SPI_MISO`, `nFAULT` 1 open each) |

## Post-Refill Staged Verification & Root Cause

- **Overlaps (`query_design`):** `0` courtyard overlaps, `0` footprints outside board (`329` footprints).
- **DRC (`run_drc`):** `0` shorts, `0` keepout violations, `3` minor clearance errors (`0.1745–0.1790 mm` vs `0.1800 mm`: pre-existing `J5.A6` `0.1790 mm` + two `+3.3VA` rounding slivers at `C12`/`C13`); `241` unconnected items across `55` nets (`111` `GND`, `17` `+3.3V`, `11` `VDC`, `10` `+3.3VA`, `7` `GVDD`, `6` `+5V`, `6` `Net-(D6-K)`, `29` `SH`/`SL` driver taps, `44` remaining signal connections).
- **Key Physical Bottleneck (RCA):**
  1. **Gate resistor via-drop pinch (`y = 83..85 mm`):** `R20–R54` gate resistor pads (`y = 84.02 mm`) sit between the `F.Cu` `VDC` pours (`y = 79.4..92.5`) and `F.Cu` `SL_B/C` pours (`y = 84.2..107.5`), leaving `< 1.10 mm` (`0.60 mm` via + `2 × 0.25 mm` HV clearance) to drop a `B.Cu` via for `GH_A/C` and `GL_B/C`. Trimming a `1.5 mm` notch in the `F.Cu` `VDC` pour edge at each gate resistor pad (`y = 83.0..85.0`) opens clean `B.Cu` via drops without touching `In1.Cu` `GND` or `In2.Cu` `VDC`.
  2. **Board complexity vs. 12-run cap:** With `87` DSN planes and `329` footprints, `8–13` net groups complete reliably in `95–215 s` per run. Finishing the remaining `55` nets requires a second budgeted routing pass (no rule relaxation required).
