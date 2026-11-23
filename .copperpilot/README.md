# Open Drive — CopperPilot Project Index

## Saved Hardware Revisions

| Revision | Path | Outline | Power Stage | Status |
|---|---|---|---|---|
| `v8.3` | `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.*` | `150.0 x 98.5 mm` | `IRF7480MTRPBF` (`DirectFET_ME`) | Promoted snapshot (`0` ERC errors, `0` copper DRC errors) |
| `v9.0` | `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.*` | `150.0 x 98.5 mm` (Unit 1) | `IRF7759L2TRPBF` (`DirectFET_L8`, `C520641`) | Unit 1 schematic + parity baseline (`d4c42c4`) |
| `v9.1` | `bldc_motor_cntroller_v9.1/bldc_motor_cntroller_v9.1.*` | `180.0 x 115.0 mm` | `1 x 6` `DirectFET_L8`, inline `2512` shunts | Units 2–4 promoted (`5ba6300`: 82 power-stage nets routed, `100%` solid `In1.Cu` `GND`) |
| `v9.2` | `bldc_motor_cntroller_v9.2/bldc_motor_cntroller_v9.2.*` | `220.0 x 115.0 mm` | Spread 3-leg `DirectFET_L8`, `7–12.7 mm` phase pours, aligned `MR60PB-M` (`J1`/`J2`), north-edge `J5–J11`/`SW1` | Promoted (`01602f0`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9.3` | `bldc_motor_cntroller_v9.3/bldc_motor_cntroller_v9.3.*` | `220.0 x 115.0 mm` | Frozen snapshot of verified `v9.2` 3-leg power stage | Promoted (`7697cb6`: `0` ERC/copper-DRC/parity/overlap errors) |
| `v9_4` | `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.*` | `220.0 x 115.0 mm` | `6 x 10` (`60x 1206`) phase-leg `VDC` banks, aligned `H1 (5.5, 92.0)` / `H3 (214.5, 92.0)` heatsink end holes, unobstructed `>= 5.42 mm` North + inter-FET heatsink keepout | Units 1 & 2 promoted (`a00d642`: `0` ERC/DRC/parity/overlap errors, `100%` solid `In1.Cu` `GND` under FETs) |
| `v9_5` | `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.*` | `220.0 x 115.0 mm` | `v9_4` heatsink & `6 x 10` cap layout + Unit 3 power-stage routing + `U6` outward fanout rework | Promoted (`18e918c`: `0` DRC/parity errors, `0` tracks/vias under `U6`) |
| `v9_6` | `bldc_motor_cntroller_v9_6/bldc_motor_cntroller_v9_6.*` | `220.0 x 115.0 mm` | `U6` STM32 routing (`1,093` segments, `585` vias, `103` zones) | Promoted (`5c002c8`: `0` ERC/parity/overlap errors, `165` remaining unconnected) |
| `v9_7` | `bldc_motor_cntroller_v9_7/bldc_motor_cntroller_v9_7.*` | `220.0 x 115.0 mm` | `61x 1206` `CL31B106KBHNNNE` (`C89632`), `DORABO DB910-7.62-2P-GN-S` (`J12`) brake terminal, `100 V` `D2`, hybrid hardware VDC OVP | Promoted (`6ada9fa`: `0` ERC errors) |
| `v9_8` | `bldc_motor_cntroller_v9_8/bldc_motor_cntroller_v9_8.*` | `220.0 x 115.0 mm` | Upper-East brake/OVP layout + selective upper `In2.Cu` routing (`1,427` segments, `631` vias) | Promoted (`fdf506b`: `0` parity/overlap errors, `121` unconnected) |
| `v9_9` | `bldc_motor_cntroller_v9_9/bldc_motor_cntroller_v9_9.*` | `220.0 x 115.0 mm` | `In2.Cu`-focused routing (`1,565` segments, `107` on `In2.Cu`, `671` vias) | Promoted (`4cdfcef`: `0` parity/overlap errors, `84` unconnected) |
| `v9_10` / `v9_11` | `bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_11.*` | `220.0 x 115.0 mm` | `+4.0 mm` south-shifted power stage (`Q3–Q14` at `y = 96.0 mm`), `6x(2x5)` `1210` `4.7 uF 100 V` MLCCs, `12x` HS-drain `100 V` HF caps, `4x` `100 uF 100 V` SMD bulk cans (`C49–C52`), relocated `U9` bypass caps, re-annotated schematics & re-linked `329` PCB footprints | Promoted (`9e667d9` + current checkpoint: `0` overlaps, `0` keepout violations, `2` minor clearance errors, `227` unconnected across `58` nets; baseline in `.copperpilot/baseline_v9_10.rpt`) |

## Next Action
- Complete remaining routing on `bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_11.kicad_pcb` (`58` open nets / `227` unconnected items and `2` minor clearance errors documented in `.copperpilot/baseline_v9_10.rpt`).

## Key Engineering Notes & Plans
- `v9_11` DRC baseline report: `./.copperpilot/baseline_v9_10.rpt`
- `v9_10` bulk-cap placement review: `./.copperpilot/notes/v9_10_bulk_cap_placement_review.md`
- `v9_10` Unit 5 routing status & RCA: `./.copperpilot/notes/v9_10_unit5_routing_status_and_rca.md`
- `v9_9` `In2.Cu` routing summary: `./.copperpilot/notes/v9_9_in2_routing_summary.md`
- `v9_8` routing status & RCA: `./.copperpilot/notes/v9_8_finish_routing_rca.md`
- `v9_7` brake terminal & hybrid OVP plan: `./.copperpilot/plans/v9-7-brake-terminal-and-hw-ovp.plan.md`
- Active `v9_10` plan: `./.copperpilot/plans/v9-10-power-stage-shift-and-decoupling.plan.md`
