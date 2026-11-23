# `bldc_motor_cntroller_v9_12` Pass 2 Routing Status & RCA (12-Run Cap)

- **Staged candidate:** `.copperpilot/tmp/staging/v9_12_route_p2/candidate/bldc_motor_cntroller_v9_12/bldc_motor_cntroller_v9_12.kicad_pcb` (`0` `__CP_ISO_`/`CP_SKIP` leftovers).
- **Cumulative progress in `v9_12`:** `298 -> 241 (Pass 1) -> 216 (Pass 2)` unconnected items; `89 -> 55 -> 38` unconnected nets; `1,101 -> 1,340 -> 1,497` routed segments (`F.Cu`: `1,153`, `B.Cu`: `206`, `In2.Cu`: `138`, `In1.Cu`: `0`); `574 -> 591 -> 609` vias; `111` refilled zones.
- **Pass 2 geometric update:** Added `8` targeted `F.Cu` `VDC` zone cutout holes (`1.8 × 3.0 mm`, `y = 82.0..85.0 mm`) around gate-resistor Pad 1 (`R20`, `R21`, `R28`, `R33`, `R44`, `R45`, `R49`, `R54`) without disturbing `C_HF1–C_HF6` or `In1.Cu` `GND`.

## Newly 100% Routed in Pass 2 (`17` Nets)

| Category | Nets Completed in Pass 2 |
|---|---|
| Power-Stage Gates / Driver | `/Motor Driver/GH_C`, `/Motor_Driver2/GH_A`, `/Motor_Driver2/GL_B`, `/Motor_Driver2/DVDD`, `/Motor_Driver2/TEMP_SENSE_2`, `Net-(U7-RT_CLK)` |
| SPI / Brake / OVP / Core | `/Microcontroller Interface/SPI_MISO`, `OVP_IN_HI`, `U3_LI_DRV`, `Net-(U9-VCAP_2)` |
| IO / Encoders / SWD / CAN | `/I/O Interface/DEBUG_SWDIO`, `/I/O Interface/CAN_D`, `/I/O Interface/ENC0_Z`, `/I/O Interface/GPIO_1`, `/I/O Interface/GPIO_3`, `/I/O Interface/GPIO_4`, `/I/O Interface/GPIO_5` |
| Supply Reductions | `+3.3VA` (`10 -> 5`), `+5V` (`6 -> 2`), `GVDD` (`7 -> 4`) |

## Remaining `216` Unconnected Items (`38` Nets)

| Group | Unconnected Items | Unique Nets | Details |
|---|---|---|---|
| Plane ties (`GND`, `+3.3V`, `VDC`) | `144` (`67%`) | `3` | `GND` (`112`), `+3.3V` (`19`), `VDC` (`13`) — local SMD pad-to-plane via drops |
| Driver phase/shunt taps (`SH_*`, `SL_*`) | `29` | `10` | M0 `SL_C` (`5`), `SH_B` (`3`), `SH_C` (`3`), `SL_B` (`3`), `SH_A` (`2`); M1 `SH_B` (`3`), `SH_C` (`3`), `SL_B` (`3`), `SL_C` (`3`), `SH_A` (`2`) |
| Supply rails | `11` | `3` | `+3.3VA` (`5`), `GVDD` (`4`), `+5V` (`2`) |
| Remaining gate drives | `7` | `7` | M0 `GH_A`, `GL_B`, `GL_C`; M1 `GL_A`, `GH_B`, `GH_C`, `GL_C` |
| Remaining signals & buck | `25` | `15` | `Net-(D6-K)` (`6`), `M0_TEMP` (`3`), `M1_TEMP` (`2`), `Net-(U7-VSENSE)` (`2`), plus `1` each on `USB_DP`, `USB_J4_DP`, `nFAULT`, `nOCTW`, `ENC1_Z`, `GPIO_2`, `AUX_TEMP`, `OVP_IN_LI`, `DEBUG_SWCLK`, `GPIO_7`, `/Power Management/HS` |

## DRC Summary (Staged Pass 2, Post Zone Refill)

- **Courtyard / Outline Overlaps:** `0` (`329` footprints, `0` outside board).
- **Physical DRC Errors:** `5` minor clearance errors (`0.1570–0.1790 mm` vs `0.1600/0.1800 mm` at `J5.A6`, `C12`, `C13`, `R37`, `C114`), `0` shorts, `0` `zones_intersect`.
- **Schematic Parity:** `145` pre-existing `1210` footprint-prefix/MPN warnings unchanged (`0` missing/extra footprints, `0` net conflicts).

## Root Cause of Remaining Unconnected Nets & Options

1. **12-run per-board FreeRouting cap reached (`Runs 1–12`):** `SH_*`/`SL_*` driver taps and `GND`/`+3.3V` plane ties were not yet run in Pass 2 (`+3.3V` Run 12 dropped `200 -> 174` unconnected before reverting on 1 minor clearance error).
2. **Remaining 7 `GH_*/GL_*` gates (`R20–R54`):** Even with the `F.Cu` `VDC` cutout holes, `Gate_Drv` (`0.20 mm` W / `0.18 mm` Clr) crossing the `2×5` `1210` MLCC banks still prefers `B.Cu` under the `1210` caps where dense `VDC`/`GND` stitching vias narrow the corridor.
3. **Options:**
   - **Promote Pass 2 now** (`298 -> 216` unconnected, `51` nets completed across Pass 1 + Pass 2, `0` overlaps) and stop.
   - **Promote Pass 2 and run Pass 3** targeting `SH_*/SL_*` taps, remaining 7 gates/signals, and `+3.3V`/`GND` plane ties.
