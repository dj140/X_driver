# Reference Findings: `garypippi/pippitank`

## Provenance & Upgrade Summary
- **Repository**: `https://github.com/garypippi/pippitank`
- **Commit**: `665d1d1d15a6fa854aae7045a3e9a7719a26daaa`
- **License**: MIT License (permissive; no delivered board attribution required)
- **KiCad Upgrade**: Upgraded in-place from KiCad 9.0 to KiCad 10.0.8 via `/usr/bin/kicad-cli` (`sch upgrade`, `pcb upgrade`, `sym upgrade`, `fp upgrade`).

## Inspected Artifacts & Relevance
1. **3-Phase ESC Connector (`J2` in `pippitank-esc-adaptor.kicad_sch` / `.kicad_pcb`)**:
   - Uses a standard 3-pin generic connector symbol (`Connector:Conn_01x03_Pin` / `Connector_Generic:Conn_01x03`) mapped to a 3-pin AMASS PCB footprint (`Connector_AMASS:AMASS_MR30PW-M_1x03_P3.50mm_Horizontal`), matching the baseline `J1` and `J2` in `bldc_motor_cntroller`.
   - Pin 1 uses a polarized `roundrect` through-hole pad at `(0, 0)`, while Pins 2 and 3 use circular through-hole pads spaced along the positive X axis.
2. **Adaptation for `AMASS_MR60PB-M_1x03_P5.50mm_Vertical`**:
   - Neither `garypippi/pippitank` nor the stock KiCad 10 `Connector_AMASS.pretty` library includes the vertical `MR60PB-M` footprint.
   - Mechanical dimensions for `MR60PB-M` are taken directly from the official Changzhou Amass Electronics product specification (`c1ae9604bbe795ebfd366c9063019e3e.pdf`, page 16–17) and paired with the existing project-local vertical XT90 footprint convention (`AMASS_XT90-M_1x02_P10.90mm_Vertical.kicad_mod`):
     - **Pin Pitch**: `5.50 mm` (3 pins in 1x03 line: Pin 1 at `(0.0, 0.0)`, Pin 2 at `(5.5, 0.0)`, Pin 3 at `(11.0, 0.0)`).
     - **Solder Pin Diameter**: `3-Ø3.0 mm` (`3.0 mm` solder leg length).
     - **Plated Through-Hole Drill & Pad Size**: `3.30 mm` drill diameter (+0.30 mm clearance over Ø3.0 mm pin) with `4.80 mm` pad diameter (`roundrect` on Pin 1, `circle` on Pins 2 and 3), yielding `0.70 mm` inter-pad copper clearance (`> 0.40 mm` DRC clearance rule).
     - **Housing Envelope**: `21.60 mm` width × `9.80 mm` height (`X` from `-5.30 mm` to `+16.30 mm`, `Y` from `-4.90 mm` to `+4.90 mm` relative to Pin 1 at `(0, 0)`), with polarized chamfered left end on `F.SilkS` and `F.Fab`, and `0.50 mm` courtyard margin (`F.CrtYd` spanning `X: -5.80..16.80 mm`, `Y: -5.40..5.40 mm`).
