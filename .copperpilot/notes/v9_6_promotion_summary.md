# `bldc_motor_cntroller_v9_6` Promotion Summary

- **Promoted Directory**: `bldc_motor_cntroller_v9_6/`
- **Source Checkpoint**: `.copperpilot/tmp/v9_6_ckpt_n_gpio8.kicad_pcb` + `.copperpilot/tmp/v9_6_pre_n_swd2b.kicad_pro` (clean, unshielded, refilled zones; prior revisions including `bldc_motor_cntroller_v9_5/` remain untouched)
- **Board Summary**:
  - Footprints: `286` (`0` courtyard overlaps, `0` outside board)
  - Segments: `1,093` (up from `488` in `v9_5`)
  - Vias: `585` (`0` vias and `0` tracks under `U6`)
  - Zones: `103` (refilled via `kicad-cli pcb drc --refill-zones --save-board`, including all `13` heatsink `footprints not_allowed` keepouts)

## Post-Promotion Verification (`kicad-cli` 10.0.8)

| Check | Result | Details |
|---|---|---|
| Schematic ERC (`bldc_motor_cntroller_v9_6.kicad_sch`) | **0 errors** | `425` legacy `endpoint_off_grid` warnings |
| Schematic Parity (`run_drc --schematic-parity`) | **0 errors** | `0` parity mismatches |
| Courtyard / Outline Overlaps (`query_design`) | **0 overlaps** | `220.0 x 115.0 mm` outline (`[0, 15]` to `[220, 130]`) |
| PCB DRC Violations | **3 clearance errors** (WIP) | `ENC0_Z` vs `R55.1` (`0.177 mm`), `+3.3VA` vs `U5.4` (`0.177 mm`), `+5V` vs `U4.2` (`0.172 mm`) vs `0.180 mm` rule; `475` warnings (`11` `via_dangling`, `1` `isolated_copper`, legacy silk/lib warnings) |
| Unconnected Items | **165 total** (`12` on `U6` pins) | Remaining `U6` pins: `GND` (`12/18`, `63`), `VBUS_S` (`22`), `M1_TEMP` (`20`), `AUX_TEMP` (`21`), `GPIO_3` (`16`), `GPIO_4` (`17`), `AUX_L` (`29`), `AUX_H` (`30`), `DEBUG_SWDIO` (`46`), `DEBUG_SWCLK` (`49`), `GPIO_7` (`50`) |
| 3D Render Check | Not run | Unchanged from `v9_4`/`v9_5` footprint/3D set |
