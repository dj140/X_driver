# Custom Project Tools

## `apply_v3_high_power_pours.py`
- **Path**: `./.copperpilot/tools/apply_v3_high_power_pours.py`
- **Interpreter**: `/usr/bin/python3` (KiCad 10.0.8 native `pcbnew` bindings)
- **Purpose**: Idempotently constructs the 17 multi-layer high-power copper zones (`Priority 5` solid motor phase pours `SH_C..A` on `F.Cu`, `Priority 4` solid shunt return pours `SL_C..B` and brake switch-node pour `HS` on `F.Cu`, `Priority 3` monolithic coplanar `VDC` bus bar + local chopper `VDC` pour on `F.Cu`, `In2.Cu` `VDC` plane, and `F.Cu`/`In1.Cu`/`B.Cu` `GND` planes with `ISLAND_REMOVAL_MODE_ALWAYS`) plus collision-checked `0.80 mm / 0.40 mm` `VDC` and `GND` stitching via arrays on a staged candidate of `bldc_motor_cntroller_v3.kicad_pcb`.
