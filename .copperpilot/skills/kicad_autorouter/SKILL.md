---
required_inputs: [platform, pcb_path, optional project_dir and artifact overrides]
artifact_outputs: [structured JSON route result with DSN/SES/JAR paths, segment counts and net_group feedback]
---

# Skill: kicad_autorouter

## Objective
Run the external FreeRouting workflow on the user's machine:
export Specctra DSN with KiCad `pcbnew`, run `java -jar freerouting.jar`,
import the resulting SES back into the PCB, and report structured results.

**Headless by default:** route runs with `-Djava.awt.headless=true` and
`--gui.enabled=false` so FreeRouting does not launch a GUI. Use
`--no-headless` only when explicitly debugging locally with the
FreeRouting GUI.

## Platform defaults (linux)
- FreeRouting version: `2.2.4`
- FreeRouting URL: `https://github.com/freerouting/freerouting/releases/download/v2.2.4/freerouting-2.2.4.jar`
- Skill cache dir: `.copperpilot/skills/kicad_autorouter/cache`
- pcbnew site paths: `/usr/lib/kicad/lib/python3/dist-packages, /usr/lib/kicad/lib/python3/site-packages, /usr/share/kicad/scripting/plugins`
- Java binary: `java`

## Prerequisites
- KiCad installed with the `pcbnew` Python module available.
- Java 25+ reachable as `java`. CopperPilot onboarding installs this
  runtime; do not download another JDK when `java -version` is already 25+.
- Do **not** `pip install pcbnew`; use KiCad's bundled Python when needed.
- KiCad 10 removed `kicad-cli pcb export specctradsn`. This skill exports DSN
  with `pcbnew.ExportSpecctraDSN` and imports SES with
  `pcbnew.ImportSpecctraSES`.
- If JAR download fails (common when KiCad bundled Python has SSL issues),
  the skill automatically retries with system `curl`/`wget`, or you can
  pre-cache the JAR manually and pass `--jar-path` to a local copy.

## Path resolution
Relative paths such as `--pcb board.kicad_pcb` resolve against `--project-dir`,
not the shell current working directory. Absolute paths are preserved as-is.

## Clean JSON output
The CLI captures native `pcbnew`/wxWidgets debug output and prints only JSON to
stdout. Inspect `native_stdout_tail` / `native_stderr_tail` in the result when
diagnosing local environment noise.

## Post-route convenience flags
Optional local follow-up actions (disabled by default):
- `--run-drc`: run `kicad-cli pcb drc` after SES import and include
  `drc_summary.violations` and `drc_summary.unconnected_items` in the
  JSON result. These lists are distinct: empty `unconnected_items` is
  connectivity only, not DRC-clean.
- `--refill-zones`: run `kicad-cli pcb drc --refill-zones --save-board` after
  SES import.
- `--kicad-cli-path`: override auto-discovery when needed.
A net-group route (`--nets`, `--net-classes`, `--ignore-net-class`)
always runs DRC before and after (zones refilled in memory, board not
saved) to fill `net_group.drc_delta`; its after-DRC is `drc_summary`.

## Net-group routing (surgical)
FreeRouting writes all copper. Never hand-place tracks or vias.
`--nets NET1,NET2` (and/or `--net-classes CLASS`) routes only that net
group; every other net keeps its copper exactly and is not routed. The
skill rewrites the exported DSN so FreeRouting cannot touch other nets
(FreeRouting 2.2.4 ignores `-inc` when headless, so the skill does not
rely on it), then verifies after import:
- `net_group.non_target_copper.status` must be `unchanged`; otherwise
  the board is reverted and `status` is `reverted`.
- `net_group.drc_delta`: `new_errors`, `new_warnings`,
  `target_unconnected_before/after`, `still_unconnected_nets`,
  `connected_nets` (kicad-cli DRC with zones refilled in memory, before
  vs after).
- `net_group.decision`: `kept`, or `reverted` when the route changed
  other copper, added DRC errors, or left more target connections open.
  A reverted route leaves the board exactly as it was (exit code 1).
Existing copper on target nets stays fixed too; to re-route a net from
scratch, `unroute_pcb_net` it first.

Workflow:
1. Write a short routing plan first: net groups in order. High-speed
   nets and differential pairs first, then power, then the rest.
2. Route one group at a time with `--nets` and read `net_group` after
   each group before routing the next.
3. Fix a bad or missing connection with `unroute_pcb_net`, then re-route
   that net with `--nets`. Never hand-place tracks.
4. FreeRouting cannot length-match or route coupled differential pairs.
   Route those nets first (as one group), then run
   `.copperpilot/skills/kicad_autorouter/main.py lengths --nets P,N --target-skew-mm X` and report the
   skew against the target.
5. Budget: 3 attempts per net group, and at most 12 route runs per
   board. A reverted route counts as an attempt.
6. On exhaustion, stop and report infeasible: tell the user the cause
   (which nets, which obstacle, telemetry and DRC numbers) and the
   options: more layers, larger vias or a larger board, a placement
   change, or relaxed rules only with consent via `ask_user_question`.

`--ignore-net-class CLASS` (repeatable or comma separated) excludes
classes from a route; their copper stays fixed the same way.

## FreeRouting tuning flags
FreeRouting 2.2.4 only understands `-de -di -do -dr -drc -mp -mt -oit
-us -hr -is -l -dl -da -host -help -inc -dct -ll` plus `--key=value`
settings. Allowed engine knobs (iterate freely from
`freerouting_telemetry` / `next_actions`):
- `--headless` / `--no-headless` (default: headless; GUI debug only)
- `--timeout-sec` — Java **subprocess** wall clock (default 600), not `-t`
- `--max-passes N` (`-mp`, upper limit of auto-router passes;
  `--autorouter-passes` is an alias)
- `--threads N` (`-mt`, optimizer thread pool)
- `--optimization-threshold RATIO` (`-oit`)
- `--board-update-strategy greedy|global|hybrid` (`-us`, optimizer)
- `--hybrid-ratio RATIO` (`-hr`)
- `--item-selection-strategy sequential|random|prioritized` (`-is`)
- `--log-level LEVEL` (`-ll`), `--disable-analytics` (`-da`),
  `--disable-logging` (`-dl`), `--dialog-timeout SEC` (`-dct`)
- `--extra-freerouting-arg` after the headless/`-de`/`-do` skeleton
  (`-dr` / `--rules-file` extras are dropped; an extra `-inc` is merged
  into the single `-inc` list)
`--fanout`, `--post-route-passes`, `--save-intermediate`, `--trace` and
`--experimental` are accepted for old commands but ignored with a
warning: 2.2.4 has no such flags.

Protected physical constraints (exhausted engine retries + RCA + DFM
numbers + one `ask_user_question` yes; never silent):
- `--rules-file PATH` (`-dr`)
- KiCad rules (`set_design_settings`, `set_kicad_project_design_rules`,
  `.kicad_dru`), Edge.Cuts, stackup, via/track-as-router

Inspect `commands[0].command`, `commands[0].freerouting_options`, and
`freerouting_telemetry` in the JSON output.

## Telemetry vs Java exit 0
INFO stdout is enough; `-ll ALL` / `freerouting.log` is optional deeper
debug. Read the log if present; do not block the route on it.

`freerouting_telemetry` fields:
- `started_unrouted`, `pass_history` (pass, time_sec, score, unrouted,
  violations)
- omitted `(N unrouted)` on a pass means that pass has 0 unrouted
- `total_passes`, `final_score`, `cpu_seconds`, `peak_heap_mb`
- `final_unrouted`, `final_violations`, `board_unchanged`
- `violations` is FreeRouting's own count (it includes overlaps already
  on the board); judge new problems by `net_group.drc_delta`

Java exit 0 and `status: routed` mean SES imported (or the process
finished), **not** 100% connected. `segment_count_*` is not connectivity.
Always inspect `net_group` and telemetry, then `run_drc` and `list_nets`.

## When to tune passes
Start with the default route for the group. Pass starvation (score
rising, still unrouted): more `--max-passes` / `--timeout-sec`. Score
oscillation: `--item-selection-strategy random`. Board unchanged with
nets unrouted: earlier copper blocks the group; `unroute_pcb_net` the
blocker and route the stuck nets first, or change the group order.
Score ~0: **stop mutating**; RCA; ask. Do not enlarge Edge.Cuts or relax
clearance from telemetry alone.

## Skill install
If `SKILL.md` is stale (missing `--nets` / `net_group`), re-run
`install_kicad_autorouter(..., force=true)`.

## Invariants
Headless by default. JAR auto-download/cache (urllib → curl → wget).
`--timeout-sec` bounds the Java subprocess; do not leave GUI or unbounded
Java running. Never invent track geometry. Never use `write`/`edit`/`bash`
to inject `(segment …)` or `(via …)` copper. On hard FreeRouting failure
(nonzero Java exit, missing/empty SES, timeout with no import), do not
fall back to manual geometry — stop and report infeasible with an RCA.

## Steps
1. Install this skill once with `install_kicad_autorouter`.
2. Run `.copperpilot/skills/kicad_autorouter/main.py diagnose --platform linux` to verify Java and
   pcbnew.
3. If diagnose returns `recommended_route_command`, use that Python and
   script path (common on macOS when system Python cannot import
   pcbnew).
4. Write the routing plan (net groups in order), then for each group run
   `.copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir .
   --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --nets <group>`.
5. Read `status`, `net_group`, `freerouting_telemetry` and
   `next_actions`. Segment counts are not connectivity.
6. After the last group, refill zones (`fill_pcb_zones` or
   `kicad-cli pcb drc --refill-zones`) and run `run_drc`; inspect both
   `violations` and `unconnected_items`.
7. Measure differential pairs / matched nets with `lengths` and report
   the skew.

## Examples
- `python .copperpilot/skills/kicad_autorouter/main.py diagnose --platform linux --java-bin java`
- `python .copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir . --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --nets "USB_D+,USB_D-" --run-drc`
- `python .copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir . --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --net-classes Power --max-passes 20`
- `python .copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir . --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --nets SPI_CLK --max-passes 50 --timeout-sec 900`
- `python .copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir . --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --ignore-net-class Power,HighSpeed`
- `python .copperpilot/skills/kicad_autorouter/main.py lengths --platform linux --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --nets "USB_D+,USB_D-" --target-skew-mm 0.15`
- `python .copperpilot/skills/kicad_autorouter/main.py route --platform linux --project-dir . --pcb .copperpilot/tmp/staging/v9_5_u6_rework/candidate/bldc_motor_cntroller_v9_5/bldc_motor_cntroller_v9_5.kicad_pcb --freerouting-version 2.2.4 --jar-path .copperpilot/skills/kicad_autorouter/cache/freerouting-2.2.4.jar`
