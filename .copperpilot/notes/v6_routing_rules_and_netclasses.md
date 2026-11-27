# Pre-Routing Capability Statement, IPC-2221 Calculations, 90-Ohm USB Geometry, and Netclass Proposal (`bldc_motor_cntroller_v6.kicad_pcb`)

## 1. Operational Capabilities & Constraints on This Board

**Frozen Baseline State Checked (`bldc_motor_cntroller/bldc_motor_cntroller_v6.kicad_pcb`)**:
- **Footprints**: `249` placed (`249` on `F.Cu`, `0` on `B.Cu`) — **frozen** (no footprint moved, rotated, or deleted).
- **Zones**: `53` copper zones across `F.Cu`, `In1.Cu` (`GND`), `In2.Cu` (`VDC`), and `B.Cu` — **frozen** (no zone deleted or redrawn).
- **Routed Tracks / Vias**: `0` copper segments, `531` existing stitching/power vias, `177` total nets (`154` routable multi-pad nets).
- **Active KiCad Lock Caution**: `~bldc_motor_cntroller_v6.kicad_pcb.lck` and `~bldc_motor_cntroller_v6.kicad_pro.lck` indicate `bldc_motor_cntroller_v6` is currently open in a running `pcbnew` session. Close `pcbnew` (or use `File -> Revert` without saving over disk) before we promote staged edits so the GUI buffer does not overwrite updated files.

| Requested Action | Supported? | Operational Details & Limitations |
|---|---|---|
| **Run DRC** | **Yes** | Runs native KiCad `10.0.8` batch DRC (`clearance`, `track_width`, `annular_width`, `hole_to_hole`, `copper_edge_clearance`, `courtyards_overlap`, `solder_mask_bridge`, `unconnected_items`, and schematic parity) with structured violation reporting. |
| **Refill zones** | **Yes** | Refills all `53` existing copper zones across `F.Cu`, `In1.Cu`, `In2.Cu`, and `B.Cu` via KiCad `10.0.8` without deleting or modifying any zone polygon outline. |
| **Set netclasses & design rules** | **Yes** | Writes global DRC minimums, custom `.kicad_dru` neckdown/layer rules, netclass definitions (`Power`, `Gate`, `Sense`, `USB`, `CAN`, `Supply`, `Default`), and net-to-netclass pattern assignments in `bldc_motor_cntroller_v6.kicad_pro` / `.kicad_dru` (staged first). |
| **Route and edit tracks** | **Partial (with router limits)** | **Can do**: Headless net-group routing via FreeRouting (`v2.2.4`) on isolated staged candidates (`--nets ...`), keeping all previously routed copper, existing vias, footprints, and zones fixed, plus net/segment rip-up (`unroute`) and re-route.<br>**Cannot do**: FreeRouting **cannot** enforce constant edge-coupled differential pair gap (`S`), **cannot** perform serpentine/trombone length matching or intra-pair skew tuning, **cannot** route redundant parallel Kelvin return tracks (`SH_x`/`SL_x`) beside `GH_x`/`GL_x` where `SH_x`/`SL_x` pins are already connected by copper zones, and **cannot** synthesize grounded guard traces around `SP/SN`. Manual coordinate-invented copper segments are prohibited. Exact routed lengths, skew, and paths are measured after each step and any constraint miss is flagged rather than faked. |
| **Render layers** | **Yes** | Exports top/bottom 3D raytraced board renders and per-layer 2D copper/mask/silkscreen SVG/PNG plots (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`) via KiCad `10.0.8` CLI. |
| **Undo** | **Yes (staged rollback)** | Every rule or routing unit executes inside an isolated staging copy (`.copperpilot/tmp/staging/<unit>/`) and promotes only after verification; any group or step can be rolled back cleanly from its pre-unit baseline snapshot (not interactive GUI `Ctrl+Z`). |

---

## 2. Board, Operating, and Fabricator Parameters

| Parameter | Value | Provenance / Notes |
|---|---|---|
| **Board & Stackup** | Dual `DRV8301DCAR` (`U1`, `U2`) + `STM32F405RGTx` LQFP-64 (`U6`), 4 layers (`150.0 x 98.5 mm`, `1.60 mm` total) | `F.Cu` (`70 um` / `2 oz`) / `0.110 mm FR4 3313` ($\varepsilon_r = 4.1$) / `In1.Cu GND` (`35 um` / `1 oz`) / `1.170 mm FR4 Core` ($\varepsilon_r = 4.6$) / `In2.Cu VDC` (`35 um` / `1 oz`) / `0.110 mm FR4 3313` ($\varepsilon_r = 4.1$) / `B.Cu` (`70 um` / `2 oz`); `15.2 um` solder mask (`bldc_motor_cntroller_v6.kicad_pcb` `(stackup)`). |
| **Operating Ratings** | Phase `X = 40 A RMS` (`60 A` peak), Bus `Z = 36 V` max (`60 A` DC bus), Aux/Brake = `15 A` | Project specification from user session record. |
| **Fabricator (`JLCPCB`)** | 4-Layer, `2 oz` outer / `1 oz` inner (`JLC04161H-3313` stackup family) | Retrieved `2026-11-16` (`jlcpcb.com/capabilities` & `jlcpcb.com/impedance`):<br>- **Min outer trace / space (`2 oz`)**: `0.15 mm / 0.15 mm` (`6 mil / 6 mil`); `0.18–0.20 mm` preferred.<br>- **Min inner trace / space (`1 oz`)**: `0.127 mm / 0.127 mm` (`5 mil / 5 mil`).<br>- **Min mechanical via drill (4L)**: `0.20 mm` (`0.45 mm` pad preferred; `0.30 mm / 0.60 mm` standard signal via).<br>- **PTH annular ring (`2 oz`)**: `0.254 mm` recommended (`U1/U2` footprint thermal vias use `0.254 mm` drill / `0.508 mm` pad = `0.127 mm` annular ring, responsible for baseline library DRC flags).<br>- **Stackup DFM caution**: Standard `JLC04161H-3313` defaults to `1 oz` outer (`h = 0.0994 mm`); ordering `2 oz` outer / `1 oz` inner requires selecting custom `2 oz` impedance buildup at order time and confirming final pressed prepreg thickness with JLCPCB CAM. |
| **Fine-Pitch Pad Gap Limit** | `0.1952 mm` min pad-to-pad gap on `U1`/`U2` (`DRV8301DCAR`, `0.50 mm` pitch, `0.3048 mm` pad width); `0.200 mm` on `U6` (`LQFP-64`) and `J4` (`USB-C`) | Any netclass terminating on `U1`/`U2` (`Power`, `Gate`, `Sense`, `Supply`, `Default`) must allow `<= 0.19 mm` (`0.18 mm`) pad-entry clearance inside `U1`/`U2` or DRC/FreeRouting will block all `0.50 mm`-pitch pins (`28–56`). |

---

## 3. IPC-2221 Track-Width Calculations (`dT = 10 K`, `70 um` Outer, `35 um` Inner)

### Normative Standards Note (`pcb-ipc-compliance`)
- **Current Standard Status**: `IPC-2221C` (December 2023) is the current generic rigid-board design standard (`ASSUMPTION: Class 2`), while `IPC-2152` (2009) superseded the legacy `IPC-2221B` / `IPC-D-275` conductor-sizing charts for thermal current capacity.
- **Calculation Requested**: Per your prompt, conductor cross-sections and widths below are computed directly from the classical **IPC-2221 empirical equation** at $\Delta T = 10\text{ K}$:

$$I = k \cdot (\Delta T)^{0.44} \cdot A^{0.725} \implies A_{\text{mil}^2} = \left(\frac{I}{k \cdot 10^{0.44}}\right)^{\frac{1}{0.725}}, \qquad W_{\text{mm}} = \frac{A_{\text{mil}^2}}{t_{\text{mil}}} \times 0.0254$$

where:
- $10^{0.44} = 2.754229$, $\frac{1}{0.725} = 1.379310$
- **Outer layers (`F.Cu`, `B.Cu`)**: $k = 0.048$, $t_{\text{outer}} = 70\,\mu\text{m} = \frac{70}{25.4} = 2.7559\text{ mil} \implies k \cdot 10^{0.44} = 0.132203$
- **Inner layers (`In1.Cu`, `In2.Cu`)**: $k = 0.024$, $t_{\text{inner}} = 35\,\mu\text{m} = \frac{35}{25.4} = 1.3780\text{ mil} \implies k \cdot 10^{0.44} = 0.066101$

### Step-by-Step Numerical Working by Current Domain

| Domain / Nets | Design Current $I$ | Outer $A$ ($\text{mil}^2$ / $\text{mm}^2$) | Min Outer Width ($70\,\mu\text{m}$) | Inner $A$ ($\text{mil}^2$ / $\text{mm}^2$) | Min Inner Width ($35\,\mu\text{m}$) | Physical Implementation on `v6` |
|---|---:|---:|---:|---:|---:|---|
| **DC Bus (`VDC`, `GND`)** | `60.0 A` | `4620.65 mil²` (`2.9811 mm²`) | **`42.587 mm`** | `12020.35 mil²` (`7.7550 mm²`) | **`221.573 mm`** | Carried by existing frozen multi-layer `VDC` & `GND` copper pours + `531` stitching vias (`0` high-current trace routing; only `U1/U2` `PVDD` & sense taps need short `0.80–1.00 mm` stubs with `0.25 mm` HTSSOP pad entry). |
| **Motor Phase (`SH_A..C`, `SL_B..C`)** | `40.0 A RMS` | `2641.31 mil²` (`1.7041 mm²`) | **`24.344 mm`** | `6871.20 mil²` (`4.4330 mm²`) | **`126.658 mm`** | Load current is already carried by frozen `F.Cu` + `B.Cu` `SH`/`SL` zones (`18` vias/phase). Unrouted `SH_x`/`SL_x` connections to `U1/U2` pins `34,36,39,41,46` and `C13–C15`/`C32–C34` carry **bootstrap/gate-return current only** (`<= 2.0 A` peak, `<= 0.35 A RMS`). |
| **Aux / Brake (`HS`)** | `15.0 A` | `682.77 mil²` (`0.4405 mm²`) | **`6.293 mm`** | `1776.19 mil²` (`1.1459 mm²`) | **`32.741 mm`** | Load current carried by frozen `F.Cu` `HS` zone; `U3:6`/`C52:2` tap carries bootstrap/gate return only. |
| **Gate Drive Peak / RMS (`GH_*`, `GL_*`, `HO`, `LO`, `Q*-G`)** | `2.0 A` pk / `0.35 A` RMS | `42.39 mil²` (`2.0 A` DC) / `3.83 mil²` (`0.35 A` RMS) | `0.391 mm` (`2.0 A` DC) / **`0.035 mm`** (`0.35 A` RMS) | `110.28 mil²` / `9.96 mil²` | `2.033 mm` / **`0.184 mm`** | DRV8301 source/sink peak is `1.7 A / 2.3 A` pulsed (`< 100 ns`), thermal RMS `< 0.15–0.35 A` at `<= 50 kHz` PWM. Set `Gate` nominal width = **`0.35 mm`** on `F.Cu`/`B.Cu` (`0.25 mm` neckdown into `0.3048 mm` `U1/U2` pads) for low inductance. |
| **Buck `+5V` / Switch / Fuse (`+5V`, `Net-(D1-K)`, `Net-(F1-Pad1)`)** | `1.5 A` | `28.51 mil²` (`0.0184 mm²`) | **`0.263 mm`** | `74.16 mil²` (`0.0478 mm²`) | **`1.367 mm`** | Route on `2 oz` outer layers (`F.Cu`/`B.Cu`) at **`0.60 mm`** (`> 2.2x` outer IPC-2221 width; `0.25 mm` pad entry at `U1:50/51`). |
| **Gate/Logic Supplies (`GVDD`, `+3.3V`, `+3.3VA`, `AVDD`, `DVDD`)** | `0.8 A` | `11.98 mil²` (`0.0077 mm²`) | **`0.110 mm`** | `31.16 mil²` (`0.0201 mm²`) | **`0.574 mm`** | Route on `2 oz` outer layers at **`0.50 mm`** (`4.5x` outer IPC-2221 width; `0.25 mm` pad entry at `0.50 mm`-pitch `U1/U2/U6` pins). |
| **Signals (`Sense`, `USB`, `CAN`, `Default`)** | `<= 0.1 A` | `0.68 mil²` (`0.0004 mm²`) | **`0.006 mm`** | `1.77 mil²` (`0.0011 mm²`) | **`0.033 mm`** | Governed by JLCPCB `0.15 mm` 2 oz fab minimum and controlled impedance (`0.15–0.25 mm`). |

---

## 4. 90-Ohm USB 2.0 Differential Microstrip Calculation (`F.Cu` over `In1.Cu` `GND`)

### Stackup Cross-Section (`bldc_motor_cntroller_v6.kicad_pcb`)
- **Signal Layer**: `F.Cu`, finished copper thickness $t = 0.070\text{ mm}$ (`70 um`, `2 oz`).
- **Reference Plane**: Continuous solid `In1.Cu` (`GND`), dielectric height $h = 0.110\text{ mm}$ (`FR4 3313` prepreg), $\varepsilon_r = 4.1$, $\tan\delta = 0.02$.
- **Coating**: Top LPI solder mask $t_{\text{mask}} = 0.0152\text{ mm}$ ($\varepsilon_{r,\text{mask}} \approx 3.5$).

### Analytical vs. 2D Electrostatic Field-Solver Comparison
Because $t/h = 0.070 / 0.110 = 0.636$ (`70 um` tall copper walls across a narrow gap), closed-form thin-strip equations (Hammerstad-Jensen / Kirschning-Jansen) underestimate odd-mode sidewall + solder-mask capacitance and overpredict $Z_{\text{diff}}$ by `~5–6 Ohm`. Both models were evaluated:

1. **Kirschning-Jansen Analytical Coupled Microstrip (thin-strip + thickness correction)**:
   - At $W = 0.180\text{ mm}$, $S = 0.175\text{ mm}$: $Z_0 = 49.88\,\Omega$, $Z_{0o} = 46.50\,\Omega$, $Z_{\text{diff,bare}} = 93.00\,\Omega$, $Z_{\text{diff,masked}} \approx 90.02\,\Omega$.
2. **2D Laplace Electrostatic Cross-Section Solver (exact `70 um` rectangular copper sidewalls + `15 um` conformal mask, $\varepsilon_r = 4.1 / 3.5$)**:
   - $W = 0.150\text{ mm}$, $S = 0.160\text{ mm}$ $\implies Z_{0o} = 42.26\,\Omega$, $Z_{\text{diff}} = 84.52\,\Omega$ ($\varepsilon_{\text{eff},o} = 2.625$)
   - $W = 0.150\text{ mm}$, $S = 0.180\text{ mm}$ $\implies Z_{0o} = 43.31\,\Omega$, $Z_{\text{diff}} = 86.62\,\Omega$ ($\varepsilon_{\text{eff},o} = 2.640$)
   - $W = 0.150\text{ mm}$, $S = 0.200\text{ mm}$ $\implies Z_{0o} = 44.15\,\Omega$, $Z_{\text{diff}} = 88.30\,\Omega$ ($\varepsilon_{\text{eff},o} = 2.654$)
   - **$W = 0.150\text{ mm}$, $S = 0.220\text{ mm}$ $\implies Z_{0o} = 44.83\,\Omega$, $Z_{\text{diff}} = 89.67\,\Omega$** ($\varepsilon_{\text{eff},o} = 2.667$, propagation delay $t_{pd} = \frac{\sqrt{2.667}}{c_0} = 5.45\text{ ps/mm}$)
   - $W = 0.160\text{ mm}$, $S = 0.220\text{ mm}$ $\implies Z_{0o} = 43.59\,\Omega$, $Z_{\text{diff}} = 87.19\,\Omega$ (`-3.1%` vs `90 Ohm`, comfortably within USB 2.0 `90 Ohm ± 10%` = `81–99 Ohm` with extra `2 oz` etch margin).

**Selected `USB` Netclass Geometry**: **`diff_pair_width = 0.155 mm` (`track_width = 0.155 mm`), `diff_pair_gap = 0.220 mm`** (`Z_diff ≈ 88.4 Ohm` in 2D solver with `70 um` sidewalls; `>= 0.150 mm` JLCPCB `2 oz` minimum trace/space).
- **Pre-Route USB Length Geometry Warning**: On the frozen `v6` placement, `J4` USB pads sit at `(10.545, 35.75..36.75)`, `U8` at `(14.2, 36.0)`, `R52/R53` at `(17.5, 35.05/36.95)`, and `U6` `PA11/PA12` (`pins 44/45`) on the **east** edge of `U6` at `(80.675, 43.25/42.75)`. The raw Manhattan span from `J4` to `U6:44/45` is **`77.8–78.5 mm`**, right at your **`80.0 mm` stop threshold** in Step 4; we will check exact routed length in Step 4 and stop immediately if it exceeds `80.0 mm`.

---

## 5. Proposed Netclasses & DRC Rule Set (Awaiting Approval)

### Global DRC Minimums (`board.design_settings.rules`)
- `min_track_width`: `0.15 mm` (JLCPCB `2 oz` outer capability floor)
- `min_clearance`: `0.15 mm` (JLCPCB `2 oz` outer capability floor; individual netclasses enforce `0.18–0.25 mm`)
- `min_via_diameter`: `0.50 mm` (`U1/U2` existing thermal vias are `0.508 mm` / `0.254 mm` drill; newly routed vias use `0.60 / 0.30 mm` or `0.80 / 0.40 mm`)
- `min_through_hole_diameter`: `0.25 mm`
- `min_via_annular_width`: `0.12 mm`
- `min_copper_edge_clearance`: `0.50 mm`

### Netclass Table

| Netclass | Assigned Nets | Track Width (mm) | Pad-Entry Min / Neckdown (mm) | Clearance (mm)* | Via Dia / Drill (mm) | Diff Width / Gap (mm) | Target Routing Layers |
|---|---|---:|---:|---:|---:|---:|---|
| **`Power`** | `VDC`, `GND`, `/Motor Driver/SH_A..C`, `/Motor Driver/SL_B..C`, `/Motor_Driver2/SH_A..C`, `/Motor_Driver2/SL_B..C`, `/Power Management/HS` | **`0.80`** (pours carry `15–60 A`; tracks only for `U1/U2/U3` driver/bootstrap taps) | `0.25` (at `0.50 mm`-pitch `U1/U2` pins) | **`0.18`** (`0.30` outside `U1/U2` via `.kicad_dru`) | `0.90 / 0.50` (existing phase pours untouched; no phase vias added without approval) | — | Existing pours + `F.Cu` / `B.Cu` short driver taps |
| **`Gate`** | `/Motor Driver/GH_A..C`, `GL_A..C`, `/Motor_Driver2/GH_A..C`, `GL_A..C`, `Net-(Q1..Q14-G)`, `Net-(U3-HO)`, `Net-(U3-LO)` | **`0.35`** | `0.25` | **`0.18`** | `0.60 / 0.30` | — | `F.Cu` primary (`B.Cu` short crossover only if required) |
| **`Sense`** | `/Motor Driver/SP1..2`, `SN1..2`, `/Motor_Driver2/SP1..2`, `SN1..2`, `Net-(NT1,3,5,7-Pad1)`, `Net-(U1/U2-SO1..2)`, `M0_SO1..2`, `M1_SO1..2` | **`0.20`** | `0.18` | **`0.18`** | `0.60 / 0.30` | `0.20 / 0.20` | `F.Cu` / `B.Cu` away from `SH` pours, over solid `In1.Cu GND` |
| **`USB`** | `/I{slash}O Interface/USB_DN`, `USB_DP`, `USB_J4_DN`, `USB_J4_DP` | **`0.155`** | `0.155` | **`0.18`** | `0.60 / 0.30` | **`0.155 / 0.220`** (`88.4–89.7 Ohm`) | `F.Cu` over continuous `In1.Cu GND` (minimize vias) |
| **`CAN`** | `CAN_H`, `CAN_L`, `/I{slash}O Interface/CAN_D`, `/I{slash}O Interface/CAN_R` | **`0.20`** | `0.20` | **`0.20`** | `0.60 / 0.30` | `0.20 / 0.25` | `F.Cu` / `B.Cu` (short `U7` <-> `J7/J8` bus at top edge) |
| **`Supply`** | `+5V`, `+3.3V`, `+3.3VA`, `GVDD`, `/Motor Driver/AVDD`, `DVDD`, `/Motor_Driver2/AVDD`, `DVDD`, `Net-(D1-K)`, `Net-(D2-K)`, `Net-(F1-Pad1)`, `Net-(U1/U2-BST_*)`, `Net-(U1/U2-CP1..2)` | **`0.50`** (`0.60` on `+5V`/buck/fuse) | `0.25` | **`0.18`** | `0.70 / 0.35` | — | `F.Cu` / `B.Cu` (`+3.3V` local decouplers pin->cap->via) |
| **`Default`** | All remaining MCU digital, SPI (`SPI_*`), PWM (`M0_A/B/C*`, `M1_A/B/C*`, `AUX_H/L`), encoders (`ENC*`), thermistors (`*TEMP*`), `NRST`, `BOOT0`, `SWD`, `GPIO_*`, `USB_CC1..2`, RC passives | **`0.20`** | `0.18` | **`0.18`** | `0.60 / 0.30` | `0.20 / 0.20` | `F.Cu` / `B.Cu` orthogonal pair (`In1 GND` & `In2 VDC` kept intact) |

*\*Clearance note*: `U1` and `U2` (`DRV8301DCAR`, `0.50 mm` pin pitch) have `0.3048 mm` wide pads, leaving an exact **`0.1952 mm`** copper-to-copper gap between adjacent pins (`pins 1–28` and `29–56`). Setting base netclass clearance to `0.18 mm` (`>= 0.15 mm` JLCPCB `2 oz` minimum) prevents false DRC/router pad-clearance lockups at `U1`/`U2`, while `.kicad_dru` enforces `0.30 mm` `Power`-to-other clearance outside the `U1`/`U2` courtyards.
