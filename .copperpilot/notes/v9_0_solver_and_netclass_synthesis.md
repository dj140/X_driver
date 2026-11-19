# V9.0 Solver Synthesis: IPC-2152 Ampacity, Fine-Pitch IC Clearances, and 2D Laplace USB Impedance

## 1. 2D Laplace Field Solver — USB 2.0 Differential Pair (`F.Cu` over `In1.Cu`)
Stackup geometry on `bldc_motor_cntroller_v9.0`:
- Outer copper (`F.Cu`): `2 oz` (`t = 70 µm`), solder mask `15.2 µm` (`εr = 3.5`).
- Prepreg (`F.Cu` to `In1.Cu` solid `GND`): `h = 0.11 mm`, `εr = 4.1`.

| Width `W` (mm) | Gap `S` (mm) | `Zdiff` Masked `70 µm` (Ω) | `Zodd` (Ω) | `Zeven` (Ω) | `Zdiff` Bare `70 µm` (Ω) | `Zdiff` Masked `35 µm` (Ω) |
|---:|---:|---:|---:|---:|---:|---:|
| `0.150` | `0.200` | `90.31` | `45.15` | `57.30` | `94.96` | `97.64` |
| **`0.155`** | **`0.220`** | **`90.65`** | **`45.32`** | **`55.83`** | **`95.10`** | **`97.58`** |
| `0.160` | `0.240` | `90.72` | `45.36` | `54.50` | `94.99` | `97.32` |

- **Design Rule Match**: Existing `USB` netclass in `bldc_motor_cntroller_v9.0.kicad_pro` specifies `track_width = 0.155 mm`, `diff_pair_width = 0.155 mm`, and `diff_pair_gap = 0.220 mm`, hitting **`90.65 Ω`** (`+0.7%` vs `90 Ω` nominal, well inside USB 2.0 `90 Ω ± 15%`) without modifying stackup or minimum track rules (`min_track_width = 0.150 mm`).

## 2. Fine-Pitch IC Pad-Gap Clearance Audit
| Reference | Package | Minimum Different-Net Pad Gap (mm) | Active Netclass Clearance (mm) | Margin (mm) |
|---|---|---:|---:|---:|
| `U1`, `U2` (`DRV8301DCAR`) | `HTSSOP-56` (`0.50 mm` pitch, `0.3048 mm` pad) | `0.1952` | `0.180` (`Default` / `Gate` / `Sense` / `Supply`) | `+0.0152` |
| `U6` (`STM32F405RGT6`) | `LQFP-64` (`0.50 mm` pitch, `0.300 mm` pad) | `0.2000` | `0.180` | `+0.0200` |
| `U8` (`USBLC6-2SC6`) | `SOT-23-6` (`0.95 mm` pitch, `0.650 mm` pad) | `0.3000` | `0.180` (`USB`) | `+0.1200` |

- `HV_Power_Track_Clearance_Outside_Drivers` (`0.25 mm` in `.kicad_dru`) explicitly excludes `U1`/`U2` courtyards so `PVDD1` (`pins 29, 53, 54`) and `SH_*/SL_*` pins (`0.1952 mm` pad gap) pass DRC cleanly.

## 3. IPC-2152 Conductor Sizing (`2 oz` Outer / `1 oz` Inner, Adjacent `0.11 mm` `In1.Cu` Plane)
| Rail / Path | Continuous Current (A) | External `2 oz` Width (`ΔT = 20 °C`) (mm) | Planned `v9.0` Copper Geometry |
|---|---:|---:|---|
| `VDC` Battery Spine (`J3.2`) | `45–60` | `18.8–28.0` | Parallel `F.Cu` + `In2.Cu` (`178 mm` wide plane) + `B.Cu` pours + via stitching |
| Motor Phases `SH_A`, `SH_B`, `SH_C` | `30` | `10.7` | `7.5–8.5 mm` `F.Cu` + `7.5–8.5 mm` `B.Cu` in parallel (`15–17 mm` effective `2 oz` width) |
| Low-Side Shunt Trunks `SL_B`, `SL_C` | `30` (`RMS`leg) | `10.7` | Straight `5 mm` long, `6.5–7.0 mm` `F.Cu` + `6.5–7.0 mm` `B.Cu` (`13–14 mm` effective `2 oz` width) |
| `+5V` Buck Rail | `1.5` | `0.17` (`0.53` unadj.) | `0.50 mm` (`Supply_5V`) / `0.30 mm` (`Supply`) |
| `+3.3V` / `+3.3VA` / `GVDD` | `0.10–0.50` | `0.02–0.06` (`0.05–0.20` unadj.) | `In2.Cu` `+3.3V` zone + `0.30 mm` `Supply` traces |
| `Gate` (`IRF7759L2`, `Qg = 300 nC` max) | `0.35` pulsed RMS | `0.04` (`0.12` unadj.) | `0.30–0.40 mm` zero-via `F.Cu` traces over `0.11 mm` `In1.Cu` |
