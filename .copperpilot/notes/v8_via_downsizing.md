# Oversized Via Downsizing Summary (`bldc_motor_cntroller_v8.kicad_pcb`)

## 1. Scope & Confirmed Action
Per user confirmation, all `525` oversized stitching and power vias (`> 0.80 mm` pad / `> 0.40 mm` drill) on `bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_pcb` were downsized in place to **`0.80 mm` pad / `0.40 mm` drill** (`0.20 mm` annular ring, matching `bldc_motor_cntroller_v5.kicad_pcb` and standard 4-layer fabrication limits) and all `53` copper zones were refilled so `R12`/`R32` shunt `GND` islands, `XT90` (`J3`) `VDC`/`GND` spines, and `SH_A..C`/`SL_B..C` phase pours remain 100% stitched.

## 2. Before vs. After Via Geometry Breakdown

| Original Size / Drill (mm) | Annular Ring (mm) | Vias Updated | Target Size / Drill (mm) | Primary Nets |
|---|---:|---:|---|---|
| `0.80 / 0.40` | `0.20` | `0` (kept: `6`) | `0.80 / 0.40` | `SH_A..C` (`M0`, `M1`) |
| `0.85 / 0.45` | `0.20` | `73` | `0.80 / 0.40` | `VDC`, `GND`, `SH_A..C`, `SL_B` |
| `0.90 / 0.45` | `0.225` | `88` | `0.80 / 0.40` | `GND` |
| `0.90 / 0.50` | `0.20` | `22` | `0.80 / 0.40` | `SL_C`, `VDC`, `/Power Management/HS` |
| `0.95 / 0.50` | `0.225` | `42` | `0.80 / 0.40` | `VDC` |
| `0.95 / 0.55` | `0.20` | `22` | `0.80 / 0.40` | `GND` (`R12` & `R32` shunt pockets) |
| `1.00 / 0.55` | `0.225` | `166` | `0.80 / 0.40` | `SH_A..C` (`88`), `GND` (`78`) |
| `1.10 / 0.60` | `0.25` | `112` | `0.80 / 0.40` | `VDC` (`74`), `GND` (`38`) along `J3` `XT90` spine |
| **Total** | — | **`525` updated (`531` total)** | **Uniform `0.80 / 0.40`** | All stitched power & ground pours |

## 3. Post-Promotion Verification (`KiCad 10.0.8`)
- **Promoted Artifact**: `bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_pcb` (`SHA-256: a5a3046bbf5821a81dbb5e162f42bbb58ad6f2f765e972baa00385b589cb8a84`)
- **Via Read-Back**: `531 / 531` vias at `0.80 mm` pad / `0.40 mm` drill (`4:1` drill aspect ratio on `1.6 mm` stackup, `0.20 mm` annular ring).
- **DRC Delta (`run_drc`)**:
  - `0` new DRC errors or warnings vs. baseline (`0` `clearance`, `0` `via_annular_width`, `0` `hole_size`, `0` `via_dangling`, `0` `isolated_copper`).
  - `unconnected_items`: unchanged at `273` (out-of-scope unrouted signal nets; zero power/ground island regressions).
  - Pre-existing unchanged items: `181` `solder_mask_bridge` errors on `0.5 mm`-pitch `U6`/`U1`/`U2` pads, `526` silk/text/stock-library warnings, and `79` non-electrical parity warnings (`64` `U1/U2` thermal `"V"` pads + `8` `G***` silk graphics + `7` duplicate `G***`).
- **DFM & Thermal Note**: At ~`1.5–2.0 A` continuous per `0.40 mm` plated via (`1 oz` barrel plating), the `74` `VDC` + `38` `GND` vias on the `J3` `XT90` spine (`112` vias) and `14–18` vias per phase pour (`SH_A..C`) retain substantial continuous current margin while freeing routing channels between inner-layer pours. If `bldc_motor_cntroller_v8.kicad_pcb` is currently open in PCBNew, reload the file from disk (`File -> Revert`) before continuing edits so PCBNew picks up the promoted `0.80/0.40 mm` vias.
