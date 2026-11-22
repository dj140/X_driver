---
required_inputs: [query, kind, platform, optional project_dir and library path overrides]
artifact_outputs: [structured JSON search results with summary, symbol pin and footprint pad details]
---

# Skill: kicad_lib_search

## Objective
Search KiCad symbol, footprint, and 3D model libraries on the user's machine,
and read symbol pins or footprint pads without parsing library files.
Use installed KiCad stock libraries and project-local libraries such as
`${KIPRJMOD}/555_badge.kicad_sym`, `${KIPRJMOD}/*.pretty`, and
`${KIPRJMOD}/libs/3dmodels`.

## Platform defaults (linux)
- Symbols: `/usr/share/kicad/symbols`
- Footprints: `/usr/share/kicad/footprints`
- 3D models: `/usr/share/kicad/3dmodels`
- Environment overrides: `KICAD10_SYMBOL_DIR, KICAD10_FOOTPRINT_DIR, KICAD10_3DMODEL_DIR`

## Steps
1. Run `.copperpilot/skills/kicad_lib_search/main.py search` with `--platform linux` and `--project-dir .`.
2. Choose `--kind symbol`, `footprint`, `model`, or `all`.
3. Pass `--query` using symbol names, package names, footprint ids, or model filenames.
4. Read the JSON `summary` and footprint `results[].library_path` / `results[].footprint_id` (or symbol `results[].symbol_id`) values for schematic/PCB work. Pass footprint `library_path` and `footprint_id` directly into `place_pcb_footprint`.
5. Override search roots with `--symbol-dir`, `--footprint-dir`, or `--model-dir` when needed.

## Pin and pad details
Do not parse `.kicad_sym` / `.kicad_mod` files yourself (no `python -c`,
`grep` or `sed` over stock libraries). Use these commands; they accept the
same `--platform`, `--project-dir`, and `--symbol-dir` / `--footprint-dir`
options as `search`:
- `.copperpilot/skills/kicad_lib_search/main.py symbol-info --symbol-id Lib:Name` (or `--library-path <.kicad_sym> --symbol Name`):
  properties (reference, value, footprint, datasheet, description,
  keywords, fp_filters), `extends_parent` already resolved, units, body
  styles, bbox, and every pin with number, name, type, style, unit, x, y,
  orientation, side, length, hidden, plus `pins_by_name`. Narrow big parts
  with `--unit N` or `--pin NAME_OR_NUMBER`.
  Pin x,y is the wire point in library coordinates (Y up): for a symbol
  placed at (X, Y) unrotated, the wire point on the sheet is (X + x, Y - y).
- `.copperpilot/skills/kicad_lib_search/main.py footprint-info --footprint-id Lib:Name` (or `--library-path <.pretty or .kicad_mod> [--footprint Name]`):
  pads (number, type, shape, x, y, rotation, size, drill, layers),
  courtyard and fab/silk extents, pad bbox, attributes (smd /
  through_hole), 3D model paths, description and tags. PCB Y is down.
- Failures print `success: false` with `close_matches`; exit code is 1.

Includes project-local `*.kicad_sym`, `*.pretty`, and `libs/3dmodels` under the project directory.


## Examples
- `python .copperpilot/skills/kicad_lib_search/main.py search --platform linux --project-dir . --kind symbol --query "7555" --max-results 10`
- `python .copperpilot/skills/kicad_lib_search/main.py search --platform linux --project-dir . --kind footprint --query "LED_D3.0mm" --max-results 10`
- `python .copperpilot/skills/kicad_lib_search/main.py search --platform linux --project-dir . --kind model --query "BatteryHolder|CAS-120A" --max-results 10`
- `python .copperpilot/skills/kicad_lib_search/main.py search --platform linux --project-dir . --kind all --query "Resistor_THT 0805" --max-results 20`
- `python .copperpilot/skills/kicad_lib_search/main.py symbol-info --platform linux --symbol-id "Regulator_Linear:AMS1117-3.3"`
- `python .copperpilot/skills/kicad_lib_search/main.py footprint-info --platform linux --footprint-id "Package_TO_SOT_SMD:SOT-223-3_TabPin2"`
