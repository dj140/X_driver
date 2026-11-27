#!/usr/bin/env python3
"""Surgical net-group FreeRouting wrapper for staged bldc_motor_cntroller_v9_14."""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import time

CAND_DIR = pathlib.Path(".copperpilot/tmp/staging/v9_14_coroute/candidate/bldc_motor_cntroller_v9_14")
PCB = CAND_DIR / "bldc_motor_cntroller_v9_14.kicad_pcb"
PRO = CAND_DIR / "bldc_motor_cntroller_v9_14.kicad_pro"
JAVA = "/home/sam/.config/CopperPilot/runtimes/java/25.0.4.1+1/jdk-25.0.4.1+1-jre/bin/java"
ROUTER = ".copperpilot/skills/kicad_autorouter/main.py"
SHIELD = ".copperpilot/tools/via_shield.py"


def count_layers(pcb_path: pathlib.Path) -> dict:
    r = subprocess.run(
        [
            "/usr/bin/python3", "-c",
            f"import pcbnew, json; from collections import Counter; "
            f"b=pcbnew.LoadBoard({str(pcb_path)!r}); "
            f"c=Counter(b.GetLayerName(t.GetLayer()) for t in b.GetTracks() if t.GetClass()=='PCB_TRACK'); "
            f"v=sum(1 for t in b.GetTracks() if t.GetClass()=='PCB_VIA'); "
            f"print(json.dumps({{'tracks': dict(c), 'vias': v}}))",
        ],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    global CAND_DIR, PCB, PRO
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand-dir", default=str(CAND_DIR), help="Staged candidate directory")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--nets", required=True, help="Comma-separated exact KiCad net names")
    ap.add_argument("--max-passes", type=int, default=15)
    ap.add_argument("--timeout-sec", type=int, default=120)
    ap.add_argument("--no-in2", action="store_true", help="Temporarily set In2.Cu to power so this group routes F.Cu/B.Cu only")
    ap.add_argument("--extra-novia-box", action="append", default=[])
    ap.add_argument("--extra-fcu-box", action="append", default=[])
    ap.add_argument("--extra-bcu-box", action="append", default=[])
    args = ap.parse_args()

    cand_dir = pathlib.Path(args.cand_dir)
    pcb = cand_dir / "bldc_motor_cntroller_v9_14.kicad_pcb"
    pro = cand_dir / "bldc_motor_cntroller_v9_14.kicad_pro"
    CAND_DIR, PCB, PRO = cand_dir, pcb, pro

    if "__CP_ISO_" in PCB.read_text():
        print("ABORT: PCB already contains __CP_ISO_ before shield!")
        return 1

    t0 = time.time()
    before_counts = count_layers(PCB)
    bak_pcb = pathlib.Path(f".copperpilot/tmp/v9_14_pre_{args.tag}.kicad_pcb")
    bak_pro = pathlib.Path(f".copperpilot/tmp/v9_14_pre_{args.tag}.kicad_pro")
    shutil.copy2(PCB, bak_pcb)
    shutil.copy2(PRO, bak_pro)

    st = pathlib.Path(f".copperpilot/tmp/v9_14_st_{args.tag}.json")
    if st.exists():
        st.unlink()

    if args.no_in2:
        subprocess.run(
            ["/usr/bin/python3", "-c",
             f"import pcbnew\n"
             f"b=pcbnew.LoadBoard({str(PCB)!r})\n"
             f"b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)\n"
             f"for z in list(b.Zones()):\n"
             f"    if z.GetIsRuleArea() and z.GetZoneName() == 'In2_VDC_Track_Keepout':\n"
             f"        b.Remove(z)\n"
             f"b.Save({str(PCB)!r})"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    cmd_sh = [
        "/usr/bin/python3", SHIELD, "shield",
        "--pcb", str(PCB), "--pro", str(PRO),
        "--keep-nets", args.nets,
        "--state", str(st),
        "--temp-novia-box", "105.00,39.00,115.00,49.00",
        "--temp-novia-box", "0.00,85.60,220.00,101.40",
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
    subprocess.run(
        ["/usr/bin/python3", SHIELD, "restore", "--pcb", str(PCB), "--pro", str(PRO), "--state", str(st)],
        capture_output=True, text=True,
    )
    subprocess.run(
        ["/usr/bin/python3", ".copperpilot/tools/chain_pcb_segments.py", str(PCB)],
        capture_output=True, text=True,
    )
    if args.no_in2:
        subprocess.run(
            ["/usr/bin/python3", "-c",
             f"import pcbnew\n"
             f"b=pcbnew.LoadBoard({str(PCB)!r})\n"
             f"b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)\n"
             f"has_k = any(z.GetIsRuleArea() and z.GetZoneName() == 'In2_VDC_Track_Keepout' for z in b.Zones())\n"
             f"if not has_k:\n"
             f"    ko = pcbnew.ZONE(b)\n"
             f"    ko.SetIsRuleArea(True)\n"
             f"    ko.SetZoneName('In2_VDC_Track_Keepout')\n"
             f"    ko.SetLayer(pcbnew.In2_Cu)\n"
             f"    ko.SetDoNotAllowTracks(True)\n"
             f"    ko.SetDoNotAllowVias(False)\n"
             f"    ko.SetDoNotAllowPads(False)\n"
             f"    ko.SetDoNotAllowFootprints(False)\n"
             f"    ol = ko.Outline()\n"
             f"    ol.NewOutline()\n"
             f"    for x, y in [(0.50, 62.00), (195.00, 62.00), (195.00, 55.00), (219.50, 55.00), (219.50, 129.50), (0.50, 129.50)]:\n"
             f"        ol.Append(int(x*1e6), int(y*1e6))\n"
             f"    b.Add(ko)\n"
             f"b.Save({str(PCB)!r})"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    out = r_rt.stdout
    try:
        j_start = out.index("{")
        j_end = out.rindex("}") + 1
        payload = json.loads(out[j_start:j_end])
    except Exception:
        print("RAW STDOUT:", out[-1500:])
        print("RAW STDERR:", r_rt.stderr[-1000:])
        shutil.copy2(bak_pcb, PCB)
        shutil.copy2(bak_pro, PRO)
        return 1

    ng = payload.get("net_group") or {}
    drc_delta = ng.get("drc_delta") or {}
    telem = payload.get("freerouting_telemetry") or {}
    decision = ng.get("decision")
    if decision != "kept":
        shutil.copy2(bak_pcb, PCB)
        shutil.copy2(bak_pro, PRO)

    after_counts = count_layers(PCB)
    summary = {
        "tag": args.tag,
        "elapsed_s": round(time.time() - t0, 1),
        "status": payload.get("status"),
        "error": payload.get("error") or payload.get("message"),
        "decision": decision,
        "reason": ng.get("reason"),
        "before_target_unc": drc_delta.get("before_target_unconnected"),
        "after_target_unc": drc_delta.get("after_target_unconnected"),
        "still_unconnected_nets": drc_delta.get("still_unconnected_nets"),
        "new_errors": drc_delta.get("new_errors"),
        "new_error_samples": (drc_delta.get("new_error_samples") or [])[:5],
        "passes": telem.get("passes_completed") or telem.get("total_passes"),
        "stdout_tail": (payload.get("commands") or [{}])[-1].get("stdout_tail", "")[-400:],
        "before_counts": before_counts,
        "after_counts": after_counts,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
