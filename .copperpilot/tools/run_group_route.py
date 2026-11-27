#!/usr/bin/env python3
"""Run surgical FreeRouting net-group pass while preserving locked prior copper."""

import json
import subprocess
import sys
from pathlib import Path

import pcbnew


def main():
    group_name = sys.argv[1]
    cand_dir = Path(sys.argv[2]).resolve()
    pcb_name = sys.argv[3]
    new_nets = [n.strip() for n in sys.argv[4].split(",") if n.strip()]
    max_passes = sys.argv[5] if len(sys.argv) > 5 else "30"
    timeout_sec = sys.argv[6] if len(sys.argv) > 6 else "240"

    pcb_path = cand_dir / pcb_name
    root = Path("/home/sam/Open_drive")

    # 1. Refill zones so all 82 F.Cu/In1.Cu/In2.Cu/B.Cu pours export as DSN planes
    subprocess.run(
        ["/usr/bin/kicad-cli", "pcb", "drc", "--refill-zones", "--save-board", str(pcb_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    rpt = root / f"{pcb_path.stem}-drc.rpt"
    if rpt.exists():
        rpt.unlink()

    # 2. Lock all existing tracks and vias so Specctra DSN exports them as (type fix)
    board = pcbnew.LoadBoard(str(pcb_path))
    prior_wire_nets = set()
    for trk in board.GetTracks():
        trk.SetLocked(True)
        if trk.GetClass() != "PCB_VIA":
            prior_wire_nets.add(trk.GetNetname())
    pcbnew.SaveBoard(str(pcb_path), board)

    combined_nets = sorted(prior_wire_nets.union(new_nets))
    out_json = root / ".copperpilot" / "tmp" / f"route_{group_name}.json"

    cmd = [
        "/usr/bin/python3",
        str(root / ".copperpilot/skills/kicad_autorouter/main.py"),
        "route",
        "--platform", "linux",
        "--project-dir", str(cand_dir),
        "--pcb", pcb_name,
        "--jar-path", str(root / ".copperpilot/skills/kicad_autorouter/cache/freerouting-2.2.4.jar"),
        "--disable-analytics",
        "--nets", ",".join(combined_nets),
        "--max-passes", str(max_passes),
        "--timeout-sec", str(timeout_sec),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out_json.write_text(res.stdout)

    d, _ = json.JSONDecoder().raw_decode(res.stdout.lstrip())
    ng = d.get("net_group") or {}
    ntc = ng.get("non_target_copper") or {}

    # 3. Refill zones after SES import
    if d.get("status") == "routed" and ng.get("decision") == "kept":
        subprocess.run(
            ["/usr/bin/kicad-cli", "pcb", "drc", "--refill-zones", "--save-board", str(pcb_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if rpt.exists():
            rpt.unlink()

    summary = {
        "group": group_name,
        "status": d.get("status"),
        "error": d.get("error"),
        "segments_before": d.get("segment_count_before"),
        "segments_after": d.get("segment_count_after"),
        "telemetry": d.get("freerouting_telemetry"),
        "decision": ng.get("decision"),
        "reasons": ng.get("reasons"),
        "non_target_copper_status": ntc.get("status"),
        "drc_delta": ng.get("drc_delta"),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
