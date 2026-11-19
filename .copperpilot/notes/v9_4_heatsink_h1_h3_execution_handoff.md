# `bldc_motor_cntroller_v9_4` Ready-to-Run Handoff: Heatsink Keepout, Aligned `H1`/`H3`, and `10`-Cap-per-Phase Upgrade

## 1. Root Cause of Tool Blocker in Current Thread
- **Error Returned by Schematic & PCB Tools (`edit`, `delete_wire_segment`, `apply_kicad_schematic_batch`, `sync_schematic_to_pcb`)**:
  `ValueError: Mutation backup exceeds total storage limit (524288000 bytes). Accept or reject pending edits to free space.`
- **Why It Persisted**: Context compaction kept the **same chat thread** active, whose `500 MB` (`524,288,000` bytes) rollback store has `< 55 KB` remaining—smaller than `bldc_motor_cntroller_v9_4.kicad_sch` (`55 KB`), `motor_driver.kicad_sch` (`276 KB`), and `bldc_motor_cntroller_v9_4.kicad_pcb` (`1.98 MB`). Per CopperPilot tool-safety rules, custom scripts cannot be substituted for `apply_kicad_schematic_batch` or `sync_schematic_to_pcb`.
- **1-Step Fix**: Click **+ New Chat** in CopperPilot (opening a fresh thread on `/home/sam/Open_drive` with `0 / 500 MB` backup usage) and paste:
  `Execute ./.copperpilot/notes/v9_4_heatsink_h1_h3_execution_handoff.md on bldc_motor_cntroller_v9_4`

---

## 2. Verified `v9_4` Unit 1 Schematic Delta (`0` ERC Errors Target)

| Sheet | Exact Operations |
|---|---|
| `bldc_motor_cntroller_v9_4/bldc_motor_cntroller_v9_4.kicad_sch` | Delete wires `(210.82, 132.08)–(205.74, 132.08)`, `(205.74, 132.08)–(200.66, 132.08)`, `(200.66, 132.08)–(195.58, 132.08)` and junctions at `(200.66, 132.08)` & `(205.74, 132.08)`; delete symbols `H2` and `H4`; draw wire `(195.58, 132.08)–(205.74, 132.08)` tying `H1.1` and `H3.1` to `#PWR0131` (`GND`). |
| `bldc_motor_cntroller_v9_4/motor_driver.kicad_sch` | Set paper `"A3"`; `apply_kicad_schematic_batch` placing `C103–C117` (`15 × Device:C_Small`, `x = [284.48, 300.99, 317.50, 334.01, 350.52]`, `y = [50.80, 81.28, 111.76]`, `Value = "100uF 50V"`, `Footprint = "Capacitor_SMD:C_1206_3216Metric"`, `MPN = "GMK105CC6105MV-F"`) wired via `connect_net(power=true)` to `VDC` (`Pin 1`) and `GND` (`Pin 2`). |
| `bldc_motor_cntroller_v9_4/motor_driver2.kicad_sch` | Set paper `"A3"`; `apply_kicad_schematic_batch` placing `C118–C132` (`15 × Device:C_Small`, identical `1.27 mm`-grid coordinates and BOM fields) wired via `connect_net(power=true)` to `VDC` (`Pin 1`) and `GND` (`Pin 2`). |

---

## 3. Verified `v9_4` Unit 2 PCB Placement, Heatsink Keepout, and Copper Pours

### 3.1 Heatsink Envelope & Mounting Holes
- **Keep `H1` & `H3` (`H2`, `H4` deleted after `sync_schematic_to_pcb`)**:
  - `H1`: `(5.50, 92.00, 0°)` (`F.CrtYd` `[2.05, 88.55, 8.95, 95.45]`)
  - `H3`: `(214.50, 92.00, 0°)` (`F.CrtYd` `[211.05, 88.55, 217.95, 95.45]`)
- **Component-Free Heatsink Band (`y = [81.60 .. 97.40 mm]`)**:
  - Contains **only `Q1–Q12` (`y = 92.00 mm`, `DirectFET_L8`, `0.70 mm` height), `H1`, and `H3`**.
  - All components North of `Q1–Q12` have `courtyard max_y <= 81.48 mm` (`5.22 mm` clear of `Q1–Q12` courtyards and `5.945 mm` clear of `DirectFET_L8` cans), and `0` components sit between FETs.
  - Enforce with PCB `keepout` (`footprints not_allowed`) rule areas across `[1.00, 81.60] .. [219.00, 86.65]` and all 11 inter-FET/end gaps in `y = [86.65 .. 97.40]`.

### 3.2 Exact Component Coordinates (`0` Courtyard Overlaps, Verified Pad Polarities)

| Functional Group | Target Coordinates |
|---|---|
| `U2` M1 Driver Cluster (`U2`, `C22–C26`, `C29–C34`, `C38`, `R26`, `R27`, `R30`, `R37–R40`, `R42`, `TH2`) | Shift `Δy = -5.00 mm` (`U2 -> 55.00, 63.50, -90°`; south `0402` row at `y = 70.40 mm`, `max_y = 70.87 mm`) |
| `U1` M0 Driver + Buck Cluster (`U1`, `L1`, `D1`, `C1–C5`, `C8–C15`, `C17–C20`, `C36`, `C101`, `R3–R7`, `R10`, `R17–R22`, `R62`, `TH4`) | Shift `Δy = -5.00 mm` (`U1 -> 173.00, 63.50, -90°`; `L1 -> 190.40, 64.50`; south `0402` row at `y = 70.40 mm`, `max_y = 70.87 mm`) |
| **M1 Phase C `10 × 1206`** (`C35, C39, C40, C42, C44, C118..C122`) | `y = 75.50, rot = 90°`, `x = 13.40 + 2.35*k` (`13.40 .. 34.55`) + `C78 (11.40, 75.50, 90°)` (`Pad 1` South = `VDC`, `Pad 2` North = `GND`) |
| **M1 Phase B `10 × 1206`** (`C45, C46, C47, C51, C54, C123..C127`) | `y = 75.50, rot = 90°`, `x = 43.40 + 2.35*k` (`43.40 .. 64.55`) |
| **M1 Phase A `10 × 1206`** (`C55, C57, C60, C56, C53, C128..C132`) | `y = 75.50, rot = 90°`, `x = 70.10 + 2.35*k` (`70.10 .. 91.25`) + `C79 (68.20, 75.50, 90°)` |
| **M0 Phase C `10 × 1206`** (`C16, C61, C64, C65, C66, C103..C107`) | `y = 75.50, rot = 90°`, `x = 131.40 + 2.35*k` (`131.40 .. 152.55`) + `C80 (129.40, 75.50, 90°)` |
| **M0 Phase B `10 × 1206`** (`C67, C68, C69, C70, C73, C108..C112`) | `y = 75.50, rot = 90°`, `x = 161.40 + 2.35*k` (`161.40 .. 182.55`) |
| **M0 Phase A `10 × 1206`** (`C74, C76, C77, C75, C71, C113..C117`) | `y = 75.50, rot = 90°`, `x = 188.10 + 2.35*k` (`188.10 .. 209.25`) + `C81 (186.20, 75.50, 90°)` |
| **`C_HF1–C_HF6` (`0603`, `rot = -90°`, `Pad 1` North = `VDC`, `Pad 2` South = `SL_C`/`SL_B`/`GND`)** | `C_HF6 (13.20, 80.00, -90°)`, `C_HF5 (43.00, 80.00, -90°)`, `C_HF4 (94.20, 80.00, -90°)`, `C_HF3 (131.20, 80.00, -90°)`, `C_HF2 (161.00, 80.00, -90°)`, `C_HF1 (212.50, 80.00, -90°)` |
| **Gate Resistors (`0402`, `rot = -90°`, flanking outer edges of `VDC` leg pours)** | `R34 (16.0, 80.5)`, `R33 (36.5, 80.5)`, `R29 (46.0, 80.5)`, `R28 (66.5, 80.5)`, `R24 (72.3, 80.5)`, `R25 (92.3, 80.5)` and `R14 (134.0, 80.5)`, `R13 (154.5, 80.5)`, `R9 (164.0, 80.5)`, `R8 (184.5, 80.5)`, `R1 (190.3, 80.5)`, `R2 (210.2, 80.5)` |
| **Heatsink-Edge NTC Dividers (`0402`, `rot = -90°`)** | `TH5 (8.0, 80.5)`, `R63 (6.2, 80.5)`, `C102 (4.4, 80.5)` and `TH1 (126.5, 78.0)`, `R23 (124.8, 78.0)`, `C21 (123.1, 78.0)` |

### 3.3 Copper Pours & Stitching Vias
- **Critical `SL_C`/`SL_B` `F.Cu` Return Strips for `C_HF6/5/3/2`**: Extend `SL_C` (`x = 10.85..14.05` on M1, `128.85..132.05` on M0) and `SL_B` (`x = 40.80..44.00` on M1, `158.80..162.00` on M0) North on `F.Cu` to `y = 80.30 mm` so `C_HF6.2`, `C_HF5.2`, `C_HF3.2`, and `C_HF2.2` connect directly on `F.Cu` over `0.11 mm` solid `In1.Cu` `GND` with zero vias.
- **`VDC` & `GND` Bank Pours + Stitching**: `F.Cu` `GND` bars at `y = 73.00 .. 74.95 mm` (`GND` vias at `y = 73.35 mm` -> `In1.Cu`) and `F.Cu`/`B.Cu` `VDC` leg sheets `y = 76.05 .. 88.35 mm` (`VDC` vias at `y = 78.35 mm` -> `In2.Cu`/`B.Cu`); shift `In2.Cu` `+3.3V`/`VDC` boundary North by `5.0 mm` (`y = 57.4 / 58.2 mm`) under `U1`/`U2`; maintain `0` non-`GND` vias inside `y = [81.50 .. 98.00 mm]` (`> 99%` solid `In1.Cu` `GND`).
