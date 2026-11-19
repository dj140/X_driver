# `v9_5` Snapshot Summary (`bldc_motor_cntroller_v9_5/`)

## 1. Saved Artifacts
- `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pro`
- `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_prl`
- `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_dru`
- `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_sch` (plus standalone `motor_driver.kicad_sch`, `motor_driver2.kicad_sch`, `io_interface.kicad_sch`, `microcontroller_interface.kicad_sch`, `power_management.kicad_sch`)
- `bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb`
- Project-local symbol and footprint libraries (`bldc_motor_cntroller.kicad_sym`, `bldc_motor_cntroller.pretty`, `Connector_AMASS.pretty`, `MG-WDSON-8.pretty`, `Package_SON.pretty`, `fp-lib-table`, `sym-lib-table`)

All prior revisions (`v8.3`, `v9.0`, `v9.1`, `v9.2`, `v9.3`, and `bldc_motor_cntroller_v9_4/`) remain untouched.

## 2. Included Design Delta Over `v9_4`
- Preserves the `220.0 x 115.0 mm` 4-layer board outline, `H1` `(5.50, 92.00)` and `H3` `(214.50, 92.00)` FET-centerline heatsink mounting holes, `13` heatsink component-keepout zones (`>= 5.42 mm` North of `Q1-Q12` courtyards and `0` components between FETs), and `6 x 10` (`60` total) `1206` phase-leg bus capacitors (`C39-C77` + `C103-C132`).
- Includes the completed Unit 3 power-stage routing pass (`475` routed track segments, `457` vias, `97` refilled copper zones + `25` canonical keepout zones):
  - All `20` Kelvin shunt differential current-sense and amplifier output nets (`SP1/SN1`, `SP2/SN2`, `SO1/SO2`, `M0/M1_SO*`).
  - All `12` zero-via `0.50 mm` `F.Cu` lateral MOSFET gate traces (`Net-(Q1-G)` .. `Net-(Q12-G)`).
  - All `28` `DRV8301` gate-drive, bootstrap, and phase/shunt sense taps (`GH_*/GL_*`, `BST_*`, `SH_*/SL_*`, except 1 remaining connection on `/Motor Driver/SH_C`).
  - `DRV8301` local `AVDD`, `DVDD`, `GVDD`, charge-pump (`CP1/CP2`), buck (`BST_BK`, `RT_CLK`, `COMP`, `VSENSE`, `SS_TR`, `DTC`, `DC_CAL`), `+5V`, and `VDC` taps (only 3 power-stage items remain open across `+5V`, `/Motor Driver/SH_C`, and `VDC` alongside upper-board MCU/IO nets).
- Removed temporary FreeRouting via-shield/steering keepouts, restored the `13` heatsink footprint-keepouts, and refilled all copper zones.

## 3. Verification Status
| Check | Result | Notes |
|---|---|---|
| `run_erc` (`bldc_motor_cntroller_v9_5.kicad_sch`) | **PASS (`0` errors)** | `425` inherited legacy `endpoint_off_grid` warnings |
| `run_drc` (`bldc_motor_cntroller_v9_5.kicad_pcb`) | **`0` copper/rule errors, `0` parity errors** | `256` `unconnected_items` remain (down from `384` in `v9_4`); `466` legacy silk/library warnings |
| `query_design(what="overlaps")` | **PASS (`0` overlaps)** | `286` footprints, `0` courtyard overlaps, `0` parts outside `Edge.Cuts` |
| 3D Model Render Check | Inherited from `v9_4` (`DirectFET_L8`, `C_1206`) | Full-board final 3D sweep pending upper-board routing completion |

## 4. Open Engineering / BOM Caution
- Phase-leg `1206` capacitors (`C39-C77`, `C103-C132`) retain inherited schematic fields (`100uF 50V` / `GMK105CC6105MV-F`) that lack voltage derating for a `48 V` nominal bus; consolidate onto a `>= 75-100 V` X7R/X7S `1206` ceramic MPN before PCBA ordering.
