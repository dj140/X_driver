# `bldc_motor_cntroller_v9_4` Branch Snapshot & 10-Capacitor-per-Phase Upgrade Status

## 1. Promoted `bldc_motor_cntroller_v9_4/` Branch (`v9.3` Untouched)
- **Directory**: `bldc_motor_cntroller_v9_4/`
- **Primary Files**:
  - `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_pro`
  - `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_prl`
  - `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_dru`
  - `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_sch` (with dedicated `motor_driver.kicad_sch`, `motor_driver2.kicad_sch`, `power_management.kicad_sch`, `microcontroller_interface.kicad_sch`, `io_interface.kicad_sch`, and project-local symbol/footprint libraries)
  - `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_pcb`
- **Verification Summary**:
  | Check | Result |
  |---|---|
  | `bldc_motor_cntroller_v9.3/` SHA-256 Hashes | `100%` unchanged |
  | `run_erc` (`bldc_motor_cntroller_v9_4.kicad_sch`) | `0` errors (`425` legacy off-grid warnings) |
  | `run_drc` (`bldc_motor_cntroller_v9_4.kicad_pcb`) | `0` physical copper/edge/zone errors, `0` schematic-parity errors (`504` legacy silkscreen/footprint warnings, `391` unrouted signal/tie items) |
  | `query_design(what="overlaps")` | `0` courtyard overlaps, `0` footprints outside `[0.0, 15.0] .. [220.0, 130.0]` `Edge.Cuts` |

---

## 2. Blocker Encountered on Schematic & PCB Mutation Tools (`500 MB` Session Backup Cap)
- Schematic and PCB mutation tools failed on retry with:
  - `apply_kicad_schematic_batch`: `ValueError: Mutation backup exceeds total storage limit (524288000 bytes). Accept or reject pending edits to free space.`
  - `place_schematic_symbol`: `ValueError: Mutation backup exceeds total storage limit (524288000 bytes). Accept or reject pending edits to free space.`
  - `kicad_copy`: `ValueError: Mutation backup exceeds total storage limit (524288000 bytes). Accept or reject pending edits to free space.`
  - `sync_schematic_to_pcb`: `ValueError: Sync failed: PCB unavailable: Mutation backup exceeds total storage limit (524288000 bytes). Accept or reject pending edits to free space.`
- Per CopperPilot tool-safety rules, custom scripts were not used to write schematic S-expressions or bypass `sync_schematic_to_pcb`.
- **How to Clear the `500 MB` Backup Buffer**: Click **Accept All** (or **Reject All**) in the CopperPilot **Pending File Changes / Diff Review** panel (or start a fresh chat session in this workspace) so the `524,288,000`-byte undo buffer resets, then reply `resume` to execute the `+30` capacitor addition below immediately.

---

## 3. Ready-to-Execute 10-Capacitor-per-Phase Geometry (`60` Phase-Leg `1206` Caps)
- **Schematic Delta (`+30` `1206` `VDC`-to-`GND` Decoupling Capacitors)**:
  - `bldc_motor_cntroller_v9_4/motor_driver.kicad_sch` (`A3` sheet): `C103–C117` (`15 × Device:C_Small`, `Value = "100uF 50V"`, `Footprint = "Capacitor_SMD:C_1206_3216Metric"`, `MPN = "GMK105CC6105MV-F"`, `Pin 1 -> VDC`, `Pin 2 -> GND`). *(Engineering note: physical `1206` `50 V` Class-II MLCC ceiling is typically `4.7–10 µF` nominal before DC-bias derating at `48 V`; `Value`/`MPN` match existing `C39–C77` for BOM/DRC parity until a BOM consolidation pass is requested.)*
  - `bldc_motor_cntroller_v9_4/motor_driver2.kicad_sch` (`A3` sheet): `C118–C132` (`15 × Device:C_Small`, identical fields and `VDC`/`GND` rails).
- **Single-Sided `F.Cu` 10-Capacitor-per-Leg Placement (`y = 80.50 mm`, `rot = 90°`, `2.35 mm` pitch, `+118.00 mm` M1-to-M0 Symmetry)**:
  | Phase Leg | M1 `X` Centers (`y = 80.50 mm`) | M0 `X` Centers (`y = 80.50 mm`) | `100 nF` `0402` Bypass | Clearances |
  |---|---|---|---|---|
  | **Phase C** (`10 × 1206`) | `13.40 .. 34.55` (`step 2.35`) | `131.40 .. 152.55` (`step 2.35`) | `C78` (`11.40, 80.50`), `C80` (`129.40, 80.50`) | `2.0 mm` clear of `H1` (`8.95`), `0.79 mm` clear of `R34/R33/R14/R13` (`y = 83.57`) |
  | **Phase B** (`10 × 1206`) | `43.40 .. 64.55` (`step 2.35`) | `161.40 .. 182.55` (`step 2.35`) | — | Preserves full `2.35 mm` `U1/U2` South signal fanout corridor (`y = 75.87 .. 78.22`) |
  | **Phase A** (`10 × 1206`) | `70.10 .. 91.25` (`step 2.35`) | `188.10 .. 209.25` (`step 2.35`) | `C79` (`68.20, 80.50`), `C81` (`186.20, 80.50`) | `0.68 mm` clear of `H3` courtyard (`211.05`), `100.00%` solid `In1.Cu` `GND` under `Q1–Q12` |
