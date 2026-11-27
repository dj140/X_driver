# `bldc_motor_cntroller_v9_8` Selective-`In2.Cu` Routing Status & RCA

## Promoted State (`bldc_motor_cntroller_v9_8/`)
- **Board & Layer Policy**: `220.0 × 115.0 mm` 4-layer (`70 µm` outer / `35 µm` inner). `In1.Cu` (`GND`) remains an unbroken `power` plane; `In2.Cu` is set to `mixed` with `In2_VDC_Track_Keepout` (`tracks not_allowed`) protecting the lower `VDC` plane (`y >= 61.8 mm`, and `x >= 195.2, y >= 54.8 mm`), while upper `In2.Cu` (`+3.3V`) is selectively open for slow/medium signals.
- **Cleanup Completed**: Removed `16` duplicate zones from the prior `v9_8` snapshot (`3 -> 0` `zones_intersect` errors).
- **Newly Routed Nets (`150 -> 121` unconnected items, `1,266 -> 1,415` segments, `609 -> 632` vias)**:
  - `CAN_H`, `CAN_L` (skew `3.02 mm` vs `5.0 mm` target), `USB_CC1`, `USB_CC2`, `Net-(F1-Pad1)`, `Net-(D4-A)`
  - `OVP_IN_HI`, `OVP_IN_LI`, `/Power Management/HS`, `/Motor Driver/PWRGD`, `/Motor Driver/nOCTW`, `/Motor Driver/TEMP_SENSE_2`, `/Motor_Driver2/TEMP_SENSE_2`, `Net-(D3-A)`
  - `/I/O Interface/GPIO_3`, `GPIO_4`, `GPIO_7`, `DEBUG_SWDIO`, `DEBUG_SWCLK`, `/Microcontroller Interface/VBUS_S`, `M1_TEMP`
  - Partial `GVDD` / `+5V` ties

## Post-Promotion Verification
| Check | Result | Details |
|---|---|---|
| `run_erc` | **0 errors** | `420` pre-existing warnings (`418` `endpoint_off_grid`, `2` `multiple_net_names`) |
| `run_drc` (Schematic Parity) | **0 errors** | `0` schematic parity issues |
| `query_design(what="overlaps")` | **0 overlaps** | `307` footprints, `0` courtyard overlaps, `0` outside board |
| `run_drc` (Copper / Rule Errors) | **8 errors** (down from `11`) | `8` minor clearance errors (`0.157–0.177 mm` vs `0.160/0.180 mm` at `U11`, `C136`, `R55`, `U4`, `U5`); `0` `zones_intersect` |
| `run_drc` (`unconnected_items`) | **121 remaining** (down from `150`) | `63` `GND` + `29` `+3.3V` plane-tie SMD pads + `29` signal/supply items below |
| 3D Model Render Check | **Not re-run** | No footprint geometry changes in this routing unit |

## Routing Budget Exhaustion & Root-Cause Analysis (Remaining `121` Items)
The 12-run per-board FreeRouting budget for this pass is exhausted. Remaining open items fall into four root-cause buckets:

| Bucket | Unconnected Count | Nets | Root Cause |
|---|---|---|---|
| Plane-tie SMD pads | `92` | `GND` (`63`), `+3.3V` (`29`) | Unrouted local `F.Cu` pad-to-via dogbones into `In1.Cu` (`GND`) and `In2.Cu` (`+3.3V`); deferred until signal routing finishes so vias do not block signal channels |
| Supply rails (`0.30/0.50 mm` tracks into `0.50 mm`-pitch pins) | `14` | `+3.3VA` (`8`), `GVDD` (`2`), `+5V` (`2`), `VDC` (`2`) | `Supply` (`0.30 mm` width, `0.18 mm` clearance) entering `0.50 mm`-pitch `U1`/`U2` pads (`0.3048 mm` pad) leaves only `0.0176 mm` margin, triggering `0.1787 mm` vs `0.1800 mm` clearance reverts on `U1.15`; `U2.13` (`GVDD`) was also pinched by `Net-(U2-DC_CAL)` |
| USB-C entry pair | `8` | `USB_J4_DP` (`4`), `USB_J4_DN` (`4`) | Unrouted to clear `0.179 mm` `J4`/`U8` clearance and `18.7 mm` skew; needs co-routing with `Net-(F1-Pad1)` and `USB_CC1`/`USB_CC2` |
| Local single-pad pin-entry pinches | `7` | `AUX_TEMP` (`1`), `/Motor_Driver2/nOCTW` (`1`), `Net-(U3-HO)` (`1`), `Net-(U2-DC_CAL)` (`1`), `/Motor Driver/SH_C` (`1`), plus `2` `VDC` (`R66.1`, `C36.1`) | `U2.5` (`nOCTW`) boxed by `nFAULT` stub; `U3.7` (`HO`) boxed by `/Power Management/HS`; `C15.1` (`SH_C`) sits in `F.Cu` `U1` south fanout |

## Recommended Options to Close Remaining `121` Connections
1. **Continue another surgical FreeRouting pass (no rule changes)**: Co-route `USB_J4_DP/DN` with `Net-(F1-Pad1)`/`USB_CC1/2`, co-route `nOCTW+nFAULT`, `U3-HO+HS`, `AUX_TEMP`, and `SH_C`, then route `+3.3VA`/`GVDD`/`+5V`/`VDC` in small 1–2 net groups, and finally fan out the `92` `GND`/`+3.3V` plane-tie vias.
2. **Placement relief**: Shift `U1`/`U2` north passives (`R39/R40`, `C26`) and `U3`/`R47` by `1–2 mm` to eliminate the `0.50 mm`-pitch pin-entry pinches on `U2.5`, `U2.13`, and `U3.7`.
3. **Rule/stackup adjustment (requires approval)**: Neck `Supply` pad-entry width to `0.25 mm` at `U1`/`U2` (matching the original approved pad-entry table) or switch to 6 layers if you want dedicated signal layers without `In2.Cu` `+3.3V` plane sharing.
