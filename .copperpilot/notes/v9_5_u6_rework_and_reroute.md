# STM32 (`U6`) Outward Fanout Relocation, Component Optimisation, and Track Re-Routing Plan (`v9_5`)

## 1. Scope & Physical Constraints
- **Target Board**: `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb` (`U6` `STM32F405RGTx`, `LQFP-64_10x10mm_P0.5mm` at `(110.00, 44.00)`, courtyard `[103.30, 37.30] .. [116.70, 50.70]`).
- **Under-MCU Exclusion Rules**:
  - `F.Cu` interior keepout `[105.35, 39.35] .. [114.65, 48.65]` (`tracks not_allowed`, `vias not_allowed`).
  - `B.Cu`, `In1.Cu`, `In2.Cu` full-courtyard keepout `[103.30, 37.30] .. [116.70, 50.70]` (`tracks not_allowed`, `vias not_allowed`, `copperpour allowed`).
  - `B.Cu` crystal guard keepout `[92.90, 39.75] .. [98.20, 43.65]` under `Y1` + `C83`/`C84`.
- **Outward Fanout Via Geometry (`64` vias, `0` under `U6`)**:
  - Staggered two-row outward rings at `3.13 .. 5.78 mm` from `U6` pad centers (`2.10 .. 4.00 mm` outside `U6` courtyard), `0.60 mm / 0.30 mm` (`0.15 mm` annular ring on `2 oz` outer copper), `>= 1.44 mm` non-USB center-to-center spacing preserving continuous `In1.Cu` (`GND`) and `In2.Cu` (`+3.3V`) plane webs, and a symmetric `1.05 mm` coupled pair on `USB_DN`/`USB_DP` (`Pins 44/45`).

## 2. Surgical Net-Group Routing Order
1. **Group 1 (`Sense` current-sense amplifier outputs previously routed under `U6` and attached to relocated filter bank `C6, C7, C28, C27` & `TP8–TP11`)**:
   - `/Microcontroller Interface/M0_SO1` (`R17.2` -> `C6.2` -> `TP8.1` -> `U6.8` + outward fanout via `(99.30, 43.62)`)
   - `/Microcontroller Interface/M0_SO2` (`R18.2` -> `C7.2` -> `TP9.1` -> `U6.9` + outward fanout via `(100.80, 44.38)`)
   - `/Microcontroller Interface/M1_SO2` (`R38.2` -> `TP11.1` -> `C28.2` -> `U6.10` + outward fanout via `(99.30, 45.14)`)
   - `/Microcontroller Interface/M1_SO1` (`R37.2` -> `TP10.1` -> `C27.2` -> `U6.11` + outward fanout via `(100.80, 45.90)`)
   - Constraint check: `0` segments or vias inside `U6` keepout `[103.30, 37.30] .. [116.70, 50.70]` or `Y1` keepout, `0` new DRC errors, `non_target_copper.status == unchanged`, `still_unconnected_nets == []`.
