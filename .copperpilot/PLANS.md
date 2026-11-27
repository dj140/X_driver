# Project Plans Index

## Active Plan
- **[V9_10 South-Shift Power Stage, 100 V 1210/HF/Bulk Decoupling, U6/DRV/USB Bypass, and Full Routing](./plans/v9-10-power-stage-shift-and-decoupling.plan.md)** (`status: open`)
  - **Unit 1 (`unit-1-v9-10-branch-and-power-stage-100v-sch`)**: Branch `bldc_motor_cntroller_v9_10` from `v9_9`, upgrade all 61 `VDC` `1206` caps to `4.7 µF 100 V X7R 1210` (`GRM32ER72A475KE14L`, `C162515`), add 12× per-half-bridge `100 V` HF caps (`6× 100 nF 0603` + `6× 1 µF 0805`) and 4× `DRV8301` `VDD_SPI`/`REF` `100 nF 0402` caps, and pass 0-error unit ERC.
  - **Unit 2 (`unit-2-j3-bulk-caps-and-usb-vbus-sch`)**: Add 4× `100 µF 100 V` SMD bulk caps (`HV1K107M1010PZ`, `C42436546`, `CP_Elec_10x10.5`) near `J3` and USB `J4` VBUS protection/decoupling (`SMF5.0A` + `4.7 µF 25 V 0805` + `100 nF 0402`), run full-hierarchy ERC + review sweep, and promote `v9_10` schematics.
  - **Unit 3 (`unit-3-south-shift-1210-banks-hf-and-j3-bulk-pcb`)**: Sync `v9_10` PCB in staging, shift `Q1–Q12`, `H1/H3`, heatsink keepouts, `C_HF1–6`, gate resistors, NTCs, and shunts `+4.0 mm` south (`y = 96.0`), place `6×(2×5)` `1210` banks, 12× HS-drain HF caps, and 4× `10×10.5 mm` bulk cans around `J3`, rebuild pours (`>95%` `In1.Cu` `GND`), and verify `0` overlaps/parity.
  - **Unit 4 (`unit-4-u6-bypass-drv-and-usb-vbus-placement-pcb`)**: Relocate all 9 `U6` bypass/VCAP `0402` caps within `<= 2.0 mm` of pins `1/13/19/31/32/47/48/64` with dedicated `GND` vias, place 4× `DRV8301` `VDD_SPI`/`REF` and USB `J4` VBUS parts, and verify `0` overlaps/parity.
  - **Unit 5 (`unit-5-full-routing-drc-and-3d-verification`)**: Route all shifted/added nets plus the remaining `84` `v9_9` unconnected items (and clear `7` minor clearance errors) via headless FreeRouting with selective upper `In2.Cu`, refill zones, pass 0-error ERC/DRC/3D audit, and promote `bldc_motor_cntroller_v9_10`.

## Completed Plans
- **[V9_7 Brake Terminal Block, Upper-East Chopper Relocation, and Hybrid Hardware VDC OVP](./plans/v9-7-brake-terminal-and-hw-ovp.plan.md)** (`status: done`)
- **[V9.0 DirectFET L8 Upgrade, 180x115 mm Board Expansion, and Power-Stage Copper Rework](./plans/v9-0-directfet-l8-rework.plan.md)** (`status: done`)
- **[V8 Schematic STM32 Pinout Restoration, PCB Parity, and ERC Cleanup](./plans/v8-schematic-parity-and-erc-cleanup.plan.md)** (`status: done`)
- **[Restore Removed Capacitors, Expand Board to 150x98.5 mm, and Place Large High-Power Copper Zones](./plans/pre-order-layout-and-thermistor-fixes.plan.md)** (`status: done`)
