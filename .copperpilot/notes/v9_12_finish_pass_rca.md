# `bldc_motor_cntroller_v9_12` Finish-Routing Pass RCA & Status

**Staged candidate:** `.copperpilot/tmp/staging/v9_12_finish_p1/candidate/bldc_motor_cntroller_v9_12/bldc_motor_cntroller_v9_12.kicad_pcb` (primary `bldc_motor_cntroller_v9_12/` untouched at checkpoint `5ed80a5`)  
**Routing budget:** Reached the 12-run per-board FreeRouting cap.

---

## 1. Progress Achieved in Staging

| Metric | Promoted Baseline (`5ed80a5`) | Staged Candidate (`v9_12_finish_p1`) | Delta |
|---|---|---|---|
| Segments | `1,478` | `1,551` (`F.Cu`: `1,183`, `B.Cu`: `222`, `In2.Cu`: `146`) | `+73` |
| Vias | `604` | `609` | `+5` |
| Zones (refilled) | `111` | `113` (`+2` priority-5 `F.Cu` `GND` source windows on `Q4`/`Q10`) | `+2` |
| Courtyard Overlaps | `0` | `0` | `0` |
| Unconnected Items | `208` (`36` open nets) | `192` (`34` open nets) | `-16` |
| Physical Clearance Errors | `2` | `5` (`0.1513–0.1790 mm` vs `0.1600/0.1800 mm`) | `+3` |
| Dangling Tracks / Vias | `38` / `42` | `37` / `41` | `-1` / `-1` |
| USB Differential Skew (`USB_DP`/`USB_DN`) | — | `7.60 mm` (`114.96` vs `122.56 mm`, exceeds `5.0 mm` target) | Measured |

### Completed / Improved Nets in This Pass
- **100% routed:** `/Microcontroller Interface/nFAULT`, `/Microcontroller Interface/M0_TEMP`, `/Microcontroller Interface/AUX_TEMP`, `/I/O Interface/USB_J4_DN`, plus `Q4` and `Q10` south `GND` source pads (`8` items closed via priority-5 `F.Cu` `GND` source-window pours).
- **Major reductions:** `+3.3VA` (`15 -> 4` open), `+3.3V` (`18 -> 15` open).
- **Pour cleanup:** Trimmed `HS` `F.Cu` sliver beside `Q1.4` and trimmed Upper-East `GND` `F.Cu` zone (`eeb03389`) off `U7` (`x = 170.50 -> 186.00 mm`).

---

## 2. Root-Cause Analysis (Why FreeRouting Exhausted the 12-Run Cap)

1. **`U7`/`U8` south-pin `F.Cu` lock-in (`16` open power-stage nets: `7` `GH_*/GL_*` + `9` `SH_*/SL_*`):**
   - Already-locked `F.Cu` traces (`GH_B`, `GL_A`, `SN1`, `SH_C`, `BST_*`) cross horizontally directly south of `U7` (`y = 65.0..67.8 mm`) and `U8`, sealing off `U7.34/35/39/40/41/47` and the mirrored `U8` pins. Because `via_shield` locks existing copper on other nets, FreeRouting exits Pass 1 with `0` tracks added for those nets.
   - **Fix:** Unroute the locked `U7`/`U8` south-side fanout nets (`GH_*`, `GL_*`, `SH_*`, `SL_*`, `BST_*`) together and co-route each driver's south bus in one coordinated FreeRouting pass.
2. **FreeRouting 3-layer (`In2.Cu`) & `GND` plane timeouts:**
   - Enabling `In2.Cu` with `>= 6` passes caused FreeRouting to exceed `150 s` on multi-pad nets (`+3.3VA`, `+5V`/`GVDD`, 9-net upper bundle). Switching to `--no-in2` (`F.Cu`/`B.Cu`) with `3–4` passes completed reliably (`139–152 s`).
   - Routing `GND` (`226` total pads, `112` unconnected SMD pads) in FreeRouting timed out at `200 s` during Pass 1 triangulation. Many of those SMD `GND` pads (`C79–C152`) already sit `~0.9 mm` from a dedicated `GND` via, and others simply need a local `F.Cu` `GND` pour or local via drop to `In1.Cu`.
3. **5 minor clearance errors (`0.1513–0.1790 mm` vs `0.1600/0.1800 mm`):**
   - `U7.5` (`nOCTW`) vs `nFAULT` (`0.1513 mm`), `J5.A6` vs `USB_J4_DN` (`0.1790 mm`), `U8.25` vs `+3.3VA` (`0.1767 mm`), `TH5.2` vs `+3.3VA` (`0.1770 mm`), and `U3.2` vs `+5V` (`0.1720 mm`). All 5 are `0.001–0.009 mm` edge grazes introduced by FreeRouting's 45-degree snapping near `0.50 mm`-pitch pins and `0402` pads.

---

## 3. Recommended Next Options

1. **Promote staged progress + run a fresh Pass 2 (co-routed `U7`/`U8` south buses + local `F.Cu` `GND`/`+3.3V` plane-tie pours):** Promote `v9_12_finish_p1` (`208 -> 192` unconnected), then unroute & co-route each `DRV8301`'s south fanout (`U7`, then `U8`), close the `12` remaining upper signals, and add local `F.Cu` `GND` pours/via drops to close the `112` `GND` SMD pads without hitting FreeRouting's 226-pad triangulation timeout.
2. **Upgrade stackup to 6 layers (Sig / GND / Sig / Power / GND / Sig):** Gives `U7`/`U8` and `U9` two clean inner signal layers with unbroken `GND` and `VDC` planes, eliminating the `F.Cu`/`B.Cu` congestion and closing all `192` items rapidly.
3. **Discard staged pass and keep promoted `5ed80a5` (`2` clearance errors, `208` unconnected) as-is.**
