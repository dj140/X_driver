# Project Plans Index

## Active Plan
- **[V9.0 DirectFET L8 Upgrade, 180x115 mm Board Expansion, and Power-Stage Copper Rework](./plans/v9-0-directfet-l8-rework.plan.md)** (`status: open`)
  - **Unit 1 (`unit-1-v9-0-branch-and-irf7759l2-schematic`)**: Branch `bldc_motor_cntroller_v9.0` project and dedicated `motor_driver_v9.0` / `motor_driver2_v9.0` subsheets (keeping `v8.3` untouched), replace `Q1–Q12` with KiCad 10 `Transistor_FET:IRF7759L2` (`Package_DirectFET:DirectFET_L8`, LCSC `C520641`), normalize parity items, and pass `0`-error ERC.
  - **Unit 2 (`unit-2-expand-180x115-and-place-directfet-l8-stage`)**: Expand `Edge.Cuts` to `180.0 × 115.0 mm` (`[0.0, 15.0]..[180.0, 130.0]`), translate upper digital section (`+15.0 mm` X) preserving edge connectors/mounting holes, place `Q1–Q12` (`DirectFET_L8`, `-90°`) on `9.2 / 8.8 mm` pitch, and place inline vertical `2512` shunts `R16/R12` and `R36/R32` directly under `Q6/Q4` and `Q12/Q10` with `0` courtyard overlaps.
  - **Unit 3 (`unit-3-power-pours-vdc-cap-stitching-and-solid-in1-gnd`)**: Rebuild symmetric `F.Cu` (fast commutation over `0.11 mm` `In1.Cu`) and `B.Cu` (DC current-sharing) pours for `VDC`, `SH_A/B/C`, straight `5 mm` `SL_B/SL_C`, and split shunt/quiet `GND`; stitch `C16/C61/C64/C80` and `C35/C39/C40/C78` `VDC/GND` vias; keep `>95%` solid `In1.Cu` `GND` under FETs and within `3.5 mm` of `C_HF1–C_HF6`.
  - **Unit 4 (`unit-4-route-gate-kelvin-and-drv8301-power-nets`)**: Route zero-via `F.Cu` lateral gate traces (`Q1–Q12` `Pad 2` through the `2.55 mm` channel to `R_gate`), coupled differential Kelvin sense pairs (`SP1/SN1`, `SP2/SN2`), and `DRV8301` `PVDD1` (`pins 29, 53, 54`) + bootstrap/buck/bypass nets via headless FreeRouting with `0` copper DRC errors.
  - **Unit 5 (`unit-5-route-upper-mcu-io-and-final-v9-0-verification`)**: Route remaining USB, CAN, SPI3, PWM, encoder, thermistor, and brake-chopper signal groups over continuous `In1.Cu` `GND`, clean up `F.SilkS` designators (`"Rev v9.0"`), refill all zones, and verify `run_erc`, `run_drc`, and `DirectFET_L8` 3D STEP alignment.

## Superseded Plans
- **[V8.1 Snapshot, Footprint Normalization, Surgical Re-Placement, Full Re-Route, and Zero-DRC Completion](./plans/v8-1-zero-drc-placement-and-routing.plan.md)** (`status: open` — superseded by `v8.3` power-stage promotion and `v9.0` DirectFET L8 rework above)
- **[V8 Power-Stage Via Arrays, Netclass Rules, Signal Routing, and DFM Completion](./plans/v8-power-vias-routing-and-dfm-completion.plan.md)** (`status: open` — Units 1–3 promoted on `v8`)

## Completed Plans
- **[V8 Schematic STM32 Pinout Restoration, PCB Parity, and ERC Cleanup](./plans/v8-schematic-parity-and-erc-cleanup.plan.md)** (`status: done`)
- **[Restore Removed Capacitors, Expand Board to 150x98.5 mm, and Place Large High-Power Copper Zones](./plans/pre-order-layout-and-thermistor-fixes.plan.md)** (`status: done`)
