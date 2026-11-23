# `bldc_motor_cntroller_v9_10` Bulk Capacitor (`C154–C157`) Placement Review

- **Reviewed file:** `bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_10.kicad_pcb` (user-edited working copy vs. Git `HEAD` `1bd03cf`)
- **Review mode:** Read-only (no files modified)
- **Visual render:** `.copperpilot/tmp/v9_10_bulk_review/top_3d.png`

---

## 1. Summary of Changes vs. `HEAD` (`1bd03cf`)

| Ref | `HEAD` Pose `(x, y, rot)` | Current Pose `(x, y, rot)` | Pad 1 (`VDC`) | Pad 2 (`GND`) | Courtyard `[x1, y1, x2, y2]` |
|---|---|---|---|---|---|
| `C154` | `(103.5, 109.5, -90°)` | `(109.8, 111.5, 180°)` | `(114.0, 111.5)` East | `(105.6, 111.5)` West | `[103.15, 106.00, 116.45, 117.00]` |
| `C155` | `(116.5, 109.5, -90°)` | `(128.3, 123.0, 180°)` | `(132.5, 123.0)` East | `(124.1, 123.0)` West | `[121.65, 117.50, 134.95, 128.50]` |
| `C156` | `(89.5, 122.5, -90°)` | `(89.5, 122.5, 0°)` | `(85.3, 122.5)` West | `(93.7, 122.5)` East | `[82.85, 117.00, 96.15, 128.00]` |
| `C157` | `(130.5, 122.5, -90°)` | `(112.3, 63.5, 0°)` | `(108.1, 63.5)` West | `(116.5, 63.5)` East | `[105.65, 58.00, 118.95, 69.00]` |
| `G1` (`M00`) | `(102.0, 62.0, 0°)` | `(56.5, 111.0, 0°)` | — | — | Logo (no courtyard) |
| `G2` (`M1`) | `(108.5, 62.0, 0°)` | `(174.5, 109.5, 0°)` | — | — | Logo (no courtyard) |

---

## 2. Mechanical & Heatsink Clearance (`±5.0 mm` Around `Q1–Q12`)

- **`Q1–Q12` envelope (`y = 96.00 mm` centerline):**
  - DirectFET L8 body: `y = 91.425 .. 100.575 mm` → `±5.0 mm` tall-component band = **`y = 86.43 .. 105.58 mm`**
  - DirectFET L8 courtyard: `y = 90.70 .. 101.30 mm` → `±5.0 mm` courtyard band = **`y = 85.70 .. 106.30 mm`**
  - Existing DRC heatsink component keepout: `y = 85.60 .. 101.40 mm`
- **`query_design(what="overlaps")`:** `0` courtyard overlaps and `0` board-outline violations across all `330` footprints.

| Ref | Clearance to `Q1–Q12` Body (`±5 mm` target) | Clearance to `J3` Courtyard `[99.15, 117.60, 120.85, 128.40]` | Board Edge Margin (`y = 130.0`) | Mechanical Verdict |
|---|---|---|---|---|
| `C154` | `5.78 mm` South of FET body (`4.70 mm` to FET courtyard) | `0.60 mm` North of `J3` | `13.00 mm` | **PASS** — clean single-can fit in center spine |
| `C155` | `16.93 mm` South of FET body | `0.80 mm` East of `J3` | `1.50 mm` | **PASS** |
| `C156` | `16.43 mm` South of FET body | `3.00 mm` West of `J3` | `2.00 mm` | **PASS** |
| `C157` | `22.43 mm` North of FET body | — (North corridor, South of `U6`) | `48.00 mm` (North) | **PASS** mechanically (overlaps `G3`/`G6`/`G7` silkscreen logos only) |

---

## 3. Electrical, Power-Integrity & DRC Audit

Running `run_drc` on the promoted working copy shows **`12` copper/mask DRC errors** (up from `2` at `HEAD`; **`10` new errors on `C155` and `C157`**) and **`5` unconnected pad items** across `C155`, `C156`, and `C157`:

| Ref | Polarity Alignment vs. `J3` (`GND` W / `VDC` E) | Pad Connectivity | DRC Errors Introduced | Power-Integrity & Routing Notes |
|---|---|---|---|---|
| `C154` | **Optimal** (`GND` W `105.6`, `VDC` E `114.0` matches `J3`) | Both pads connected | `0` | Very good placement directly North of `J3`; tidy the old `GND` via at `(114.1, 113.7)` sitting just South of `C154.1` (`VDC`) when rebuilding pours |
| `C156` | **Optimal** (`GND` E `93.7` faces `J3.1` `GND`, `VDC` W `85.3`) | `GND` connected; **`VDC` pad unconnected** | `0` | Good location & orientation; extend `F.Cu` `VDC` pour to `(85.3, 122.5)` and add `2–3× 0.80/0.40 mm` `VDC` vias |
| `C155` | **Reversed (`180°`)** — `GND` W (`124.1`) faces `J3.2` (`VDC` `115.45`) | **Both `VDC` and `GND` pads unconnected** | `2` (`1` `F.Cu` `VDC` zone clearance `0.000 mm`, `1` `solder_mask_bridge`) | Rotate `180° -> 0°` so `VDC` (`124.1`) faces `J3.2` (`VDC`) and `GND` (`132.5`) faces East `GND` return, then update/refill pours + stitching vias |
| `C157` | **Reversed vs. local `VDC` vias** (`VDC` W `108.1`, `GND` E `116.5`) | **Both `VDC` and `GND` pads unconnected** | `8` (**`2` `VDC`-to-`GND` `shorting_items`**, `2` `hole_clearance` `0.000 mm`, `3` `solder_mask_bridge`, `1` `F.Cu` `VDC` zone clearance `0.000 mm`) | `C157.2` (`GND`) lands directly on two existing `VDC` vias `(114.5, 64.2)` & `(117.0, 64.2)` and the `F.Cu` `VDC` pour. Electrically, `y = 63.5` is `~60 mm` from `J3` (minimal hot-plug damping) and occupies the central East–West signal routing corridor South of `U6` (`y = 55..70 mm`), though `In2.Cu` `VDC` (`y = 55.5..129.0`) and `In1.Cu` `GND` do exist underneath |

---

## 4. Recommended Fixes

1. **Fix `C157` `VDC`-to-`GND` dead short (Critical):**
   - **Option A (Keep `C157` at `112.3, 63.5`):** Rotate `C157` from `0°` to `180°` (putting `VDC` East at `116.5` over the `VDC` pour/vias and `GND` West at `108.1` with fresh `0.80/0.40 mm` `GND` vias), shift/clear the `VDC` vias from under the pad (avoid via-in-pad), move `G3`/`G6`/`G7` logos out from under `C157`, and refill zones. Trade-off: `C157` remains in the central `U6`-south signal routing corridor and far from `J3`.
   - **Option B (Preferred for PI + routing):** Move `C157` back to the south power stage (e.g., open pockets between `J2`/`C156` or `C155`/`J1`, or West/East of `C154` if clearance permits) so all 4 bulk cans damp `J3` hot-plug ringing locally and the central `U6` routing corridor stays open.
2. **Rotate `C155` `180° -> 0°`:** Aligns `C155.1` (`VDC`) directly beside `J3.2` (`VDC`) and `C155.2` (`GND`) on the East side, eliminating the `F.Cu` `VDC` pour conflict and matching `C156`'s symmetry.
3. **Update `F.Cu` pours, `0.80/0.40 mm` stitching vias, and refill zones:** Re-align the `0.80/0.40 mm` `VDC`/`GND` via pairs to the new horizontal pad positions on `C154–C157` and run `fill_pcb_zones` to clear all stale zone collisions and connect all 8 bulk-cap pads.
