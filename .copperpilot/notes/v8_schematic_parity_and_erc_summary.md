# V8 Schematic STM32 Pinout Restoration, PCB Parity, and ERC Verification Summary

## 1. Completed Units Overview

All five execution units of [v8-schematic-parity-and-erc-cleanup.plan.md](../plans/v8-schematic-parity-and-erc-cleanup.plan.md) have been executed through staged candidates and verified on the promoted primary KiCad `10.0.8` files without altering any existing electrical component values:

1. **Unit 1 — Project-Local KiCad 10 Libraries & Identity-Safe Title Blocks**:
   - Created and registered `bldc_motor_cntroller/bldc_motor_cntroller.kicad_sym` in `bldc_motor_cntroller/sym-lib-table` (`${KIPRJMOD}/bldc_motor_cntroller.kicad_sym`, replacing the broken legacy `/home/sam/.../*.lib` entry) with `DRV8301DCAR` (TI `SLOS719F` pin electrical types: `SDO`=`tri_state`, `~{FAULT}`/`~{OCTW}`=`open_collector`, `AVDD`/`DVDD`=`power_out`, `GVDD`/`BST_*`/`CP*`=`passive`, `PH` `50`=`output`/`51`=`passive`), `IRF7480MTRPBF`, `Net-Tie_2` (`in_bom no`), and `USB_C_Receptacle_USB2.0`.
   - Extracted board-matched custom footprints from `bldc_motor_cntroller_v8.kicad_pcb` into `bldc_motor_cntroller.pretty`, `MG-WDSON-8.pretty`, and `Package_SON.pretty`, registered in `bldc_motor_cntroller/fp-lib-table` without shadowing stock `Crystal` or `TestPoint` libraries.
   - Sanitized all title blocks across `bldc_motor_cntroller_v8.kicad_sch` and the 5 child sheets (`Title: Open Drive` + subsheet titles, `Revision: v8`, `Company: ""`), and removed third-party copyright properties from `U1/U2` (`DRV8301DCA`).

2. **Unit 2 — Restored Original 64-Pin `U6` (`STM32F405RGTx`) Schematic Pinout**:
   - Restored all 21 scrambled left-side `U6` pins in `bldc_motor_cntroller/microcontroller_interface.kicad_sch` to match `bldc_motor_cntroller/microcontroller_interface.sch` 1:1 on the `1.27 mm` (`50 mil`) schematic connection grid:
     - `PH0 (Pin 5)` & `PH1 (Pin 6)` -> `8 MHz` resonator `Y1` + `C83/C84` (`12pF`)
     - `VCAP_1 (Pin 31)` -> `C88` (`2.2uF 16V`), `VCAP_2 (Pin 47)` -> `C90` (`2.2uF 16V`)
     - `PC0..PC3 (Pins 8..11)` -> `M0_SO1`, `M0_SO2`, `M1_SO2`, `M1_SO1` (`ADC123_IN10..13`)
     - `PC4 (Pin 24)` -> `GPIO_5`, `PC5 (Pin 25)` -> `M0_TEMP`
     - `PC6..PC8 (Pins 37..39)` -> `M1_AH`, `M1_BH`, `M1_CH` (`TIM8_CH1..3`)
     - `PC9 (Pin 40)` -> `M0_ENC_Z`, `PC15 (Pin 4)` -> `M1_ENC_Z`
     - `PC10..PC14 (Pins 51..53, 2, 3)` -> `SPI_SCK`, `SPI_MISO`, `SPI_MOSI`, `SPI_M0_nCS`, `SPI_M1_nCS`
     - `PD2 (Pin 54)` -> `nFAULT`, `NRST (Pin 7)` -> `C86` (`100nF 16V`), `BOOT0 (Pin 60)` -> `MCU_BOOT0`
   - Placed explicit `no_connect` markers on the auxiliary `TEMP_SENSE_2` root sheet pins (`TH4/R62/C101` and `TH5/R63/C102` retained for 100% PCB footprint parity).

3. **Unit 3 — Mounting Hole, MPN, BOM Attribute Parity & ERC Cleanup**:
   - Updated `H1–H4` on `bldc_motor_cntroller_v8.kicad_sch` to `MountingHole:MountingHole_3.2mm_M3_Pad_Via` (`in_bom no`) and added corner mounting holes `H7–H10` (`MountingHole:MountingHole_4.3mm_M4_Pad` on `GND`, `in_bom no`) with dual project instances.
   - Aligned `C78–C81` `MPN = GCM155L8EH104KE07D`, `J3` `MPN = XT90PB-M`, and `in_bom no` on `TP1–TP6` & `NT1–NT8` without changing electrical values.
   - Added `PWR_FLAG` symbols on `VDC`, `GND`, `+5V`, and `GVDD`; resolved `hier_label_mismatch` (`PWRGD`), `multiple_net_names` (`GNDA`/`VBUS`/`SL_A`), `same_local_global_label` (`GVDD`), `label_multiple_wires` (`SH_C`), and `U7` `no_connect` alignment.

4. **Unit 4 & Unit 5 — Senior Schematic Sweep & `bldc_motor_cntroller_v8.kicad_pcb` Sync**:
   - Unrouted the 24 stale `U6` local stub segments (`PH0/PH1/PC3/PC4`), synced all `241` schematic components (`173` nets) and custom symbol fields onto `bldc_motor_cntroller_v8.kicad_pcb`, placed `C88` (`76.5, 53.2 mm`) and `C90` (`83.4, 43.25 mm`) adjacent to `U6` `VCAP_1` (`Pad 31`) and `VCAP_2` (`Pad 47`) with `0` courtyard overlaps, and refilled all `53` copper zones.

---

## 2. Verification Metrics (Baseline vs. Promoted v8)

| Check / Metric | Baseline (`v8`) | Promoted (`v8`) | Status |
|---|---|---|---|
| **Schematic ERC Errors (`run_erc`)** | `31` | **`0`** | Pass |
| **`lib_symbol_issues` / `footprint_link_issues` (`run_erc`)** | `29` | **`0`** | Pass |
| **`multiple_net_names` / `same_local_global_label` / `label_multiple_wires`** | `7` | **`0`** | Pass |
| **Pre-existing Legacy `endpoint_off_grid` Warnings** | `484` | `477` (`0` new) | Unchanged brownfield |
| **PCB Zone Clearance Violations (`clearance`)** | `8` | **`0`** | Pass |
| **PCB Unresolved Library Footprints (`lib_footprint_issues`)** | `26` | **`0`** | Pass |
| **PCB Parity: `footprint_symbol_mismatch`** | `26` | **`0`** | Pass |
| **PCB Parity: `footprint_symbol_field_mismatch`** | `185` | **`0`** | Pass |
| **PCB Parity: `extra_footprint` on `H7–H10`** | `4` | **`0`** | Pass (`8` decorative `G***` silk graphics retained) |
| **PCB Parity: Electrical `net_conflict`** |Scrambled `U6` | **`0`** electrical (`64` `U1/U2` `"V"` thermal via pads on `GND`) | Pass |
| **PCB Courtyard Overlaps / Out-of-Board** | `0` | **`0`** | Pass |
| **Remaining Out-of-Scope Signal Routing (`unconnected_items`)** | `265` | `273` (reflects restored `U6` nets; signal autorouting out of scope) | Disclosed |
| **Fine-Pitch `0.5 mm` Pad Solder-Mask Web (`solder_mask_bridge`)** | `189` | `181` (`U6` LQFP-64 / `U1,U2` HTSSOP-56 pad mask expansion vs `0.05 mm` web rule) | Disclosed |

---

## 3. Pre-Order Engineering & DFM Advisories (Values Preserved Per Scope)

- **Bus Capacitor MPN & Voltage Rating (`C39–C77`)**: Existing `Value = 100uF 50V` (`1206`) and `MPN = GMK105CC6105MV-F` (`0402 1 uF 35 V`) were preserved unchanged per request. Before PCBA ordering, substitute a valid `1206` >= `63 V` X7R MLCC MPN (plus external low-ESR bulk electrolytic capacitance across `J3`) if operating up to `48–56 V`.
- **Power Stage MOSFET Voltage Rating (`Q1–Q12`)**: Existing `IRF7480MTRPBF` (`40 V` V_DSS) was preserved unchanged per request; limit DC bus voltage `VDC <= 30–32 V` with `IRF7480MTRPBF`, or substitute >= `60–80 V` `MG-WDSON-8` / `DirectFET` devices for higher bus voltages.
- **Fine-Pitch Solder-Mask Expansion (`U6, U1, U2`)**: `bldc_motor_cntroller_v8.kicad_pcb` retains `181` pre-existing `solder_mask_bridge` DRC flags between `0.5 mm`-pitch pads on `U6` (`LQFP-64`) and `U1/U2` (`DRV8301DCA`) due to pad solder-mask expansion against the `0.05 mm` minimum mask web constraint; set footprint solder-mask margin to `0 mm` (or confirm ENIG + `0.075 mm` mask dam capability with the selected fabricator) during the final PCB routing/DFM phase.
