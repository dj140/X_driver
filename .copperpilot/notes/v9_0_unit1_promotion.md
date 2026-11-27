# V9.0 Promotion Status (`unit-1-v9-0-branch-and-irf7759l2-schematic`)

## Where the Staged Files Were
The `v9.0` Unit 1 files from the interrupted run were sitting unpromoted inside `.copperpilot/tmp/staging/v9_0_unit1/candidate/bldc_motor_cntroller/`. That staging directory has now been verified, promoted into `bldc_motor_cntroller/`, and cleaned up.

## Promoted Real Files in `bldc_motor_cntroller/`
| File | Status / Role |
|---|---|
| `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.kicad_pro` | Standalone `v9.0` KiCad 10 project |
| `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.kicad_prl` | Standalone `v9.0` local settings |
| `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.kicad_dru` | Standalone `v9.0` custom design rules |
| `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.kicad_sch` | Root `v9.0` schematic (`rev "v9.0"`, pointing to `motor_driver_v9.0.kicad_sch` and `motor_driver2_v9.0.kicad_sch`) |
| `bldc_motor_cntroller/motor_driver_v9.0.kicad_sch` | Channel M0 subsheet (`Q1–Q6` upgraded to `Transistor_FET:IRF7759L2`, `Package_DirectFET:DirectFET_L8`, `MPN = IRF7759L2TRPBF`, `LCSC = C520641`; `U1` mapped to `bldc_motor_cntroller:DRV8301DCA_v9`) |
| `bldc_motor_cntroller/motor_driver2_v9.0.kicad_sch` | Channel M1 subsheet (`Q7–Q12` upgraded to `Transistor_FET:IRF7759L2`, `Package_DirectFET:DirectFET_L8`, `MPN = IRF7759L2TRPBF`, `LCSC = C520641`; `U2` mapped to `bldc_motor_cntroller:DRV8301DCA_v9`) |
| `bldc_motor_cntroller/bldc_motor_cntroller.pretty/DRV8301DCA_v9.kicad_mod` | Normalized `DRV8301DCAR` footprint (`32` thermal vias mapped as pad `57` jumpers) |
| `bldc_motor_cntroller/bldc_motor_cntroller_v9.0.kicad_pcb` | Seeded `v9.0` PCB with `G1–G8` silkscreen graphics normalized as `board_only` (`0` `duplicate_footprints`, `0` `extra_footprint`); **awaiting Unit 2–5 PCB rework** |

## Verification Summary
- **Schematic ERC (`run_erc`)**: **PASS** (`0` errors, `425` inherited `endpoint_off_grid` warnings on unchanged sheets).
- **Schematic Layout Audit (`validate_schematic_layout`)**: **PASS** (violations reduced from `38 -> 32` on `motor_driver_v9.0.kicad_sch` and `30 -> 24` on `motor_driver2_v9.0.kicad_sch`; `0` new collisions).
- **PCB DRC (`run_drc`)**: **Work-in-progress baseline** (`0` physical copper DRC errors, `0` `duplicate_footprints` / `extra_footprint`; `198` `Q1–Q12` / `U1–U2` footprint-sync parity items and `274` unconnected upper-board items remain until Unit 2–5 PCB execution).
- **3D Model Check**: Not yet run (scheduled in Unit 2 / Unit 5 once `DirectFET_L8` footprints are synced onto the expanded `180 x 115 mm` PCB).
- **`v8.3` & Shared Subsheet Isolation**: Verified unchanged SHA-256 hashes on all `bldc_motor_cntroller_v8.3.*` files and shared subsheets (`motor_driver.kicad_sch`, `motor_driver2.kicad_sch`, `io_interface.kicad_sch`, `microcontroller_interface.kicad_sch`, `power_management.kicad_sch`).

## Remaining Plan Units (`v9-0-directfet-l8-rework.plan.md`)
- **Unit 2**: Sync `DirectFET_L8` (`Q1–Q12`) & `DRV8301DCA_v9` (`U1–U2`) onto `bldc_motor_cntroller_v9.0.kicad_pcb`, expand `Edge.Cuts` to `180.0 x 115.0 mm`, re-pitch both 6-FET banks (`9.2 / 8.8 mm`), and place inline Phase B/C shunts (`R16/R12`, `R36/R32`).
- **Unit 3**: Rebuild symmetric `F.Cu` / `B.Cu` power pours (`SL_B` straight `5 mm` pours, stitched `C16/C61/C64/C80` & `C35/C39/C40/C78` `VDC` caps, `>95%` solid `In1.Cu` `GND` under FETs and `C_HF1–C_HF6`).
- **Unit 4**: Route zero-via `F.Cu` lateral gate traces, coupled Kelvin sense pairs, and `DRV8301` `PVDD1` / bootstrap / buck nets.
- **Unit 5**: Route remaining upper MCU/IO signals, clean up silkscreen (`Rev v9.0`), and run final ERC/DRC/3D verification.
