# `bldc_motor_cntroller_v9_8` Promoted Snapshot Summary

## Source & Scope
- **Source**: Promoted from the latest staged `v9_7` Unit 5 candidate (`.copperpilot/tmp/staging/v9_7_pcb_unit5/candidate/bldc_motor_cntroller_v9_7/`) into standalone `bldc_motor_cntroller_v9_8/` with updated project stems (`bldc_motor_cntroller_v9_8.{kicad_pro,kicad_prl,kicad_dru,kicad_sch,kicad_pcb}`) and `(rev "v9_8")` title-block metadata.
- **Unchanged Revisions**: `bldc_motor_cntroller_v9_7/` and all earlier revisions remain untouched.

## Board & Schematic Contents
| Metric | Value |
|---|---|
| Board Outline | `220.0 × 115.0 mm` (`x = 0..220`, `y = 15..130`) |
| Footprints | `307` (`0` courtyard overlaps, `0` outside board) |
| Routed Segments | `1,266` |
| Vias | `609` |
| Refilled Copper Zones | `121` (refilled via `kicad-cli pcb drc --refill-zones --save-board`) |

## Post-Promotion Verification (`bldc_motor_cntroller_v9_8/`)
| Check | Result | Details |
|---|---|---|
| `run_erc` | **0 errors** | `420` warnings (`418` legacy `endpoint_off_grid`, `2` `multiple_net_names` on `OVP_IN_HI`/`CTRL_HI`) |
| `run_drc` (Schematic Parity) | **0 errors** | `0` schematic parity violations |
| `query_design(what="overlaps")` | **0 overlaps** | `0` courtyard overlaps, `0` parts outside board |
| `run_drc` (Copper / Rules) | **11 errors** (WIP) | `8` minor clearance (`0.1588–0.1770 mm` at `U4`, `U5`, `R55`, `U1`, `ENC0_Z/GPIO_6`, `M1_CH/M1_BH`, `M0_SO1/M0_SO2`); `3` `zones_intersect` on inner planes (`In1.Cu` `GND`, `In2.Cu` `+3.3V` & `VDC`) |
| `run_drc` (Connectivity) | **150 unconnected** (WIP) | Remaining unrouted upper-board / brake-OVP / `GND` tie items |
| 3D Model Render Audit | **Not run** | Deferred for this work-in-progress snapshot |
