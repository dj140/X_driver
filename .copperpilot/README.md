# Open Drive — CopperPilot Project Index

## Saved Hardware Revisions

| Revision | Path | Outline | Power Stage | Status |
|---|---|---|---|---|
| `v8.3` | `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.*` | `150.0 x 98.5 mm` | `IRF7480MTRPBF` (`DirectFET_ME`) | Promoted snapshot (`0` ERC errors, `0` copper DRC errors) |
| `v9.0` | `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.*` | `150.0 x 98.5 mm` (Unit 1) | `IRF7759L2TRPBF` (`DirectFET_L8`, `C520641`) | Unit 1 schematic + parity baseline (`d4c42c4`) |
| `v9.1` | `bldc_motor_cntroller_v9.1/bldc_motor_cntroller_v9.1.*` | `180.0 x 115.0 mm` | `1 x 6` `DirectFET_L8`, inline `2512` shunts | Units 2–4 promoted (`5ba6300`: 82 power-stage nets routed, `100%` solid `In1.Cu` `GND`) |
| `v9.2` | `bldc_motor_cntroller_v9.2/bldc_motor_cntroller_v9.2.*` | `220.0 x 115.0 mm` | Spread 3-leg `DirectFET_L8`, `7–12.7 mm` phase pours, aligned `MR60PB-M` (`J1`/`J2`), north-edge `J5–J11`/`SW1` | Promoted (`01602f0`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9.3` | `bldc_motor_cntroller_v9.3/bldc_motor_cntroller_v9.3.*` | `220.0 x 115.0 mm` | Frozen snapshot of verified `v9.2` 3-leg power stage | Promoted (`7697cb6`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9_4` | `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.*` | `220.0 x 115.0 mm` | `6 x 10` (`60x 1206`) phase-leg `VDC` banks, aligned `H1 (5.5, 92.0)` / `H3 (214.5, 92.0)` heatsink end holes, unobstructed `>= 5.42 mm` North + inter-FET heatsink keepout | Units 1 & 2 promoted (`0` ERC/DRC/parity/overlap errors, `100%` solid `In1.Cu` `GND` under FETs; `384` signal/tie items ready for FreeRouting) |

## Next Action
- Signal routing on `bldc_motor_cntroller_v9_4` via headless FreeRouting (`route --nets` per net group: `0.50 mm` zero-via `F.Cu` FET gates, `0.20 mm` driver/bootstrap taps, `0.16 mm` coupled Kelvin sense pairs, `90 Ohm` USB, and upper-board MCU/IO nets).

## Key Engineering Notes & Plans
- `v9_4` completion summary: `./.copperpilot/notes/v9_4_heatsink_and_10cap_completion.md`
- Handoff spec (`v9_4`): `./.copperpilot/notes/v9_4_heatsink_h1_h3_execution_handoff.md`
- Detailed `v9_4` spec: `./.copperpilot/notes/v9_4_heatsink_h1_h3_and_10cap_spec.md`
- `v9.3` snapshot summary: `./.copperpilot/notes/v9_3_snapshot_summary.md`
- `v9.2` 3-leg rework & north-edge connectors: `./.copperpilot/notes/v9_2_wide_power_stage_rework.md`
- `v9.0` IPC-2152, IC pad-gap, and 2D Laplace USB `90 Ohm` solver: `./.copperpilot/notes/v9_0_solver_and_netclass_synthesis.md`
- Original vs. `v9` track-width hierarchy: `./.copperpilot/notes/original_vs_v9_track_thicknesses.md`
- Active `v9` plan: `./.copperpilot/plans/v9-0-directfet-l8-rework.plan.md`
