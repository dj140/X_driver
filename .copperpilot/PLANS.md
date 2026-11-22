# Project Plans Index

## Active Plan
- **[V9_7 Brake Terminal Block, Upper-East Chopper Relocation, and Hybrid Hardware VDC OVP](./plans/v9-7-brake-terminal-and-hw-ovp.plan.md)** (`status: open`)
  - **Unit 1 (`unit-1-db910-footprint-and-brake-terminal-sch`)**: Verify `DORABO DB910-7.62-2P-GN-S` (`C395876`) mechanical drawing, create project-local `7.62 mm` 30 A footprint, replace `H5`/`H6` with `J12`, upgrade `D2` to `100 V` Schottky and `C52` to `470 nF 50 V`, and document off-board `VO RX24/150W-3R3` (`C22395400`) options.
  - **Unit 2 (`unit-2-hw-ovp-comparator-interlock-tvs-sch`)**: Add hybrid hardware VDC OVP in `power_management.kicad_sch` (`LM393BIDR` + `LM4040C25IDBZR` tripping at `48.86 V / 47.07 V`, `74LVC1G08`/`74LVC1G32` + `BAT54` `~400 ns` break-before-make shoot-through interlock on `U3.HI`/`U3.LI`, and `5.0SMDJ48A` TVS on `VDC`).
  - **Unit 3 (`unit-3-merge-and-verify-v9-7-schematic`)**: Merge Units 1–2 into staged `bldc_motor_cntroller_v9_7/power_management.kicad_sch`, clean up `R43–R48`/`C41` MPN mismatches, pass full-hierarchy 0-error ERC, and promote.
  - **Unit 4 (`unit-4-relocate-brake-chopper-and-place-upper-east`)**: Sync `v9_7` PCB in staging, place `J12` on Upper-East edge (`x=208.5..219.5, y=46..61.5`, East exit), relocate `Q13`/`Q14`/`U3`/passives to `x=180..206, y=40..59`, place OVP + `5.0SMDJ48A` adjacent, and verify `0` overlaps and `0` parity errors.
  - **Unit 5 (`unit-5-hs-vdc-copper-pours-routing-and-verification`)**: Extend `In2.Cu` `VDC` north, build short wide (`4–6 mm` long, `>= 6–8 mm` wide, `2 oz` `F.Cu`+`B.Cu`) `HS` pour and stitched `GND` return clear of the heatsink keepout, route brake/OVP nets via headless FreeRouting, refill zones, run DRC/ERC/3D audit, and promote `v9_7`.

## Completed Plans
- **[V9.0 DirectFET L8 Upgrade, 180x115 mm Board Expansion, and Power-Stage Copper Rework](./plans/v9-0-directfet-l8-rework.plan.md)** (`status: done`)
- **[V8 Schematic STM32 Pinout Restoration, PCB Parity, and ERC Cleanup](./plans/v8-schematic-parity-and-erc-cleanup.plan.md)** (`status: done`)
- **[Restore Removed Capacitors, Expand Board to 150x98.5 mm, and Place Large High-Power Copper Zones](./plans/pre-order-layout-and-thermistor-fixes.plan.md)** (`status: done`)
