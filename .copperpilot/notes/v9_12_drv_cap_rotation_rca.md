# v9_12 DRV8301 South Cap 90° Rotation & Routing RCA

**Staged candidate:** `.copperpilot/tmp/staging/v9_12_drv_route/candidate/bldc_motor_cntroller_v9_12/bldc_motor_cntroller_v9_12.kicad_pcb` (primary `bldc_motor_cntroller_v9_12/` untouched pending approval).

## 1. Does Rotating the 8 South `0402` Caps by `90°` Help Routing?

**Yes.** Rotating `C67, C66, C65, C62, C68` (below `U7`) and `C111, C110, C109` (below `U8`) vertically (`rot = 90°`, `y = 66.60 mm`) aligns Pad 2 (`BST_*`/`GND`) North toward `U7`/`U8` (`y = 66.11 mm`) and Pad 1 (`SH_*`/`D6-K`/`VDC`) South toward the phase pours (`y = 67.08 mm`). This cuts each capacitor's horizontal `F.Cu` width from `1.62 mm` to `0.62 mm` and opens `~1.6 mm`-wide vertical `F.Cu` channels between adjacent caps into the open `y = 67.4..71.3 mm` via-fanout strip.

| Ref | Channel | Old Pose (`x, y, rot`) | New Pose (`x, y, rot`) | Pad 2 (North, `y=66.11`) | Pad 1 (South, `y=67.08`) |
|---|---|---|---|---|---|
| `C67` | M0 (`U7`) | `(171.20, 66.40, 0°)` | `(171.20, 66.60, 90°)` | `Net-(U7-BST_C)` | `/Motor Driver/SH_C` |
| `C66` | M0 (`U7`) | `(173.40, 66.40, 0°)` | `(173.40, 66.60, 90°)` | `Net-(U7-BST_B)` | `/Motor Driver/SH_B` |
| `C65` | M0 (`U7`) | `(175.60, 66.40, 0°)` | `(175.80, 66.60, 90°)` | `Net-(U7-BST_A)` | `/Motor Driver/SH_A` |
| `C62` | M0 (`U7`) | `(178.00, 66.40, 0°)` | `(178.00, 66.60, 90°)` | `Net-(U7-BST_BK)` | `Net-(D6-K)` |
| `C68` | M0 (`U7`) | `(180.40, 66.40, 0°)` | `(180.40, 66.60, 90°)` | `GND` | `VDC` |
| `C111` | M1 (`U8`) | `(53.20, 66.40, 0°)` | `(53.20, 66.60, 90°)` | `Net-(U8-BST_C)` | `/Motor_Driver2/SH_C` |
| `C110` | M1 (`U8`) | `(55.40, 66.40, 0°)` | `(55.40, 66.60, 90°)` | `Net-(U8-BST_B)` | `/Motor_Driver2/SH_B` |
| `C109` | M1 (`U8`) | `(57.60, 66.40, 0°)` | `(57.75, 66.60, 90°)` | `Net-(U8-BST_A)` | `/Motor_Driver2/SH_A` |

## 2. Staged Verification After Cap Rotation & Runs D1–D7 (12-Run Cap Reached)

| Metric | Primary `v9_12` Baseline | Staged `v9_12_drv_route` | Delta |
|---|---|---|---|
| Footprints / Courtyard Overlaps | `329` / `0` | `329` / `0` | `0` |
| Copper Segments (`F.Cu / B.Cu / In2.Cu`) | `1,547` (`1193 / 208 / 146`) | `1,529` (`1167 / 216 / 146`) | `-18` (old horizontal stubs removed) |
| Vias / `via_dangling` warnings | `643` / `19` | `635` / `12` | `-8` vias, `-7` dangling |
| Physical DRC Errors (`clearance`) | `5` (`0.1513–0.1790 mm`) | `5` (`0.1513–0.1790 mm`) | `0` net change |
| Unconnected Items | `79` (`34` open nets) | `76` (`36` open nets) | `-3` (even after unrouting old `GH_B`/`GL_A`/`GL_B` stubs) |

**Completed on `F.Cu` (`0` vias, `0` new DRC errors):**
- `Net-(U7-BST_A)`, `Net-(U7-BST_B)`, `Net-(U7-BST_C)`, `Net-(U7-BST_BK)`, `Net-(D6-K)` (`100%`)
- `Net-(U8-BST_A)`, `Net-(U8-BST_B)`, `Net-(U8-BST_C)` (`100%`)
- `/Motor Driver/SH_A` (`100%`), `/Motor Driver/GL_B` (`100%`), and `U7`/`U8`-to-cap `SH_B`/`SH_C` links.

## 3. Root Cause of Remaining Unrouted DRV8301 Gates (`GH_*`, `GL_*`)

On TI's `DRV8301` south pin row (`y = 63.32 mm`, `0.50 mm` pitch), **`GH_x` sits physically between `SH_x` and `BST_x`** on all three phases (`36/37/38`, `41/42/43`, `46/47/48`):
- Routing and locking `BST_x` (`d1`/`d2`) and `SH_x` (`d5`/`d6`) to the vertical caps *first* enclosed each `GH_x` pin inside a `0.80 mm`-wide `F.Cu` cage (`< 0.96 mm` needed for a `0.60 mm` via + `2 × 0.18 mm` clearance).
- On `U8`, the pre-rotation `GH_A` track crossed diagonally in front of `U8.46` (`SH_A`) and `U8.45` (`GL_A`).
- `B.Cu` under `y = 63..85 mm` is completely open (no blocking pours).

## 4. Recommended Next Pass (No Rule Relaxation Required)

1. Promote the rotated-cap staged progress (`79 -> 76` unconnected, `0` overlaps, `0` new DRC errors) to `bldc_motor_cntroller_v9_12/` (or keep working in a fresh stage from it).
2. Unroute only the short local `F.Cu` `BST_x`/`SH_x` and `U8 GH_A` stubs under `U7`/`U8`.
3. Route **`GH_A/B/C` and `GL_A/B/C` FIRST** so all 12 driver gate traces escape straight South between the rotated vertical caps into the open `y = 67.4..71.3 mm` strip, drop `0.60/0.30 mm` vias to `B.Cu`, and run directly to `R20–R54`.
4. Re-route `BST_A/B/C` (`F.Cu` straight to Pad 2 North of the vertical caps) and `SH_A/B/C` + `SL_B/C` (hopping on `B.Cu` if needed to Pad 1 South of the vertical caps and down to the phase pours), then finish `GVDD`, `VSENSE`, `nOCTW`, `VDC`, and `+3.3V` ties.
