# Open Drive — CopperPilot Project Index

## Saved Hardware Revisions

| Revision | Path | Outline | Power Stage | Status |
|---|---|---|---|---|
| `v8.3` | `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.*` | `150.0 x 98.5 mm` | `IRF7480MTRPBF` (`DirectFET_ME`) | Promoted snapshot (`0` ERC errors, `0` copper DRC errors) |
| `v9.0` | `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.*` | `150.0 x 98.5 mm` (Unit 1) | `IRF7759L2TRPBF` (`DirectFET_L8`, `C520641`) | Unit 1 schematic + parity baseline (`d4c42c4`) |
| `v9.1` | `bldc_motor_cntroller_v9.1/bldc_motor_cntroller_v9.1.*` | `180.0 x 115.0 mm` | `1 x 6` `DirectFET_L8`, inline `2512` shunts | Units 2–4 promoted (`5ba6300`: 82 power-stage nets routed, `100%` solid `In1.Cu` `GND`) |
| `v9.2` | `bldc_motor_cntroller_v9.2/bldc_motor_cntroller_v9.2.*` | `220.0 x 115.0 mm` | Spread 3-leg `DirectFET_L8`, `7–12.7 mm` phase pours, aligned `MR60PB-M` (`J1`/`J2`), north-edge `J5–J11`/`SW1` | Promoted (`01602f0`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9.3` | `bldc_motor_cntroller_v9.3/bldc_motor_cntroller_v9.3.*` | `220.0 x 115.0 mm` | Frozen snapshot of verified `v9.2` 3-leg power stage | Promoted (`7697cb6`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9_4` | `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.*` | `220.0 x 115.0 mm` | Active branch from `v9.3` for heatsink keepout + aligned `H1`/`H3` + `10` `1206` caps/phase | Base branch committed (`7b2d16c`, `0` ERC/copper-DRC/parity/overlap errors); ready for Unit 1 & Unit 2 execution |

## Next Action in Fresh Chat Session

Execute [./.copperpilot/notes/v9_4_heatsink_h1_h3_execution_handoff.md](./.copperpilot/notes/v9_4_heatsink_h1_h3_execution_handoff.md) on `bldc_motor_cntroller_v9_4`:
1. **Unit 1 (Schematic)**: Keep `H1` & `H3` (`H2` & `H4` removed), set `motor_driver.kicad_sch` and `motor_driver2.kicad_sch` to `A3`, add `C103–C132` (`+30 x 1206` `100uF 50V` `GMK105CC6105MV-F` `VDC`-to-`GND` caps -> `10` caps per phase leg), verify `0` ERC errors, promote, and checkpoint.
2. **Unit 2 (PCB)**: Sync `C103–C132` and remove `H2`/`H4`, align `H1 (5.50, 92.00)` & `H3 (214.50, 92.00)` on the `y = 92.00 mm` FET centerline, keep `y = [81.60 .. 97.40 mm]` clear of all components except `Q1–Q12`/`H1`/`H3` (`>= 5.22 mm` North of FET courtyards / `5.95 mm` North of `0.70 mm`-tall `DirectFET_L8` cans, `0` parts between FETs) with component-keepout rule areas, place `6 x 10` `1206` phase banks + `SL_B`/`SL_C` `F.Cu` return strips for `C_HF2/3/5/6` + `VDC`/`GND` stitching vias, refill zones, verify `0` DRC/parity/overlap errors, promote, and checkpoint.

## Key Engineering Notes & Plans
- Handoff spec (`v9_4`): `./.copperpilot/notes/v9_4_heatsink_h1_h3_execution_handoff.md`
- Detailed `v9_4` spec: `./.copperpilot/notes/v9_4_heatsink_h1_h3_and_10cap_spec.md`
- `v9.3` snapshot summary: `./.copperpilot/notes/v9_3_snapshot_summary.md`
- `v9.2` 3-leg rework & north-edge connectors: `./.copperpilot/notes/v9_2_wide_power_stage_rework.md`
- `v9.0` IPC-2152, IC pad-gap, and 2D Laplace USB `90 Ohm` solver: `./.copperpilot/notes/v9_0_solver_and_netclass_synthesis.md`
- Original vs. `v9` track-width hierarchy: `./.copperpilot/notes/original_vs_v9_track_thicknesses.md`
- Active `v9` plan: `./.copperpilot/plans/v9-0-directfet-l8-rework.plan.md`
