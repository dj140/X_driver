# v9_13 Complete Routing Plan

Target: `bldc_motor_cntroller_v9_13/bldc_motor_cntroller_v9_13.kicad_pcb` (staged at `.copperpilot/tmp/staging/v9_13_complete/candidate/bldc_motor_cntroller_v9_13/`).
Baseline: `61` unconnected items across `23` nets, `5` minor clearance errors (`0.1513–0.1790 mm`), `0` courtyard overlaps, `0` ERC errors.
Plane policy: `In1.Cu` (`GND`) strictly locked (`0` tracks); lower `In2.Cu` (`y >= 54.80 mm`, `VDC`) protected by `In2_VDC_Track_Keepout`; upper `In2.Cu` (`y < 54.80 mm`) selectively open for slow/medium signals and supply rails. No rule relaxation.

## Ordered Net Groups (12-run budget, <= 3 attempts/group)

1. **Pre-pass (Stitching & Clearance Reset):** Drop `2×` `GND` (`(68.82, 67.70)`, `(138.69, 56.24)`) and `2×` `VDC` (`(32.75, 84.55)`, `(75.75, 82.95)`) `0.60/0.30 mm` stitching vias for detached `F.Cu` pour islands; unroute the `5` nets with minor clearance errors (`USB_J4_DP/DN`, `nFAULT`, `Net-(D6-K)`, `+5V` stub at `U3`, `+3.3VA` stub at `TH5`) so FreeRouting re-routes them cleanly.
2. **Group R1 — High-Speed USB (`F.Cu`/`B.Cu` only, `--no-in2`):** `/I/O Interface/USB_DP`, `/I/O Interface/USB_J4_DP`, `/I/O Interface/USB_J4_DN` (measure skew with `lengths`).
3. **Group R2 — DRV8301 Power-Stage & Control (`F.Cu`/`B.Cu` only, `--no-in2`):**
   - **R2a (M0 `U7`):** `/Motor Driver/GH_B`, `/Motor Driver/SH_C`, `/Motor Driver/SL_B`, `/Motor Driver/SL_C`, `Net-(D6-K)`, `Net-(U7-VSENSE)`, `/Microcontroller Interface/nFAULT`.
   - **R2b (M1 `U8`):** `/Motor_Driver2/SH_C`, `/Motor_Driver2/SL_B`, `/Motor_Driver2/SL_C`, `/Motor_Driver2/nOCTW`.
4. **Group R3 — Upper-Board Signals & Brake (`F.Cu`/`B.Cu` + upper `In2.Cu`):** `/Microcontroller Interface/M0_SO1`, `/I/O Interface/ENC1_Z`, `/I/O Interface/GPIO_2`, `/I/O Interface/GPIO_7`, `OVP_IN_LI`, `/Power Management/HS`.
5. **Group R4 — Power & Supply Rails (`F.Cu`/`B.Cu` + upper `In2.Cu`):**
   - **R4a (`VDC` & `+5V`):** `VDC`, `+5V`.
   - **R4b (`GVDD` & `+3.3VA`):** `GVDD`, `+3.3VA`.
   - **R4c (`+3.3V` & remaining `GND` ties):** `+3.3V`, `GND`.
6. **Cleanup & Phase Exit:** Prune dangling tracks/vias, refill all copper zones, run `run_drc` (`0` physical errors, `0` unconnected), load `pcb-dfm-engineer` section `Sequence`, promote to `bldc_motor_cntroller_v9_13/`, and commit checkpoint.
