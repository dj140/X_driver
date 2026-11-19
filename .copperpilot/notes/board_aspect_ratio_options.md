# Board Aspect Ratio Evaluation: Wider & Shorter vs. Current `130.0 × 98.5 mm`

## 1. Current Board Footprint & Vertical Dead Space
- **Current Outline (`Edge.Cuts`)**: `130.0 mm × 98.5 mm` (`x = 10.0..140.0 mm`, `y = 15.0..113.5 mm`, area = `128.05 cm²`).
- **Why the Current Board Feels Tall (`98.5 mm`)**:
  - The power stage (`U1`/`U2` at `y = 78.5 mm`, DirectFET row `Q1–Q12` at `y = 89.5 mm`, shunts at `y = 98.5 mm`, and `MR60PB-M` / `XT90` connectors `J1–J3` at `y = 107.5 mm`) occupies the bottom `40 mm` (`y = 73.5..113.5 mm`).
  - The signal/logic stage (`J5–J11` JST-SH headers, `J4` USB-C, `U7` CAN, `U4`/`U5` LDOs, and `U6` STM32F405) needs only `~32–35 mm` of vertical height (`y = 38.0..70.0 mm`), leaving **`~20 mm` of unused vertical height** in the upper half of the board.

## 2. How Compacting the DirectFETs Changes the Width Requirement
- In the current layout, `Q1–Q12` sit at `0°` (`7.35 mm` wide courtyard on an `8.5–17.0 mm` pitch), so each 6-FET motor bank spans **`42.5 mm`** horizontally (`85.0 mm` for both banks).
- Rotating `Q1–Q12` to `±90°` (`5.10 mm` wide courtyard on a `5.5 mm` HS-to-LS pitch and `11.5 mm` leg-to-leg pitch) shrinks each 6-FET bank from `42.5 mm` to **`28.5 mm`**—freeing **`28.0 mm` of horizontal width** across the power row without making the board wider, or giving generous room if we also widen the board by `10–20 mm`.

## 3. Aspect Ratio Options

| Option | Dimensions (`W × H`) | Board Area | Key Electrical & Mechanical Impact |
| :--- | :--- | :--- | :--- |
| **Option A: Shorter + Slightly Wider (Recommended)** | **`140.0 × 78.5 mm`** (`x = 5..145`, `y = 35..113.5`) | `109.9 cm²` (`-14%` area) | Drops top edge by `20 mm` (`J5–J11` at `y = 40.5`, `U6` at `y = 58.0`, `U1/U2` at `y = 78.5`), cutting MCU-to-DRV trace lengths by `~40%` while adding `10 mm` width for wide `J3` 60 A bus pours, local per-leg `1206` ceramics, and `U1` buck loop clearance. |
| **Option B: Wider & Ultra-Short Strip** | **`150.0 × 73.5 mm`** (`x = 0..150`, `y = 40..113.5`) | `110.3 cm²` (`-14%` area) | Places `U4/U5` LDOs, `U7` CAN, and `J4` USB-C laterally beside `U6` (`y = 56.0`), with `20 mm` extra width along the bottom row so all 29× `1206` bus caps and the brake chopper sit in-line with the FET legs. |
| **Option C: Shorter Only (Keep `130 mm` Width)** | **`130.0 × 78.5 mm`** (`x = 10..140`, `y = 35..113.5`) | `102.1 cm²` (`-20%` area) | Preserves existing `130 mm` left/right mounting hole X-spacing (`H1–H4`, `H7–H10`) while removing `20 mm` of dead vertical height; relies on the `28.5 mm` compacted `±90°` DirectFET banks for horizontal clearance. |
| **Option D: Keep Current Outline** | **`130.0 × 98.5 mm`** (`x = 10..140`, `y = 15..113.5`) | `128.1 cm²` | Leaves `Edge.Cuts`, mounting holes `H1–H4`/`H7–H10`, and top JST-SH connectors `J5–J11` at their current coordinates and applies the power-stage fixes in place. |
