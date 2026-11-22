# `bldc_motor_cntroller_v9_6` STM32 (`U6`) Full Net-Group Routing Plan

## Ordered Net Groups (All 64 `U6` Pins)
- **Pre-routed in `v9_5` (`4` nets / `4` pins)**:
  - `/Microcontroller Interface/M0_SO1` (`U6.8`), `/Microcontroller Interface/M0_SO2` (`U6.9`), `/Microcontroller Interface/M1_SO2` (`U6.10`), `/Microcontroller Interface/M1_SO1` (`U6.11`)
- **Group 2A — 90-Ohm USB Differential Pair & Local Oscillator / Core / Reset (`7` nets / `7` pins)**:
  - `/I{slash}O Interface/USB_DN` (`U6.44`), `/I{slash}O Interface/USB_DP` (`U6.45`) -> post-route skew check via `lengths --target-skew-mm 2.0`
  - `Net-(U6-PH0)` (`U6.5`), `Net-(U6-PH1)` (`U6.6`), `Net-(U6-NRST)` (`U6.7`), `Net-(U6-VCAP_1)` (`U6.31`), `Net-(U6-VCAP_2)` (`U6.47`)
- **Group 2B — Fast Digital Buses: CAN, SWD, BOOT0, SPI3 + nCS, Driver Control/Fault, Brake Chopper (`14` nets / `14` pins)**:
  - `/I{slash}O Interface/CAN_R` (`U6.61`), `/I{slash}O Interface/CAN_D` (`U6.62`), `/I{slash}O Interface/BOOT0` (`U6.60`), `/I{slash}O Interface/DEBUG_SWDIO` (`U6.46`), `/I{slash}O Interface/DEBUG_SWCLK` (`U6.49`)
  - `/Microcontroller Interface/SPI_M0_nCS` (`U6.2`), `/Microcontroller Interface/SPI_M1_nCS` (`U6.3`), `/Microcontroller Interface/SPI_SCK` (`U6.51`), `/Microcontroller Interface/SPI_MISO` (`U6.52`), `/Microcontroller Interface/SPI_MOSI` (`U6.53`)
  - `/Microcontroller Interface/nFAULT` (`U6.54`), `/Microcontroller Interface/EN_GATE` (`U6.33`), `/Microcontroller Interface/AUX_L` (`U6.29`), `/Microcontroller Interface/AUX_H` (`U6.30`)
- **Group 2C — Dual 6-PWM Motor Control Buses (`12` nets / `12` pins)**:
  - `/Microcontroller Interface/M0_AH` (`U6.41`), `/Microcontroller Interface/M0_BH` (`U6.42`), `/Microcontroller Interface/M0_CH` (`U6.43`), `/Microcontroller Interface/M0_AL` (`U6.34`), `/Microcontroller Interface/M0_BL` (`U6.35`), `/Microcontroller Interface/M0_CL` (`U6.36`)
  - `/Microcontroller Interface/M1_AH` (`U6.37`), `/Microcontroller Interface/M1_BH` (`U6.38`), `/Microcontroller Interface/M1_CH` (`U6.39`), `/Microcontroller Interface/M1_AL` (`U6.23`), `/Microcontroller Interface/M1_BL` (`U6.26`), `/Microcontroller Interface/M1_CL` (`U6.27`)
- **Group 2D — Encoders, Analog Telemetry, and GPIO (`18` nets / `18` pins)**:
  - `/I{slash}O Interface/ENC0_A` (`U6.56`), `/I{slash}O Interface/ENC0_B` (`U6.57`), `/I{slash}O Interface/ENC0_Z` (`U6.40`), `/I{slash}O Interface/ENC1_A` (`U6.58`), `/I{slash}O Interface/ENC1_B` (`U6.59`), `/I{slash}O Interface/ENC1_Z` (`U6.4`)
  - `/Microcontroller Interface/M1_TEMP` (`U6.20`), `/Microcontroller Interface/AUX_TEMP` (`U6.21`), `/Microcontroller Interface/VBUS_S` (`U6.22`), `/Microcontroller Interface/M0_TEMP` (`U6.25`)
  - `/I{slash}O Interface/GPIO_1` (`U6.14`) .. `/I{slash}O Interface/GPIO_8` (`U6.55`)
- **Group 2E — `U6` Power & Return Nets (`3` nets / `9` `U6` pins + local decoupling ties)**:
  - `+3.3VA` (`U6.13`), `+3.3V` (`U6.1, 19, 32, 48, 64`), `GND` (`U6.12, 18, 63`)
