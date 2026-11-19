# `bldc_motor_cntroller_v9_4` Specification: Heatsink Clearance (`>= 5 mm` North & Inter-FET), Aligned `H1`/`H3` End Mounting Holes, and 10-Cap-per-Phase Upgrade

## 1. Confirmed User Decisions & Mechanical Constraints

- **Target Project**: `bldc_motor_cntroller_v9_4/` (`220.0 × 115.0 mm`, `Edge.Cuts` `[0.0, 15.0] .. [220.0, 130.0]`, `v9.3` untouched).
- **Single Aligned Heatsink Mounting Hole at Each End of the FET Row**:
  - **Keep `H1` and `H3`** (`MountingHole:MountingHole_3.2mm_M3_Pad_Via`, tied to `GND`); **delete `H2` and `H4`** in both `bldc_motor_cntroller_v9_4.kicad_sch` and `bldc_motor_cntroller_v9_4.kicad_pcb`.
  - **Left End (`H1`)**: `(5.50, 92.00, 0°)` (`F.CrtYd` `[2.05, 88.55, 8.95, 95.45]`), exact `y = 92.00 mm` centerline alignment with `Q12–Q1` (`6.82 mm` clear of `Q12` courtyard).
  - **Right End (`H3`)**: `(214.50, 92.00, 0°)` (`F.CrtYd` `[211.05, 88.55, 217.95, 95.45]`), exact `y = 92.00 mm` centerline alignment with `Q12–Q1` (`0.32 mm` courtyard / `1.25 mm` copper clearance to `Q2`).
- **Unobstructed Heatsink Envelope ("between and 5 mm above the FETs")**:
  - `DirectFET_L8` (`Q1–Q12` at `y = 92.00 mm`, `rot = -90°`) has metal body `y = 87.425 .. 96.575 mm` (`0.70 mm` max height), pads `y = 86.950 .. 97.050 mm`, and courtyard `y = 86.700 .. 97.300 mm`.
  - **Component-Free Heatsink Band**: `y = [81.60 .. 97.40 mm]` across `x = [1.00 .. 219.00 mm]` contains **only `Q1–Q12`, `H1`, and `H3`**.
  - All relocated components North of the FET row have `courtyard max_y <= 81.48 mm` (**`5.22 mm` North of FET courtyards**, **`5.47 mm` North of FET pads**, and **`5.945 mm` North of FET metal cans**), with **zero components in any inter-FET gap**.

---

## 2. Schematic Delta (`bldc_motor_cntroller_v9_4`)

| Sheet | Exact Operations |
|---|---|
| `bldc_motor_cntroller_v9_4.kicad_sch` | Delete wires `(195.58, 132.08)–(200.66, 132.08)`, `(200.66, 132.08)–(205.74, 132.08)`, `(205.74, 132.08)–(210.82, 132.08)` and extra junctions at `(200.66, 132.08)` / `(205.74, 132.08)`; delete symbols `H2` and `H4`; draw wire `(195.58, 132.08)–(205.74, 132.08)` connecting `H1.1` and `H3.1` to `#PWR0131` (`GND`). |
| `motor_driver.kicad_sch` | Set paper to `A3`; place `C103–C117` (`15 × Device:C_Small`, `Value = "100uF 50V"`, `Footprint = "Capacitor_SMD:C_1206_3216Metric"`, `MPN = "GMK105CC6105MV-F"`) wired between `VDC` and `GND` (+5 caps per M0 phase leg -> 10 per leg). |
| `motor_driver2.kicad_sch` | Set paper to `A3`; place `C118–C132` (`15 × Device:C_Small`, `Value = "100uF 50V"`, `Footprint = "Capacitor_SMD:C_1206_3216Metric"`, `MPN = "GMK105CC6105MV-F"`) wired between `VDC` and `GND` (+5 caps per M1 phase leg -> 10 per leg). |

---

## 3. PCB Placement & Copper Delta (`bldc_motor_cntroller_v9_4.kicad_pcb`)

### 3.1 Mounting Holes & Driver `-5.00 mm` Y Translation

| Group | Refs | Target Coordinates / Delta |
|---|---|---|
| Heatsink End Holes | `H1`, `H3` (`H2`, `H4` deleted) | `H1 = (5.50, 92.00, 0°)`, `H3 = (214.50, 92.00, 0°)` |
| M1 `DRV8301` Cluster | `U2`, `C22–C26`, `C29–C34`, `C38`, `R26`, `R27`, `R30`, `R37–R40`, `R42`, `TH2` | Shift `Δy = -5.00 mm` (`U2 -> 55.00, 63.50, -90°`; south `0402` row at `y = 70.40 mm`, `max_y = 70.87 mm`) |
| M0 `DRV8301` + Buck Cluster | `U1`, `L1`, `D1`, `C1–C5`, `C8–C15`, `C17–C20`, `C36`, `C101`, `R3–R7`, `R10`, `R17–R22`, `R62`, `TH4` | Shift `Δy = -5.00 mm` (`U1 -> 173.00, 63.50, -90°`; `L1 -> 190.40, 64.50`; south `0402` row at `y = 70.40 mm`, `max_y = 70.87 mm`) |

### 3.2 Six 10-Capacitor `1206` Phase-Leg Banks (`y = 75.80 mm`, `rot = 90°`, Courtyard `y = 73.52 .. 78.08 mm`)

| Phase Leg | Refs (`10 × 1206` per leg) | `X` Centers (`2.35 mm` pitch) | Local `100 nF` `0402` |
|---|---|---|---|
| **M1 Phase C** | `C35, C39, C40, C42, C44, C118, C119, C120, C121, C122` | `13.40, 15.75, 18.10, 20.45, 22.80, 25.15, 27.50, 29.85, 32.20, 34.55` | `C78 (11.40, 75.80, 90°)` |
| **M1 Phase B** | `C45, C46, C47, C51, C54, C123, C124, C125, C126, C127` | `43.40, 45.75, 48.10, 50.45, 52.80, 55.15, 57.50, 59.85, 62.20, 64.55` | — |
| **M1 Phase A** | `C55, C57, C60, C56, C53, C128, C129, C130, C131, C132` | `70.10, 72.45, 74.80, 77.15, 79.50, 81.85, 84.20, 86.55, 88.90, 91.25` | `C79 (68.20, 75.80, 90°)` |
| **M0 Phase C** | `C16, C61, C64, C65, C66, C103, C104, C105, C106, C107` | `131.40, 133.75, 136.10, 138.45, 140.80, 143.15, 145.50, 147.85, 150.20, 152.55` | `C80 (129.40, 75.80, 90°)` |
| **M0 Phase B** | `C67, C68, C69, C70, C73, C108, C109, C110, C111, C112` | `161.40, 163.75, 166.10, 168.45, 170.80, 173.15, 175.50, 177.85, 180.20, 182.55` | — |
| **M0 Phase A** | `C74, C76, C77, C75, C71, C113, C114, C115, C116, C117` | `188.10, 190.45, 192.80, 195.15, 197.50, 199.85, 202.20, 204.55, 206.90, 209.25` | `C81 (186.20, 75.80, 90°)` |

### 3.3 Relocated `C_HF1–C_HF6`, Gate Resistors, and Heatsink-Edge NTCs (`courtyard max_y <= 81.48 mm`)

| Group | Exact Coordinates `(x, y, rot)` |
|---|---|
| `C_HF1–C_HF6` (`0603`) | `C_HF6 (25.75, 80.00, -90°)`, `C_HF5 (55.75, 80.00, -90°)`, `C_HF4 (82.75, 80.00, -90°)`, `C_HF3 (143.75, 80.00, -90°)`, `C_HF2 (173.75, 80.00, -90°)`, `C_HF1 (200.75, 80.00, -90°)` |
| M1 Gate Resistors (`0402`) | `R34 (16.2, 80.5, -90°)`, `R33 (35.8, 80.5, -90°)`, `R29 (46.2, 80.5, -90°)`, `R28 (65.8, 80.5, -90°)`, `R24 (73.2, 80.5, -90°)`, `R25 (92.3, 80.5, -90°)` |
| M0 Gate Resistors (`0402`) | `R14 (134.2, 80.5, -90°)`, `R13 (153.8, 80.5, -90°)`, `R9 (164.2, 80.5, -90°)`, `R8 (183.8, 80.5, -90°)`, `R1 (191.2, 80.5, -90°)`, `R2 (210.3, 80.5, -90°)` |
| Heatsink-Edge NTCs (`0402`) | `TH5 (8.0, 80.5, -90°)`, `R63 (6.2, 80.5, -90°)`, `C102 (4.4, 80.5, -90°)` and `TH1 (125.5, 80.5, -90°)`, `R23 (123.7, 80.5, -90°)`, `C21 (121.9, 80.5, -90°)` |

### 3.4 Copper Pours, Stitching Vias, and Heatsink Footprint Keepout

- Extend `F.Cu` and `B.Cu` `VDC` leg pours to `y = 75.00 .. 88.20 mm` across all six 10-capacitor banks over `100.00%` solid `In1.Cu` `GND` (`~35 pH` sheet inductance across the `5.5 mm` heatsink clearance band).
- Add `0.60 / 0.30 mm` `VDC` (`F.Cu <-> In2.Cu/B.Cu`) and `GND` (`F.Cu <-> In1.Cu`) stitching via arrays across all `60` `1206` phase-leg capacitors and `C_HF1–C_HF6` strictly North of `y = 81.50 mm` (zero non-`GND` vias in `y = 82.0 .. 98.0 mm`).
- Add `footprints not_allowed` rule areas across `[1.00, 81.60] .. [219.00, 86.65]` and every inter-FET gap so DRC permanently enforces the heatsink keepout.
