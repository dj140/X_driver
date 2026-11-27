# Board Via Removal Summary (`bldc_motor_cntroller_v8.kicad_pcb`)

## 1. Executed Change
Per user confirmation to clear all board-level vias prior to signal routing, all `531` board-level `(via ...)` items were removed from `bldc_motor_cntroller/bldc_motor_cntroller_v8.kicad_pcb` via canonical staging while preserving 100% of existing footprints, copper zones, and routed `F.Cu` signal/charge-pump/bootstrap segments, followed by full zone refill (`fill_pcb_zones`) and post-promotion `run_drc` verification.

## 2. Before vs. After Inventory & DRC Metrics

| Metric | Before (`1812ed8`) | After Promotion | Notes |
|---|---:|---:|---|
| **Board-Level Vias (`PCB_VIA`)** | `531` | **`0`** | All `531` power/ground stitching vias removed (`U1/U2` footprint thermal PTH pads `"V"` remain part of `DRV8301DCA` footprints) |
| **Routed `F.Cu` Segments** | `120` | **`120`** | Preserved (`BOOT0`, `SWCLK`, `SWDIO`, `NRST`, `AVDD`, `DVDD`, `BST_A..C/BK`, `CP1/CP2`, `D1–D4`, `F1`) |
| **Copper Zones (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`)** | `53` | **`53`** | All zone outlines preserved and refilled cleanly |
| **Placed Footprints** | `249` | **`249`** | Untouched |
| **DRC Errors (`run_drc`)** | `260` | **`260`** | **`0` new DRC errors** (`181` pre-existing `0.5 mm`-pitch `solder_mask_bridge` + `79` non-electrical `U1/U2` `"V"` / `G***` parity warnings) |
| **DRC Warnings** | `526` | **`530`** | `+4` expected `isolated_copper` warnings on `B.Cu` `SL_B`/`SL_C` mirror pours (`Z38, Z40, Z43, Z49`) awaiting post-route re-stitching |
| **Unconnected Items** | `273` | **`302`** | `+29` ratsnest links across `25` SMD-only (`TH=0`) `F.Cu` power/shunt islands that require vias after signal routing |

- **Promoted Primary SHA-256**: `7de0963f71cac494beac8f298b9cce64b7d9e1f83a07329fb311630692d95425`
- **Verification Render**: `./.copperpilot/tmp/v8_no_vias_candidate.png`

## 3. Post-Routing Re-Stitching Checklist (`TH=0` Power & Shunt Islands)
After completing signal routing, re-stitch these SMD-only (`TH=0`) copper islands before fabrication:
1. **10 Single-Pad MOSFET Drain-Tab Pockets (`F.Cu` -> `In2.Cu` `VDC` or `B.Cu` `SH_A..C`)**: `Q2.9`, `Q3.10`, `Q4.10`, `Q5.9`, `Q6.10`, `Q8.9`, `Q9.10`, `Q10.10`, `Q11.9`, `Q12.10`.
2. **6 High-Side MOSFET Source Switch-Node Islands (`F.Cu` -> `B.Cu` `SH_A..C`)**: `Q1`, `Q3`, `Q5` (`M0`) and `Q7`, `Q9`, `Q11` (`M1`) source pours (`Z09, Z13, Z20, Z24, Z28, Z37`) + corresponding `LS` drain `F.Cu <-> B.Cu` phase-sharing arrays.
3. **9 Isolated `VDC` Input Islands (`F.Cu` -> `In2.Cu` `VDC`)**: High-side drain/`C_HF1–C_HF6` islands (`Z00, Z10, Z11, Z17, Z23, Z31`), outer `1206` bus-cap banks (`Z07, Z26`), and `Q13` brake-chopper `VDC` island (`Z27`), plus `J3` `XT90` `VDC` collar vias.
4. **4 Isolated `GND` Islands (`F.Cu` -> `In1.Cu` `GND`) & 4 `B.Cu` Shunt Mirror Pours**: Phase-B shunt `GND` pads `R12.1` and `R32.1` (`Z25#0, Z25#1`), inner bus-cap `GND` pockets `C47/C51` and `C69/C70` (`Z25#2, Z25#3`), and `SL_B`/`SL_C` `F.Cu <-> B.Cu` pours (`Z38, Z40, Z43, Z49`).
