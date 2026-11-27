# Custom Project Tools

## `apply_v3_high_power_pours.py`
- **Path**: `./.copperpilot/tools/apply_v3_high_power_pours.py`
- **Interpreter**: `/usr/bin/python3` (KiCad 10.0.8 native `pcbnew` bindings)
- **Purpose**: Idempotently constructs the 17 multi-layer high-power copper zones (`Priority 5` solid motor phase pours `SH_C..A` on `F.Cu`, `Priority 4` solid shunt return pours `SL_C..B` and brake switch-node pour `HS` on `F.Cu`, `Priority 3` monolithic coplanar `VDC` bus bar + local chopper `VDC` pour on `F.Cu`, `In2.Cu` `VDC` plane, and `F.Cu`/`In1.Cu`/`B.Cu` `GND` planes with `ISLAND_REMOVAL_MODE_ALWAYS`) plus collision-checked `0.80 mm / 0.40 mm` `VDC` and `GND` stitching via arrays on a staged candidate of `bldc_motor_cntroller_v3.kicad_pcb`.

## `apply_v9_4_unit2_pcb.py`
- **Path**: `./.copperpilot/tools/apply_v9_4_unit2_pcb.py`
- **Interpreter**: `/usr/bin/python3` (KiCad 10.0.8 native `pcbnew` bindings)
- **Purpose**: Applies `v9_4` Unit 2 PCB updates strictly on a staged candidate of `bldc_motor_cntroller_v9_4.kicad_pcb`: aligns `H1` `(5.50, 92.00)` and `H3` `(214.50, 92.00)` on the FET centerline, translates `U1`/`U2` driver clusters `-5.00 mm` North, places `6 × 10` (`60 × 1206`) phase-leg `VDC` decoupling capacitor banks, clears all components out of `y = [81.60 .. 97.40 mm]` (`>= 5.22 mm` North of FET courtyards / `5.945 mm` North of `DirectFET_L8` cans and `0` inter-FET parts) with DRC-enforced `footprints not_allowed` rule areas, extends zero-via `F.Cu` `SL_B`/`SL_C` return strips for `C_HF2/3/5/6`, and stitches all `60` `1206` capacitors while preserving `>99%` solid `In1.Cu` `GND`.

## `chain_pcb_segments.py`
- **Path**: `./.copperpilot/tools/chain_pcb_segments.py`
- **Interpreter**: `python3`
- **Purpose**: Post-processes FreeRouting SES-imported `(segment ...)` blocks on a staged candidate `.kicad_pcb` (collapsing `< 8 µm` SES quantization slivers, merging `~180°` collinear pairs, and ordering segments head-to-tail along degree-2 chains) so `pcbnew.ExportSpecctraDSN` emits continuous multi-point `(wire (path ...))` polylines rather than fragmented 2-point records that trigger `PolylineTrace.combine` recursion in FreeRouting 2.2.4 at coordinates `>= 100 mm`. Never creates or invents routing.
