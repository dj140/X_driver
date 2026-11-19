# V9.2 Power-Stage Copper Bottleneck Audit & `220 × 115 mm` Placement Specification

## 1. Measured `v9.2` (`180 × 115 mm`) Phase & Shunt Copper Bottlenecks

| Net | Layer | `v9.2` Narrowest Neck (mm) | Bottleneck Location & Root Cause | `220 × 115 mm` Target Width (mm) | Expansion Ratio |
|---|---|---|---|---|---|
| `SH_B`, `SH_C` (HS Source -> Trunk) | `F.Cu` | `0.00` (South) / `0.85` (North at `y=89.0`) | `9.2 mm` intra-phase FET pitch + `C_HF2/3/5/6` placed at `y=95.2` inside the intra-phase gap completely blocked `Q3/Q5/Q9/Q11` Source on `F.Cu` | `7.48` (inter-FET) -> `12.50–12.70` (trunk) | `> 8.8x` (restores full `F.Cu` path) |
| `SH_B`, `SH_C` (LS South Drain -> Trunk) | `F.Cu` | `3.10` (`y=97.6`) | `R12/R16/R32/R36` shunt on West + `C_HF` `VDC` pad on East pinched LS South Drain exit | `12.50–12.75` (launch) -> `10.50–12.50` (trunk; `5.60` right between `MR60` `5.5 mm`-pitch outer pads) | `3.39x – 4.11x` (`1.81x` right at `MR60` pins, 100% of physical pin gap) |
| `M1/SH_B` | `B.Cu` | `3.62` (`y=97.6`) | Diagonal `B.Cu` signal trace sliced through the `B.Cu` `SH_B` pour | `10.50–12.50` (`B.Cu` keepout protected) | `2.90x – 3.45x` |
| `SH_A` (`Q1/Q2`, `Q7/Q8` -> Trunk) | `F.Cu` | `0.70` (step at `y=99.3`) / `2.40` (West slot) / `1.40` (East step) | `C_HF1/4` (`VDC <-> GND`) placed between `Q1` and `Q2` forced `SH_A` around outside edges and into `C71/C75` | `7.48` (inter-FET) -> `12.75` (trunk) | `3.12x` vs slot (`10.7x` vs `0.70 mm` step) |
| `SL_B` (`Q4 -> R12`, `Q10 -> R32`) | `F.Cu` / `B.Cu` | `2.27` (`M0 F.Cu`) / `2.95` (`M1 F.Cu`) / `3.80` (`M1 B.Cu`) | `4.10 mm` `Q5–Q4` South Drain gap shared with `SP1/SN1` Kelvin pair | `5.20` at `0.7 mm` FET pad lip (> `3.65 mm` Source array) -> `6.80` continuous `F.Cu` + `B.Cu` trunk | `2.29x` at pad lip / `3.00x` along trunk |
| `SL_C` (`Q6 -> R16`, `Q12 -> R36`) | `F.Cu` / `B.Cu` | `2.92` (`M1 F.Cu`) / `3.48` (`M0 B.Cu`) | Via/trace intrusion into narrow West `SL_C` turn | `5.20` at `0.7 mm` FET pad lip -> `7.00` continuous `F.Cu` + `B.Cu` trunk | `2.40x` (`F.Cu`) / `2.01x` (`B.Cu`) |

## 2. `DirectFET_L8` Output Window Reference
- **Drain flange (`Pad 1`, 3 pads)**: `5.50 mm` pad span (`X0 ± 2.75 mm`), `6.10 × 7.10 mm` can width.
- **Source array (`Pad 3`, 8 pads)**: `4.55 mm` wide (`X0 ± 2.275 mm`) × `3.65 mm` tall (`[Y0 - 1.275 .. Y0 + 2.375]`), inside a `6.80 mm` clear lateral window (`[Y0 - 3.40 .. Y0 + 3.40]`) on the non-gate side and `5.20 mm` (`[Y0 - 1.80 .. Y0 + 3.40]`) on the gate-exit side.

## 3. Target `220.0 × 115.0 mm` Floorplan (`[0.0, 15.0] .. [220.0, 130.0]`, `+118.0 mm` Channel Symmetry)
- **Channel M1 (`Q12..Q7` at `y = 92.0, rot = -90°`)**:
  - `Q12` (`LS_C`): `x = 21.2` | `Q11` (`HS_C`): `x = 34.2` (`13.0 mm` pitch) -> `R36` at `(14.5, 104.5)`, `SL_C = 7.00 mm`, `SH_C = 7.48 -> 12.70 mm`
  - `Q10` (`LS_B`): `x = 53.2` (`19.0 mm` inter-phase) | `Q9` (`HS_B`): `x = 66.2` (`13.0 mm` pitch) -> `R32` at `(46.75, 104.5)`, `SL_B = 6.80 mm`, `SH_B = 7.48 -> 12.50 mm`
  - `Q7` (`HS_A`): `x = 76.2` (`10.0 mm` shared-`VDC` pitch) | `Q8` (`LS_A`): `x = 89.2` (`13.0 mm` pitch) -> `SH_A = 7.48 -> 12.75 mm`, `Q8` `GND` exits East into central `GND` spine
  - `J2` (`MR60PB-M` M1): `(57.0, 123.0, 180°)` (`J2.3=51.5, J2.2=57.0, J2.1=62.5`)
- **Central Battery Spine (`x = 92.5 .. 126.5`)**:
  - `J3` (`XT90PB-M`): `(110.0, 123.0, 0°)` (`J3.1 GND = 104.55`, `J3.2 VDC = 115.45`)
- **Channel M0 (`Q6..Q1` = exact `+118.00 mm` X-translation of M1)**:
  - `Q6 = 139.2`, `Q5 = 152.2`, `Q4 = 171.2`, `Q3 = 184.2`, `Q1 = 194.2`, `Q2 = 207.2`
  - `R16 = (132.5, 104.5)`, `R12 = (164.75, 104.5)`, `J1 = (175.0, 123.0, 180°)`
- **Routing-Driven Component Placement Optimizations**:
  1. `C_HF1–C_HF6` moved out of intra-phase `SH` channels onto the `VDC`-to-`SL`/`GND` commutation boundaries (`C_HF6` at `(15.0, 88.0)`, `C_HF5` at `(44.2, 88.0)`, `C_HF4` at `(94.0, 88.0)`, and `+118.0 mm` on M0).
  2. `U2` centered at `(55.0, 69.5, -90°)` and `U1` at `(173.0, 69.5, -90°)` with vertical South bootstrap/Kelvin capacitors (`y = 77.2`) aligned directly under their `DRV8301` pins.
  3. `U1` `+5V` buck converter (`D1, L1, C12, C18, C19, C1, R4..R7, C17, C20`) relocated to the East/North-East of `U1` (`x = 183..198, y = 55..72`) right beside `U1` `PH`/`BST_BK` pins `50–56`, eliminating switching-node wrap-around and freeing `U1` North digital fanout.
  4. `U3` / `Q13` / `Q14` brake chopper centered around `x = 110..122, y = 60..72` with `R47/R48` gate resistors West of `Q13/Q14` so `/Power Management/HS` forms a single unbroken `F.Cu + B.Cu` polygon.
  5. `U6` (`STM32F405`) centered at `(110.0, 44.0)` with radially aligned decoupling caps, `4 mm` Westward spacing on `C6,C7,C27,C28`/`TP8–TP11`, and clean `Y1` oscillator spacing (`0` `silk_overlap`).
