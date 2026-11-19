# `bldc_motor_cntroller_v6.kicad_pcb` — Placement, Power Pours & Via Sizing Audit

- **Saved V6 Deliverable**: `/home/sam/Open_drive/bldc_motor_cntroller/bldc_motor_cntroller_v6.kicad_pcb` (`SHA-256: d5355a49856139627c61d8876d2993e68491b26dad4b3c24a944eaa25854ec9e`)
- **Untouched Prior PCBs**:
  - `bldc_motor_cntroller_v5.kicad_pcb`: `e20eac7b6d38ff2ac30fbad0dcda1c9cc671cfaca2e7c9e0851aa8b46f8b230b`
  - `bldc_motor_cntroller_v4.kicad_pcb`: `c22d692ee7b5474b941ebacbdef7f35b727e1f43e3884a044feeb8b7e54f3c0c`
  - `bldc_motor_cntroller_v3.kicad_pcb`: `38da45a085921cf43934d89ffa528d27dbcbc8e2a257f34ad69845726fff3071`
- **3D Renders**:
  - Top view: `./.copperpilot/tmp/v6_render_top.png`
  - Bottom view: `./.copperpilot/tmp/v6_render_bot.png`

---

## 1. Stated Current Targets, Stackup Physics & Via Sizing Basis

| Rail / Current Path | Stated Rating | Copper / Via Sizing Basis (`IPC-2152` / Brooks-Adam, `25 um` wall, `dT <= 20 C`) | V6 Provisioned Capacity |
|---|---|---|---|
| **Stackup (`JLC04161H-3313`)** | `36 V` max DC bus | `2 oz` (`70 um`) `F.Cu`/`B.Cu`, `1 oz` (`35 um`) `In1.Cu` (`GND`) / `In2.Cu` (`VDC`), `0.11 mm` `3313` prepreg (`F-In1`, `In2-B`), `1.17 mm` `FR4` core (`In1-In2`: negligible plane capacitance, so local MLCC loop inductance dominates) | Explicit `(stackup)` block retained; coplanar `2 oz F.Cu` commutation loops bypass the `1.17 mm` core |
| **DC Bus Entry (`J3` XT90)** | **`60 A` continuous DC** (`30 A` DC per inverter) | `0.60/1.10 mm` via (`A_wall = 0.0452 mm2`, `~2.3–2.6 A` derated in array); `2 oz` pour (`0.070 mm` thick) | **`10.0 mm` `F.Cu` throat (`0.70 mm2`) + `9.6 mm` `B.Cu` throat (`0.67 mm2`) + `In2.Cu` (`1.91 mm2`)**; **`46` `J3` `VDC` vias (`105.8 A`) + `28` spine `VDC` vias (`64.4 A`)**; **`40` `J3` `GND` vias (`90.8 A`)** |
| **Inter-Inverter `VDC` Feed** | **`30 A` DC per inverter** (`40 A RMS` pulsed) | Parallel `F.Cu` (`6.8 mm x 0.070 mm = 0.48 mm2`) + `B.Cu` (`6.8 mm x 0.070 mm = 0.48 mm2`) + `In2.Cu` (`55 mm x 0.035 mm = 1.93 mm2`) = **`2.89 mm2` total (`22x` V5's `0.13 mm2` F.Cu bar)** | **`36` inverter `VDC` power vias per channel (`55.9 A` `M0` / `59.7 A` `M1` local array + direct `F.Cu`/`B.Cu` bars = `> 90 A`)** |
| **Motor Phases (`SH_A, SH_B, SH_C`)** | **`40 A RMS` per phase** (`~20 A RMS` shared to `B.Cu` mirror pour) | `0.55/1.00 mm` power vias (`~2.15–2.30 A` derated per via) + `2 oz F.Cu` & `2 oz B.Cu` mirror pours (`>= 0.60 mm` phase-to-phase gap) | **Exact `18` power vias on EVERY phase (`18` `SH_A`, `18` `SH_B`, `18` `SH_C` on both `M0` & `M1` = `~39 A` `F<->B` transfer capacity per phase)** |
| **Low-Side Phase Returns (`Phase A GND`, `R12/R32`, `R16/R36`)** | **`28.3 A RMS` avg (`40 A RMS` peak clamp)** | `0.55/1.00 mm` & `0.55/0.95 mm` vias straight `0.11 mm` into solid `In1.Cu` `GND` + `2 oz B.Cu` `GND` + continuous `2 oz F.Cu` `GND` | **Phase A LS `GND`: merged into `11,182 mm2` main `F.Cu` `GND` plane + `12–13` immediate `0.55/1.00` vias (`25–28 A` via array + direct `2 oz F.Cu` sheet)**; **`R16/R36` `GND`: merged into main `F.Cu` `GND` + `18` vias (`37.8 A`)**; **`R12/R32` `GND`: `36.9 mm2` pad + `11` `0.55/0.95` vias (`23.1 A` across `0.11 mm` prepreg to `In1.Cu` + `B.Cu`)** |
| **Aux / Brake Half-Bridge (`Q13/Q14`)** | **`15 A` continuous** | `0.50/0.90 mm` & `0.55/1.00 mm` power vias | **`6` `AUX_VDC` + `18` `AUX_GND` (`38 A`) + `2` `AUX_HS` vias** + unbroken `F.Cu` `GND` merge |

---

## 2. Quantitative Before (`V5`) vs After (`V6`) Metrics

| Review Finding / Metric | `V5` Measured | **`V6` Measured** | Improvement / Status |
|---|---|---|---|
| **`C_HF1–C_HF6` (`100 nF 100 V` `0603`) return pad to LS source** | `4.79 mm` to nearest LS pad (`5.81 mm` to LS centroid), above FET row (`y = 84.85`) | **`2.68 mm` to nearest LS pad (`1.60 mm` pad-edge, `3.60 mm` to LS centroid)** inside `[LS, HS]` slot (`y = 90.45`) | **`-44%` pad distance**, direct horizontal alignment with LS source `pad 3` (`y = 89.58`) & HS drain `pad 2` (`2.33 mm` center / `1.45 mm` pad-edge) |
| **Phase A vs B/C HF commutation return symmetry & `B.Cu` return width** | Asymmetric: Phase A closed on `F.Cu/In1.Cu`, Phases B/C detoured `1.56 mm` to a **`1.20 mm` wide `B.Cu` strip** | **All 3 phases (A, B, C) close directly on coplanar `2 oz F.Cu` (`1.65 mm` bridge, `0` series vias)** + **`3.4–6.0 mm` wide `B.Cu` `SL_C`/`SL_B` parallel pours (`4–7` vias)** | Identical primary `F.Cu` commutation loop across A/B/C; `B.Cu` return widened **`3x–5x`** |
| **Outer HS gate paths (`GH_A`, `GH_C` vs `GH_B` `DRV -> Rg`)** | `GH_A = 14.81 mm`, `GH_C = 10.50 mm`, `GH_B = 7.66 mm` (`GL_C = 14.38 mm`; `~2x` spread) | **`GH_C = 6.60 mm`, `GH_B = 4.79 mm`, `GH_A = 7.48 mm`** (`sum DRV->Rg->Gate`: **`9.49, 7.68, 10.37 mm`**) | Mirror-symmetric `[LS_C, HS_C] [LS_B, HS_B] [HS_A, LS_A]` + `U1/U2` dropped `+3.25 mm` south (`y = 76.45`): **all 3 HS gates within `2.69 mm` (`1.38x–1.56x`)** |
| **Shunt Kelvin sense vertical run (`SP/SN` to shunt `SL` pad)** | `SP/SN` at `y = 77.02`, shunts at `y = 97.20` (`dy = 20.18 mm` across FET + `1206` cap rows) | `SP/SN` at `y = 80.27`, vertical shunts `SL` pad at `y = 94.30` (**`dy = 14.03 mm`**, `14.03 mm` to `R12.2`, `14.48 mm` to `NT1`) | **`-30.5%` vertical sense span**, and `1206` cap wall removed from under `U1/U2` so sense pairs cross **zero** bulk-cap rows |
| **`+5V` Buck (`L1, D1, C12, C18`) location & run to `U4/U5` LDOs** | `L1` at `(126.6, 72.2)` against M0 DC-link; `+5V` (`C18`) `40.82 mm` from `U5` & `42.32 mm` from `U4` | `L1` at `(111.2, 59.8)` & `D1` at `(116.5, 61.8)` **`20.2 mm` north of DC-link**, pointing west: `C18 (+5V)` **`10.66 mm` from `U5`** & **`14.35 mm` from `U4`** | **`-74%` `+5V -> LDO` path length**, decoupled from Inverter 1 DC-link |
| **Total Power & Stitching Vias (and Barrel Sizes)** | `303` vias, **100% `0.40/0.80 mm`** (`~1.5 A` each) | **`531` vias** (`112x` `0.60/1.10`, `166x` `0.55/1.00`, `22x` `0.55/0.95`, `42x` `0.50/0.95`, `22x` `0.50/0.90`, `161x` `0.45/0.85–0.90`, `6x` `0.40/0.80`) | **`+75%` more vias AND `0.50–0.60 mm` power drills (`2.0–2.6 A/via`)** |
| **`F.Cu` `VDC` Feed (`J3` neck & inter-inverter bar)** | `7.7 mm` `J3` neck + **`1.8 mm` (`0.13 mm2`)** inter-inverter bar; `27` `J3` vias | **`10.0 mm` (`0.70 mm2`) `F.Cu` `J3` throat + `6.8 mm` (`0.48 mm2`) `F.Cu` bar + `6.8–9.6 mm` (`0.48–0.67 mm2`) `B.Cu` `VDC` bar** + **`74` `J3`/spine `0.60/1.10` vias (`170 A`)** | **`7.4x` outer-layer `2 oz` `VDC` copper cross-section (`0.96 mm2` `F+B` + `1.93 mm2` `In2.Cu` = `2.89 mm2`)** |
| **Phase A LS-Source `GND` Return** | `41.8 mm2` isolated `F.Cu` island with **`3` `0.4/0.8` vias (`~4.5 A`)** | **Merged directly into `11,182 mm2` continuous main `F.Cu` `GND` plane** + **`12–13` immediate `0.55/1.00` vias (`25–28 A` local vias + solid `2 oz` sheet)** | Island eliminated; **`> 6x` immediate via current capacity** |
| **Shunt `R12/R16/R32/R36` `GND` Pads** | Isolated `18 mm2` `F.Cu` islands with **`6` `0.4/0.8` vias (`~9 A`)** | `R16/R36`: **merged into main `F.Cu` `GND` + `18` `0.55/1.00` vias (`37.8 A`)**; `R12/R32`: **`36.9 mm2` pad + `11` `0.55/0.95` vias (`23.1 A`)** | **`2.6x–4.2x` shunt return via capacity** |
| **`F<->B` Phase Pour Stitching (`SH_A / SH_B / SH_C`)** | `9` (`A`), `18` (`B`), `16` (`C`) `0.4/0.8` vias | **`18` (`A`), `18` (`B`), `18` (`C`) `0.55/1.00 mm` power vias on both `M0` & `M1`** | **100% balanced (`18/18/18`), `2.9x` Phase A transfer capacity** |
| **Small `F.Cu` `GND` Islands in Power Stage** | **`11` islands (`2.1–41.8 mm2`)**, including `12.8 mm2` cap-row island with **`1` via** | **`7` of `11` merged into `11,182 mm2` main plane (`201` vias)**; only `4` symmetric pockets remain (`2x 29.0 mm2` with **`12` vias each**, `2x 36.9 mm2` with **`11–14` vias each**; **`0` 1-via islands**) | Minimum via count in ANY `F.Cu` `GND` island raised from **`1` -> `11`** |

---

## 3. KiCad 10.0.8 DRC Verification (`V5` vs `V6`)

| DRC Check (`/usr/bin/kicad-cli pcb drc`) | `V5` | **`V6` (Promoted)** | Delta |
|---|---|---|---|
| **Total Errors** (`U1/U2/U6` library mask/pad/drill baseline) | `351` | **`351`** | **`0` new errors** |
| **Courtyard Overlaps / Outside Board** | `0 / 0` | **`0 / 0`** | Clean (`249` top-side footprints, `B.Cu` 100% flat) |
| **Shorting Items / Hole Clearance / Zones Intersect / Starved Thermal** | `0 / 0 / 0 / 0` | **`0 / 0 / 0 / 0`** | Clean |
| **Isolated Copper Islands / Dangling Vias / Silk Overlap** | `0 / 0 / 0` | **`0 / 0 / 0`** | Clean (`53` zones, `531` vias) |
| **Total DRC Violations (Errors + Warnings)** | `913` | **`899`** | **`-14` violations** |
| **Unconnected Items (Pre-route Signal/Rail Nets)** | `297` | **`296`** | **`-1`** (`0` disconnected copper zone islands) |
