#!/usr/bin/env python3
"""Surgical net-group FreeRouting wrapper for staged bldc_motor_cntroller_v9_8."""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time

CAND_DIR = pathlib.Path(".copperpilot/tmp/staging/v9_8_finish/candidate/bldc_motor_cntroller_v9_8")
PCB = CAND_DIR / "bldc_motor_cntroller_v9_8.kicad_pcb"
PRO = CAND_DIR / "bldc_motor_cntroller_v9_8.kicad_pro"
JAVA = "/home/sam/.config/CopperPilot/runtimes/java/25.0.4.1+1/jdk-25.0.4.1+1-jre/bin/java"
ROUTER = ".copperpilot/skills/kicad_autorouter/main.py"
SHIELD = ".copperpilot/tools/via_shield.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--nets", required=True, help="Comma-separated exact KiCad net names")
    ap.add_argument("--max-passes", type=int, default=12)
    ap.add_argument("--timeout-sec", type=int, default=120)
    ap.add_argument("--no-in2", action="store_true", help="Temporarily set In2.Cu to power so this group routes F.Cu/B.Cu only")
    ap.add_argument("--extra-novia-box", action="append", default=[])
    ap.add_argument("--extra-fcu-box", action="append", default=[])
    ap.add_argument("--extra-bcu-box", action="append", default=[])
    ap.add_argument("--refill", action="store_true")
    args = ap.parse_args()

    if "__CP_ISO_" in PCB.read_text():
        print("ABORT: PCB already contains __CP_ISO_ before shield!")
        return 1

    t0 = time.time()
    bak_pcb = pathlib.Path(f".copperpilot/tmp/v9_8_pre_{args.tag}.kicad_pcb")
    bak_pro = pathlib.Path(f".copperpilot/tmp/v9_8_pre_{args.tag}.kicad_pro")
    shutil.copy2(PCB, bak_pcb)
    shutil.copy2(PRO, bak_pro)

    st = pathlib.Path(f".copperpilot/tmp/v9_8_st_{args.tag}.json")
    if st.exists():
        st.unlink()

    if args.no_in2:
        subprocess.run(
            ["/usr/bin/python3", "-c", f"import pcbnew; b=pcbnew.LoadBoard({str(PCB)!r}); b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER); b.Save({str(PCB)!r})"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    cmd_sh = [
        "/usr/bin/python3", SHIELD, "shield",
        "--pcb", str(PCB), "--pro", str(PRO),
        "--keep-nets", args.nets,
        "--state", str(st),
        "--temp-novia-box", "105.00,39.00,115.00,49.00",
    ]
    for b in args.extra_novia_box:
        cmd_sh += ["--temp-novia-box", b]
    for b in args.extra_fcu_box:
        cmd_sh += ["--temp-fcu-box", b]
    for b in args.extra_bcu_box:
        cmd_sh += ["--temp-bcu-box", b]

    r_sh = subprocess.run(cmd_sh, capture_output=True, text=True)
    if r_sh.returncode != 0:
        print("SHIELD FAILED:", r_sh.stdout, r_sh.stderr)
        shutil.copy2(bak_pcb, PCB)
        shutil.copy2(bak_pro, PRO)
        return 1

    r_ch = subprocess.run(
        ["/usr/bin/python3", ".copperpilot/tools/chain_pcb_segments.py", str(PCB), "--t-tag"],
        capture_output=True, text=True,
    )
    if r_ch.returncode != 0:
        print("CHAIN FAILED:", r_ch.stdout, r_ch.stderr)
        shutil.copy2(bak_pcb, PCB)
        shutil.copy2(bak_pro, PRO)
        return 1

    cmd_rt = [
        "/usr/bin/python3", ROUTER, "route",
        "--platform", "linux",
        "--project-dir", str(CAND_DIR),
        "--pcb", PCB.name,
        "--java-bin", JAVA,
        "--nets", args.nets,
        "--max-passes", str(args.max_passes),
        "--timeout-sec", str(args.timeout_sec),
        "--disable-analytics",
        "--extra-freerouting-arg=--router.optimizer.enabled=false",
    ]
    r_rt = subprocess.run(cmd_rt, capture_output=True, text=True)

    # Always restore shield state
    r_un = subprocess.run(
        ["/usr/bin/python3", SHIELD, "restore", "--pcb", str(PCB), "--pro", str(PRO), "--state", str(st)],
        capture_output=True, text=True,
    )
    subprocess.run(
        ["/usr/bin/python3", ".copperpilot/tools/chain_pcb_segments.py", str(PCB)],
        capture_output=True, text=True,
    )
    if args.no_in2:
        subprocess.run(
            ["/usr/bin/python3", "-c", f"import pcbnew; b=pcbnew.LoadBoard({str(PCB)!r}); b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED); b.Save({str(PCB)!r})"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    # Parse JSON from router stdout
    out = r_rt.stdout
    try:
        j_start = out.index("{")
        j_end = out.rindex("}") + 1
        payload = json.loads(out[j_start:j_end])
    except Exception:
        payload = {"status": "parse_error", "stdout_tail": out[-1000:], "stderr_tail": r_rt.stderr[-500:]}

    status = payload.get("status")
    ng = payload.get("net_group", {})
    telem = payload.get("freerouting_telemetry", {})
    print(json.dumps({
        "tag": args.tag,
        "elapsed_sec": round(time.time() - t0, 1),
        "status": status,
        "decision": ng.get("decision"),
        "still_unconnected": ng.get("drc_delta", {}).get("still_unconnected_nets"),
        "new_errors": ng.get("drc_delta", {}).get("new_errors"),
        "telemetry": {
            "started_unrouted": telem.get("started_unrouted"),
            "final_unrouted": telem.get("final_unrouted"),
            "total_passes": telem.get("total_passes"),
        },
        "error": payload.get("error"),
        "restore_rc": r_un.returncode,
    }, indent=2))

    if status != "routed" or r_un.returncode != 0 or "__CP_ISO_" in PCB.read_text():
        shutil.copy2(bak_pcb, PCB)
        shutil.copy2(bak_pro, PRO)
        return 1

    if args.refill:
        subprocess.run(
            ["/usr/bin/kicad-cli", "pcb", "drc", "--refill-zones", "--save-board", str(PCB)],
            capture_output=True, text=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
