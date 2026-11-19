# Open Drive v8.3 Staging Promotion Summary

## Promoted Files (`bldc_motor_cntroller/`)

| File | Size (Bytes) | SHA-256 Prefix |
| --- | --- | --- |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_pro` | 21,224 | `540e5b124be78b17` |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_prl` | 2,586 | `7fb9cddb1ba1ffeb` |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_dru` | 325 | `72c9bddf18ff4dcc` |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_sch` | 53,158 | `7d60580cc614d740` |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.3.kicad_pcb` | 3,050,550 | `f6ff8acfde4e9768` |

## What Is Included in `v8.3`

- Symmetrical M0/M1 power-stage layout with `C_HF1–C_HF6` high-frequency commutation capacitors, `100uF 50V` `1206` bulk capacitor banks, Kelvin shunt resistors (`R12`, `R16`, `R32`, `R36`) with net-ties (`NT1–NT8`), and FET thermistor dividers (`TH1`, `TH5`).
- Rebuilt high-current polygonal copper zones on `F.Cu` and `B.Cu` (`SH_A`, `SH_B`, `SH_C`, `SL_B`, `SL_C`, `VDC`, split quiet/shunt `GND` returns) over `In1.Cu` `GND` and `In2.Cu` `VDC`/`+3.3V` planes, all refilled.
- Guided FreeRouting Group 1 Kelvin current-sense (`SP1/SN1`, `SP2/SN2`) and gate-drive traces preserved alongside `0.60 / 0.30 mm` stitching via arrays (`0` vias inside FET pads) and upper-board baseline vias.
- `bldc_motor_cntroller_v8.2.*` and all shared schematic subsheets/libraries remain untouched.

## Verification Status on Promoted Primary Files

| Check | Status | Result Summary |
| --- | --- | --- |
| Parser / Courtyard Overlaps (`query_design`) | Pass | `0` courtyard or board-edge overlaps across all footprints |
| Schematic ERC (`run_erc`) | Pass (0 errors) | `0` errors, `477` pre-existing `endpoint_off_grid` warnings |
| Physical PCB DRC (`run_drc` copper/layout rules) | Work-in-progress | `0` physical copper/clearance/via/dangling DRC errors; `529` legacy silkscreen/library footprint warnings; `274` `unconnected_items` remaining for unrouted upper-board/MCU signal groups; `79` `schematic_parity` items (`G***` logos and `U1/U2` thermal jumper pads `V`) |
| Identity Baseline Diff | Pass | `0` newly introduced attribution or external strings vs `v8.2` |
| 3D Model Render Gate | Not run | Deferred until remaining signal groups and silkscreen cleanup complete |
