# Amass MR60PB-M 3-Pin Motor Phase Connector Upgrade (`J1` & `J2`)

## Summary of Changes Against Updated Board
The motor phase connectors `J1` (Motor 0) and `J2` (Motor 1) have been upgraded from horizontal `MR30PW-M` (`15A/30A`, `3.50 mm` pitch) to vertical **Amass `MR60PB-M`** (`30A continuous / 60A peak`, `5.50 mm` pitch) against the latest updated `bldc_motor_cntroller/bldc_motor_cntroller.kicad_pcb` (where `J3` is placed vertically at `(72.55, 107.5)` at `0°`).

| Item | Previous State | Updated State |
| :--- | :--- | :--- |
| **Part / MPN** | `MR30PW-M 15A (30A)` | `MR60PB-M 30A (60A)` (`MPN: MR60PB-M`) |
| **Footprint ID** | `Connector_AMASS:AMASS_MR30PW-M_1x03_P3.50mm_Horizontal` | `Connector_AMASS:AMASS_MR60PB-M_1x03_P5.50mm_Vertical` |
| **Pin Pitch & Geometry** | `3.50 mm` pitch, `2.1 mm` drills, `3.0 mm` pads + 2 mounting holes | `5.50 mm` pitch (`11.00 mm` outer span), `3.30 mm` drills, `4.80 mm` pads (`0.70 mm` inter-pad clearance), `21.60 mm × 9.80 mm` body |
| **Motor 0 (`J1`) PCB Pose** | `(106.0, 100.0)` at `180°` | `(111.5, 107.5)` at `180°` (aligned with `J3` at `y = 107.5 mm`) |
| **Motor 0 (`J1`) Pad Coordinates** | Pad 1 (`SH_A`): `(106.0, 100.0)`<br>Pad 2 (`SH_B`): `(109.5, 100.0)`<br>Pad 3 (`SH_C`): `(113.0, 100.0)` | Pad 1 (`SH_A`): `(111.5, 107.5)`<br>Pad 2 (`SH_B`): `(106.0, 107.5)`<br>Pad 3 (`SH_C`): `(100.5, 107.5)` |
| **Motor 1 (`J2`) PCB Pose** | `(44.0, 100.0)` at `180°` | `(49.5, 107.5)` at `180°` (aligned with `J3` at `y = 107.5 mm`) |
| **Motor 1 (`J2`) Pad Coordinates** | Pad 1 (`SH_A`): `(44.0, 100.0)`<br>Pad 2 (`SH_B`): `(47.5, 100.0)`<br>Pad 3 (`SH_C`): `(51.0, 100.0)` | Pad 1 (`SH_A`): `(49.5, 107.5)`<br>Pad 2 (`SH_B`): `(44.0, 107.5)`<br>Pad 3 (`SH_C`): `(38.5, 107.5)` |
| **DC Input (`J3`) PCB Pose** | `(72.55, 107.5)` at `0°` (preserved from updated board) | `(72.55, 107.5)` at `0°` (`GND` at `(67.1, 107.5)`, `VDC` at `(78.0, 107.5)`) |

## Clearance & Verification Summary
- **Courtyard & Edge Clearance**:
  - `J2` courtyard `[32.7, 102.1, 55.3, 112.9]` to `J3` courtyard `[61.7, 102.1, 83.4, 112.9]`: `6.40 mm` gap.
  - `J3` courtyard `[61.7, 102.1, 83.4, 112.9]` to `J1` courtyard `[94.7, 102.1, 117.3, 112.9]`: `11.30 mm` gap.
  - Bottom board edge (`y = 113.5 mm`) to `J1`/`J2`/`J3` courtyard bottom (`y = 112.9 mm`): `0.60 mm` courtyard margin (`1.10 mm` from physical housing edge `y = 112.4 mm`).
  - `query_design(what="overlaps")`: `0` courtyard overlaps, `0` parts outside board.
- **Schematic ERC (`run_erc`)**:
  - `0` violations on `J1` and `J2`; total project ERC count reduced from `662` to `661` (`46` pre-existing out-of-scope errors, `615` pre-existing out-of-scope warnings).
- **PCB DRC (`run_drc`)**:
  - `0` schematic parity errors on `J1` and `J2` (previously 4 parity mismatches on `J1`/`J2`).
  - `0` `silk_edge_clearance` warnings (`J1` and `J2` silkscreen references placed at `y = 101.0 mm` above the connector housings, matching `J3`).
  - Total PCB DRC violations reduced from `890` to `886` (`351` pre-existing out-of-scope errors, `535` pre-existing out-of-scope warnings; `499` unconnected items on the unrouted board).
- **3D Model Audit**:
  - Neither stock KiCad 10 `${KICAD10_3DMODEL_DIR}/Connector_AMASS.3dshapes` nor the project workspace contains a 3D model for `MR60PB-M` (only `XT60-F` and `XT60-M` exist); recorded as `missing_no_adequate_model` and verified via top-down 3D raytrace render (`.copperpilot/tmp/unit3_pcb_render_top.png`).
