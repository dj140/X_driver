# V8 Schematic Promotion and Parity Verification

## 1. Promoted Files (`bldc_motor_cntroller/`)

| File | SHA-256 (12-char) | Role / Update |
|---|---|---|
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_sch` | `bc83ba94377d` | New top-level root schematic for `bldc_motor_cntroller_v8` cloned from `bldc_motor_cntroller.kicad_sch` with `(project "bldc_motor_cntroller_v8" ...)` sheet and symbol instances added alongside `bldc_motor_cntroller`. |
| `bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_pro` | `4ac6d657dd9a` | Updated `schematic.top_level_sheets` from missing `bldc_motor_cntroller_v7.kicad_sch` to `bldc_motor_cntroller_v8.kicad_sch`. |
| `bldc_motor_cntroller/microcontroller_interface.kicad_sch` | `6d053e1be82b` | Added 29 `(project "bldc_motor_cntroller_v8" ...)` symbol instance bindings (includes `U6.12 VSSA -> GND`, `C83/C84` 12 pF resonator caps, `M0_TEMP2`/`M1_TEMP2` ADC pins). |
| `bldc_motor_cntroller/io_interface.kicad_sch` | `58a2600955c9` | Added 61 `(project "bldc_motor_cntroller_v8" ...)` symbol instance bindings (includes `U8` `USBLC6-2SC6` flow-through USB ESD and `R64`/`R65` 5.1 kOhm `CC1`/`CC2` pull-downs). |
| `bldc_motor_cntroller/motor_driver.kicad_sch` | `09de9d1ad410` | Added 109 `(project "bldc_motor_cntroller_v8" ...)` symbol instance bindings (includes `J1` `MR60PB-M`, `TH4`/`R62`/`C101`, and `C_HF1`–`C_HF3` 470 nF 100 V HF commutation caps). |
| `bldc_motor_cntroller/motor_driver2.kicad_sch` | `e2a64b677ad4` | Added 84 `(project "bldc_motor_cntroller_v8" ...)` symbol instance bindings (includes `J2` `MR60PB-M`, `TH5`/`R63`/`C102`, `C_HF4`–`C_HF6`) and renumbered duplicate `#PWR307` (`uuid 9a4d6815-d420-4f5b-bb51-7cd036586ae0`) to `#PWR311`. |
| `bldc_motor_cntroller/power_management.kicad_sch` | `5c799a41f449` | Added 96 `(project "bldc_motor_cntroller_v8" ...)` symbol instance bindings (includes 29x `100uF 50V` `1206` bus caps `C39–C77` and `C_AUX1`). |

`bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_pcb` (`44bf46181547`) was not modified during schematic promotion.

## 2. Verification Summary (`kicad-cli` 10.0.8)

| Check | Result | Notes |
|---|---|---|
| Netlist export (`bldc_motor_cntroller_v8.kicad_sch`) | **PASS** (`237` components, `177` nets, `0` annotation warnings) | Duplicate `#PWR307` warning eliminated; `0` unannotated `?` references. |
| Schematic ERC (`run_erc`) | `31` baseline errors, `610` baseline warnings (`0` new) | Unchanged from `bldc_motor_cntroller.kicad_sch` baseline (`19` `power_pin_not_driven`, `4` `pin_not_connected`, `4` `pin_not_driven`, `3` `pin_to_pin`, `1` `hier_label_mismatch` on unused `PWRGD` sheet pin). |
| Schematic layout audit (`validate_schematic_layout`) | `125` legacy root-sheet items (`0` new) | Unchanged pre-existing root-sheet graphical/bus wire endpoints. |
| PCB DRC + Schematic Parity (`run_drc` on `_v8.kicad_pcb`) | `parity_checked: true` (`0` electrical net conflicts) | All `237` schematic components match `_v8.kicad_pcb` (`+8` `G***` silk graphics + `4` `H7–H10` M4 corner holes = `249` PCB footprints; the `64` reported `net_conflict` warnings are the `64` `PTH pad V [GND]` thermal vias inside `U1`/`U2` library footprints). Note: `_v8.kicad_pcb` currently has `8` stale zone-fill clearances from recent component moves in PCBNew that clear on `fill_pcb_zones`, and `265` unrouted connections (`0` routed trace segments). |
| Pre-order BOM / voltage safety reminder | **OPEN** | `GMK105CC6105MV-F` on `1206` caps `C39–C77` is an `0402` `1 uF` `35 V` MPN and must be replaced with a valid `>= 50 V` `1206` MLCC + external/radial bulk damping; `IRF7480MTRPBF` (`Q1–Q12`) is `40 V` rated (`<= 30 V` bus recommended, or `60 V` `IRF7580MTRPBF` for `36 V` max bus). |
