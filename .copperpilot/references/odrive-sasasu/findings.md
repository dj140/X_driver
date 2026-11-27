# Reference Findings: `Sasasu/ODrive`

## Provenance & Upgrade Summary
- **Repository**: `https://github.com/Sasasu/ODrive`
- **Commit**: `aa720cff554198ea71cac7a9456401e8a0286b54`
- **License**: Unspecified in repository (inspect-only architectural reference; no graphical/text assets copied).
- **KiCad Upgrade**: Upgraded in-place to KiCad 10.0.8 via `/bin/kicad-cli` (`sch upgrade --force`, `pcb upgrade --force`, `sym upgrade --force`, `fp upgrade --force`).

## Key Architectural & Layout Evidence
1. **DRV8301 to MOSFET Proximity & Gate Drive Loop**:
   - In `ODrive.kicad_pcb`, `U4` (`DRV8301DCAR` at `10.49, 35.40`) and `U5` (`DRV8301DCAR` at `36.58, 35.40`) are placed ~14 mm from the high-side MOSFET row (`y = 49.8 mm`), with 1206 ceramic decoupling capacitors (`C31..C33`, `C51..C53` at `y = 45.1 mm`) compactly arranged so gate drive and current-sense traces remain short (< 12-15 mm).
2. **Brake / AUX Chopper (`LM5109` + Dual MOSFETs)**:
   - `U2` (`LM5109BMA` at `24.55, 40.28`) and brake MOSFETs `Q1` (`24.54, 49.76`) / `Q2` (`24.51, 57.65`) are placed in the power-stage band directly inline with the DC input connector (`J10` at `x = 23.24 mm`), keeping the switching node `HS` completely out of the STM32F405 (`U3` at `25.0, 14.0`) and crystal (`Y2` at `36.38, 15.43`) quiet analog/digital region.
3. **Differential Shunt Sensing & Bulk Capacitor Ground Return**:
   - Shunt sense resistors (`R26`, `R29`, `R41`, `R44`, `500 uOhm`) feed differential RC filters (`120 Ohm` + `2.2 nF`) directly below `U4`/`U5`.
   - Bulk capacitor ground pads connect directly to the low-side power ground plane (`GND`) on the source/return side rather than returning through the shunt sense path.
4. **Thermistor NTC Divider Topology**:
   - Uses `10k` NTC thermistors biased from `+3.3VA` with `3.3k` pull-down resistors to `GNDA` and `2.2 uF` filter capacitors feeding STM32F405 ADC inputs (`PC0`–`PC5` / `PA4`–`PA5`), matching the existing `TH1`–`TH3` topology in `bldc_motor_cntroller`.
