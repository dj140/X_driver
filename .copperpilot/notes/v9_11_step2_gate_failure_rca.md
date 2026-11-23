# Step 2 Supply-Tap Routing Gate Failure RCA (`bldc_motor_cntroller_v9_11.kicad_pcb`)

- **Gate outcome**: **FAILED** (`0 unconnected connections on scope nets` not met after 3 attempts per group).
- **Board status**: **Unchanged** (`bldc_motor_cntroller_v9_10/bldc_motor_cntroller_v9_11.kicad_pcb` not modified; no `.bak` created; staging deleted).
- **Staged best**: `16 / 19` scope connections routed on `F.Cu` + `B.Cu` only (`1,329` segments, `605` vias, `0` new DRC errors vs. `.copperpilot/baseline_v9_10.rpt` after zone refill, `non_target_copper = unchanged`).

## Unconnected Scope Nets & Geometric Obstacles

| Net | Open Endpoints | Required Throat (`W + 2×Clr`) | Measured Throat | Exact Obstacle |
|---|---|---|---|---|
| `/Motor Driver/DVDD` | `U7.23 (168.75, 59.68)` <-> `C61.1 (168.85, 55.28)` | `0.6600 mm` (`Supply`: `0.30` W, `0.18` Clr) | `0.5942 mm` N / `0.2480 mm` S / `0.1952 mm` E/W | North: `C82.1` (`+3.3VA`, `[168.19..168.81, 57.95..58.51]`) to `U7.22` (`[169.10..169.40, 59.04..60.31]`) = `0.5942 mm`. South: `M0_CH` `F.Cu` track at `y = 60.64` (`top = 60.56`) leaves `0.2480 mm` below `U7.23` (`bottom = 60.312`). Boxed in on all 4 sides. |
| `/Motor_Driver2/DVDD` | `U8.23 (50.75, 59.68)` <-> `C107.1 (50.85, 55.28)` | `0.6600 mm` (`Supply`: `0.30` W, `0.18` Clr) | `0.5942 mm` N (`U8.23`); `0.5000 mm` E (`C107.1`) | North: `C121.1` (`+3.3VA`, `[50.19..50.81, 57.95..58.51]`) to `U8.22` (`[51.10..51.40, 59.04..60.31]`) = `0.5942 mm`. At `C107.1`: boxed in by `M1_SO1` (West, `x = 49.45`), `M1_CH` (East, `x = 51.75`, gap `0.50 mm`), `C107.2` (North), and `GND` via `(50.50, 56.60)` (South). |
| `+3.3VA` | `U9.13`/`C148.1`/`C149.1` (`102.785, 47.40`) <-> main `+3.3VA` trunk (`91.38, 66.08`) | `0.6600 mm` track / `0.9600 mm` via (`Supply`) | `F.Cu`/`B.Cu` pocket sealed | `U9.13 -> C148.1 -> C149.1` routed on `F.Cu` (`0.30 mm`), but `C148`/`C149` are surrounded on `F.Cu` by `M1_SO1` (North, `y = 45.25`), `C148.2`/`C149.2` + `GND` vias (West, `x = 101.00`), `U9.14–16` (East, `x = 103.55`), and `GPIO_5` via `(102.19, 48.74)` + track (South-West); on `In2.Cu` by `GPIO_3` (`x = 103.31`); and on `B.Cu` by `M1_BH` (`y = 50.17`) + under-`U9` keepout (`[105..115, 39..49]`). |

## Runs Used

| Run | Group | Nets | Seconds | Result |
|---|---|---|---|---|
| 1 | (c) Attempt 1 | `/Motor Driver/DVDD`, `/Motor_Driver2/DVDD`, `Net-(U7-BST_BK)`, `Net-(U8-BST_A)` | `95.71 s` | `Net-(U7-BST_BK)` & `Net-(U8-BST_A)` routed (`13` `F.Cu` segs, `0` vias, `0` new DRC errors); both `DVDD` nets open |
| 2 | (c) Attempt 2 | `/Motor_Driver2/DVDD` | `62.73 s` | `0` tracks added (`1` pass); open |
| 3 | (a)+(b) Attempt 1 | `+3.3VA` | `100.42 s` | `14/15` connections routed (`56` `F.Cu` + `14` `B.Cu` segs, `9` vias, `305.83 mm`, `0` new DRC errors); `U9.13`/`C148`/`C149` open |
| 4 | (a)+(b) Attempt 2 | `+3.3VA` | `71.86 s` | Reverted (`1` new DRC error, `U9.13`/`C148`/`C149` still open) |
| 5 | (a)+(b) Attempt 3 | `+3.3VA` (fresh) | `91.92 s` | `14/15` connections routed (`70` segs, `9` vias, `305.83 mm`, `0` new DRC errors); `U9.13`/`C148`/`C149` open |
| 6 | (c) Attempt 3 | `/Motor Driver/DVDD`, `/Motor_Driver2/DVDD` | `69.79 s` | `0` tracks added (`1` pass); both `DVDD` nets open |

## Options to Resolve

1. **Assign `DVDD` nets to `Gate_Drv` (`0.20 mm` width, `0.18 mm` clearance -> `0.56 mm < 0.5942 mm`)** or **shift `C82` (`C145`) and `C121` (`C153`) `0.35 mm` west/north** so `U7.23` and `U8.23` can exit north to `C61.1` / `C107.1`.
2. **Unfreeze `GPIO_5` (1 local `F.Cu` track/via at `(102.19, 48.74)`) or allow `In2.Cu` escape for `+3.3VA` at `C149.1`** so the `U9.13`/`C148`/`C149` island joins the `+3.3VA` star.
3. **Accept partial promotion (`16/19` routed, `0` new DRC errors)** for `Net-(U7-BST_BK)`, `Net-(U8-BST_A)`, and the `14/15` routed `+3.3VA` connections.
