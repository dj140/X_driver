# STM32 (`U6`) 64-Pin Fanout Via Placement (`bldc_motor_cntroller_v9_5`)

## 1. Design Summary & Physical Verification
- **Target**: `U6` (`STM32F405RGTx`, `Package_QFP:LQFP-64_10x10mm_P0.5mm` at `(110.00, 44.00)`) in `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb`.
- **Coverage**: `64 / 64` connected pins (`0` unconnected schematic pins on `U6`) each received one dedicated `0.60 mm / 0.30 mm` (`F.Cu` to `B.Cu`, `0.15 mm` annular ring for `2 oz` outer copper) fanout via (`38` outward, `26` inward; total board vias `457 -> 521`).
- **Dogbone Geometry**: Pad-center-to-via-center distance `1.68 mm .. 3.03 mm` (`0.90 mm .. 2.25 mm` from pad tip), preserving `>= 0.45 mm` solder-mask dam from each own pad and `>= 0.25 mm` copper clearance to all neighboring pads and existing `M0_SO1/2`, `M1_SO1/2` traces (`Pin 8` placed directly on `M0_SO1` at `(102.550, 43.750)`).
- **Reference-Plane Integrity (`In1.Cu` `GND` & `In2.Cu` `+3.3V`)**: Minimum center-to-center pitch across all non-coupled different-net vias is `1.331 mm`, maintaining continuous copper webs on both `In1.Cu` (`GND`) and `In2.Cu` (`+3.3V`) with `0` plane-splitting slots and `0` new `isolated_copper` islands; `USB_DN` (`pin 44`) and `USB_DP` (`pin 45`) use a coupled `1.05 mm` inward differential via pair aimed West toward `J4`.
- **Post-Promotion DRC**: `0` copper/clearance/hole/annular/parity DRC errors (`64` expected `via_dangling` warnings until `F.Cu` pad-to-via escape stubs and upper-board nets are routed).

## 2. Pin-by-Pin Fanout Via Coordinates

| Pin | Side | Net | Pad `(x, y)` (mm) | Via `(x, y)` (mm) | Center Dist (mm) |
|---:|:---:|---|---:|---:|---:|
| 1 | out | `+3.3V` | `(104.325, 40.250)` | `(102.600, 39.700)` | `1.81` |
| 2 | out | `/Microcontroller Interface/SPI_M0_nCS` | `(104.325, 40.750)` | `(101.650, 40.750)` | `2.67` |
| 3 | in | `/Microcontroller Interface/SPI_M1_nCS` | `(104.325, 41.250)` | `(106.050, 41.250)` | `1.72` |
| 4 | out | `/I{slash}O Interface/ENC1_Z` | `(104.325, 41.750)` | `(102.600, 41.750)` | `1.73` |
| 5 | in | `Net-(U6-PH0)` | `(104.325, 42.250)` | `(107.350, 42.050)` | `3.03` |
| 6 | in | `Net-(U6-PH1)` | `(104.325, 42.750)` | `(106.050, 42.750)` | `1.72` |
| 7 | out | `Net-(U6-NRST)` | `(104.325, 43.250)` | `(101.650, 42.700)` | `2.73` |
| 8 | out | `/Microcontroller Interface/M0_SO1` | `(104.325, 43.750)` | `(102.550, 43.750)` | `1.78` |
| 9 | in | `/Microcontroller Interface/M0_SO2` | `(104.325, 44.250)` | `(107.350, 44.450)` | `3.03` |
| 10 | in | `/Microcontroller Interface/M1_SO2` | `(104.325, 44.750)` | `(106.050, 44.950)` | `1.74` |
| 11 | out | `/Microcontroller Interface/M1_SO1` | `(104.325, 45.250)` | `(102.600, 45.500)` | `1.74` |
| 12 | in | `GND` | `(104.325, 45.750)` | `(107.350, 45.950)` | `3.03` |
| 13 | out | `+3.3VA` | `(104.325, 46.250)` | `(101.650, 46.500)` | `2.69` |
| 14 | in | `/I{slash}O Interface/GPIO_1` | `(104.325, 46.750)` | `(106.050, 46.750)` | `1.72` |
| 15 | out | `/I{slash}O Interface/GPIO_2` | `(104.325, 47.250)` | `(102.600, 47.500)` | `1.74` |
| 16 | out | `/I{slash}O Interface/GPIO_3` | `(104.325, 47.750)` | `(101.650, 48.700)` | `2.84` |
| 17 | out | `/I{slash}O Interface/GPIO_4` | `(106.250, 49.675)` | `(105.300, 51.350)` | `1.93` |
| 18 | out | `GND` | `(106.750, 49.675)` | `(106.200, 52.350)` | `2.73` |
| 19 | out | `+3.3V` | `(107.250, 49.675)` | `(107.250, 51.350)` | `1.68` |
| 20 | in | `/Microcontroller Interface/M1_TEMP` | `(107.750, 49.675)` | `(107.300, 47.950)` | `1.78` |
| 21 | in | `/Microcontroller Interface/AUX_TEMP` | `(108.250, 49.675)` | `(108.700, 47.950)` | `1.78` |
| 22 | out | `/Microcontroller Interface/VBUS_S` | `(108.750, 49.675)` | `(108.200, 52.350)` | `2.73` |
| 23 | out | `/Microcontroller Interface/M1_AL` | `(109.250, 49.675)` | `(109.250, 51.350)` | `1.68` |
| 24 | in | `/I{slash}O Interface/GPIO_5` | `(109.750, 49.675)` | `(109.550, 46.650)` | `3.03` |
| 25 | in | `/Microcontroller Interface/M0_TEMP` | `(110.250, 49.675)` | `(110.250, 47.950)` | `1.72` |
| 26 | out | `/Microcontroller Interface/M1_BL` | `(110.750, 49.675)` | `(110.750, 51.350)` | `1.68` |
| 27 | in | `/Microcontroller Interface/M1_CL` | `(111.250, 49.675)` | `(111.050, 46.650)` | `3.03` |
| 28 | out | `/I{slash}O Interface/GPIO_6` | `(111.750, 49.675)` | `(111.750, 52.350)` | `2.68` |
| 29 | in | `/Microcontroller Interface/AUX_L` | `(112.250, 49.675)` | `(112.250, 47.950)` | `1.72` |
| 30 | out | `/Microcontroller Interface/AUX_H` | `(112.750, 49.675)` | `(112.750, 51.350)` | `1.68` |
| 31 | out | `Net-(U6-VCAP_1)` | `(113.250, 49.675)` | `(113.750, 52.350)` | `2.72` |
| 32 | out | `+3.3V` | `(113.750, 49.675)` | `(114.700, 51.350)` | `1.93` |
| 33 | out | `/Microcontroller Interface/EN_GATE` | `(115.675, 47.750)` | `(117.400, 47.500)` | `1.74` |
| 34 | in | `/Microcontroller Interface/M0_AL` | `(115.675, 47.250)` | `(113.950, 47.050)` | `1.74` |
| 35 | out | `/Microcontroller Interface/M0_BL` | `(115.675, 46.750)` | `(118.500, 46.750)` | `2.83` |
| 36 | out | `/Microcontroller Interface/M0_CL` | `(115.675, 46.250)` | `(117.400, 46.000)` | `1.74` |
| 37 | in | `/Microcontroller Interface/M1_AH` | `(115.675, 45.750)` | `(113.950, 45.550)` | `1.74` |
| 38 | out | `/Microcontroller Interface/M1_BH` | `(115.675, 45.250)` | `(118.500, 45.250)` | `2.83` |
| 39 | out | `/Microcontroller Interface/M1_CH` | `(115.675, 44.750)` | `(117.400, 44.500)` | `1.74` |
| 40 | in | `/I{slash}O Interface/ENC0_Z` | `(115.675, 44.250)` | `(112.650, 44.450)` | `3.03` |
| 41 | in | `/Microcontroller Interface/M0_AH` | `(115.675, 43.750)` | `(113.950, 43.750)` | `1.72` |
| 42 | in | `/Microcontroller Interface/M0_BH` | `(115.675, 43.250)` | `(112.650, 43.050)` | `3.03` |
| 43 | out | `/Microcontroller Interface/M0_CH` | `(115.675, 42.750)` | `(117.400, 42.750)` | `1.73` |
| 44 | in | `/I{slash}O Interface/USB_DN` | `(115.675, 42.250)` | `(113.900, 42.350)` | `1.78` |
| 45 | in | `/I{slash}O Interface/USB_DP` | `(115.675, 41.750)` | `(113.900, 41.300)` | `1.83` |
| 46 | out | `/I{slash}O Interface/DEBUG_SWDIO` | `(115.675, 41.250)` | `(117.400, 41.250)` | `1.73` |
| 47 | in | `Net-(U6-VCAP_2)` | `(115.675, 40.750)` | `(112.650, 40.550)` | `3.03` |
| 48 | out | `+3.3V` | `(115.675, 40.250)` | `(117.400, 39.700)` | `1.81` |
| 49 | out | `/I{slash}O Interface/DEBUG_SWCLK` | `(113.750, 38.325)` | `(114.300, 36.650)` | `1.76` |
| 50 | out | `/I{slash}O Interface/GPIO_7` | `(113.250, 38.325)` | `(113.500, 35.550)` | `2.79` |
| 51 | out | `/Microcontroller Interface/SPI_SCK` | `(112.750, 38.325)` | `(112.750, 36.650)` | `1.68` |
| 52 | out | `/Microcontroller Interface/SPI_MISO` | `(112.250, 38.325)` | `(112.000, 35.550)` | `2.79` |
| 53 | in | `/Microcontroller Interface/SPI_MOSI` | `(111.750, 38.325)` | `(111.550, 41.350)` | `3.03` |
| 54 | out | `/Microcontroller Interface/nFAULT` | `(111.250, 38.325)` | `(111.250, 36.650)` | `1.68` |
| 55 | in | `/I{slash}O Interface/GPIO_8` | `(110.750, 38.325)` | `(110.750, 40.050)` | `1.72` |
| 56 | out | `/I{slash}O Interface/ENC0_A` | `(110.250, 38.325)` | `(110.250, 35.550)` | `2.78` |
| 57 | out | `/I{slash}O Interface/ENC0_B` | `(109.750, 38.325)` | `(109.500, 36.650)` | `1.69` |
| 58 | in | `/I{slash}O Interface/ENC1_A` | `(109.250, 38.325)` | `(109.450, 41.350)` | `3.03` |
| 59 | in | `/I{slash}O Interface/ENC1_B` | `(108.750, 38.325)` | `(108.750, 40.050)` | `1.72` |
| 60 | out | `/I{slash}O Interface/BOOT0` | `(108.250, 38.325)` | `(108.000, 36.650)` | `1.69` |
| 61 | in | `/I{slash}O Interface/CAN_R` | `(107.750, 38.325)` | `(107.300, 40.050)` | `1.78` |
| 62 | out | `/I{slash}O Interface/CAN_D` | `(107.250, 38.325)` | `(107.250, 35.550)` | `2.78` |
| 63 | out | `GND` | `(106.750, 38.325)` | `(106.500, 36.650)` | `1.69` |
| 64 | out | `+3.3V` | `(106.250, 38.325)` | `(105.300, 35.550)` | `2.93` |
