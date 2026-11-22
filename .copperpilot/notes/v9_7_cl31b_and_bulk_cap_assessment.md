# `bldc_motor_cntroller_v9_7` Promotion, `CL31B106KBHNNNE` (`C89632`) Update, and 63 V Bulk Capacitor Assessment

## 1. Promoted `v9_7` Project Files
Branched cleanly from `bldc_motor_cntroller_v9_6/` (leaving `v9_6` untouched) into standalone `bldc_motor_cntroller_v9_7/`:
- `bldc_motor_cntroller_v9_7/bldc_motor_cntroller_v9_7.{kicad_pro,kicad_prl,kicad_dru,kicad_sch,kicad_pcb}`
- Dedicated subsheets: `motor_driver.kicad_sch`, `motor_driver2.kicad_sch`, `power_management.kicad_sch`, `io_interface.kicad_sch`, `microcontroller_interface.kicad_sch`

## 2. `1206` `VDC` Capacitor Consolidation (`61` Positions)
Updated all `61` `1206` (`Capacitor_SMD:C_1206_3216Metric`) `VDC`-to-`GND` capacitors in both schematics and PCB footprints (`C12` and `C18` on the `+5V` buck output remain untouched):

| Sheet | References Updated | Count | Old Part / Value | New Part / Value |
|---|---|---|---|---|
| `motor_driver.kicad_sch` | `C16` | 1 | `4.7uF 50V` / `HMK325C7475KN-TE` (1210 mismatch) | `10uF 50V` / `CL31B106KBHNNNE` / `C89632` |
| `motor_driver.kicad_sch` | `C103–C117` | 15 | `100uF 50V` / `GMK105CC6105MV-F` | `10uF 50V` / `CL31B106KBHNNNE` / `C89632` |
| `motor_driver2.kicad_sch` | `C35` | 1 | `4.7uF 50V` / `HMK325C7475KN-TE` (1210 mismatch) | `10uF 50V` / `CL31B106KBHNNNE` / `C89632` |
| `motor_driver2.kicad_sch` | `C118–C132` | 15 | `100uF 50V` / `GMK105CC6105MV-F` | `10uF 50V` / `CL31B106KBHNNNE` / `C89632` |
| `power_management.kicad_sch` | `C39, C40, C42, C44–C48, C51, C53–C57, C60, C61, C64–C71, C73–C77` | 29 | `100uF 50V` / `GMK105CC6105MV-F` | `10uF 50V` / `CL31B106KBHNNNE` / `C89632` |
| **Total** | **61 `1206` `VDC` capacitors** (`59` phase-leg + `C16` + `C35`) | **61** | — | **Samsung `CL31B106KBHNNNE`, LCSC `C89632`, `10uF 50V X7R 1206`** |

### Electrical & DC-Bias Notes
- **Package & Nominal Spec:** Samsung `CL31B106KBHNNNE` is confirmed `10 uF ±10%`, `50 V`, `X7R`, `1206` (`3.20 × 1.60 × 1.60 mm`).
- **DC-Bias Derating:** At `40–47.5 V DC` (`80–95%` of `50 V` rating), X7R `1206` MLCCs lose well over half their nominal capacitance (`~200–300 uF` effective across the `59`–`61` positions, not `610 uF`), and `50 V` provides minimal voltage margin against switching overshoot/regeneration on a `47.5 V` bus.

## 3. On-Board Placement Feasibility for `63 V` Bulk Capacitors (`10 × 10 mm`)
Audited `bldc_motor_cntroller_v9_7.kicad_pcb` outside the `y = 81.6..97.4 mm` DirectFET heatsink keepout and above/beside `J3` (`XT90` at `(110.0, 123.0)`, courtyard `x = 99.15..120.85, y = 117.6..128.4`):

| Candidate Zone (Outside Heatsink Keepout) | Clear Envelope (mm) | Capacity (`10 × 10 mm` cans, `>= 1.5 mm` gap) | Copper Access | Notes |
|---|---|---|---|---|
| **Center `VDC`/`GND` Spine (North of `J3`, between M1 `Q8` and M0 `Q6`)** | `x = 94.5..125.5`, `y = 99.0..115.5` (`31 × 16.5 mm`) | **2×** (e.g., `(103.5, 107.0)` and `(116.5, 107.0)`) | Direct `F.Cu`/`B.Cu`/`In2.Cu` `VDC` and `In1.Cu` `GND` spine | Best low-inductance spot directly feeding both half-bridge channels and `J3` |
| **Flanking `J3` (South-West & South-East of `XT90`)** | `x = 85.0..97.5, y = 114.0..127.0` and `x = 122.5..135.0, y = 114.0..127.0` | **+2×** (1 per side of `J3`, `4×` total with spine) | Direct `VDC`/`GND` spine beside `J3` | Check clearance to `SH_A` (M1) / `SH_C` (M0) phase trunks before finalizing |
| **Off-Board (External harness / daughterboard on `XT90`)** | No PCB respin | Unlimited | Via `J3` `XT90` | Lowest board change; higher lead inductance than on-board polymers |

### Part Recommendation
- **For motor PWM ripple current:** **NJCON `100 uF 63 V` polymer (`C19270540`, `10 × 10 mm`, `3 A` ripple @ `100 kHz`)** — placing `2×` to `4×` on the center `VDC`/`GND` spine gives `6–12 A` RMS ripple rating and `200–400 uF` stable `63 V` bulk capacitance without DC-bias collapse.
- **For energy storage only:** **JIERR `100 uF 63 V` electrolytic (`C51953411`, `10 × 10.5 mm`, `200 mA` @ `120 Hz`)** is too low in ripple rating for motor-drive ripple on its own; use only alongside high-ripple polymers or off-board bulk storage.

## 4. Post-Promotion Verification (`bldc_motor_cntroller_v9_7/`)
- **`run_erc`:** `0` errors (`425` pre-existing legacy `endpoint_off_grid` warnings; `0` new warnings).
- **`run_drc` (`--schematic-parity`):** `0` schematic-parity errors (`parity_errors: 0`), `0` courtyard/outline overlaps (`query_design(what="overlaps")`), `3` inherited minor clearance errors from `v9_6` (`0.172–0.177 mm` vs `0.180 mm` at `R55`, `U4`, `U5`), and `165` inherited `unconnected_items` (upper-board routing in progress).
- **3D render review:** Not re-run (unchanged `C_1206_3216Metric` footprints already verified in `v9_4`).
