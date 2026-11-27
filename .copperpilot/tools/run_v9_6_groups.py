#!/usr/bin/env python3
"""Staged ordered net-group runner for bldc_motor_cntroller_v9_6 using headless FreeRouting."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import time

CAND_DIR = pathlib.Path(".copperpilot/tmp/staging/v9_6_route/candidate/bldc_motor_cntroller_v9_6")
PCB = CAND_DIR / "bldc_motor_cntroller_v9_6.kicad_pcb"
PRO = CAND_DIR / "bldc_motor_cntroller_v9_6.kicad_pro"


def run_group(
    tag: str,
    nets: list[str],
    max_passes: int = 8,
    timeout_sec: int = 95,
    local_via_pairs: str | None = None,
    extra_fcu_boxes: list[str] | None = None,
    extra_novia_boxes: list[str] | None = None,
    target_pads_box: str | None = None,
) -> bool:
    t0 = time.time()
    bak = pathlib.Path(f".copperpilot/tmp/v9_6_pre_{tag}.kicad_pcb")
    shutil.copy2(PCB, bak)
    bak_pro = pathlib.Path(f".copperpilot/tmp/v9_6_pre_{tag}.kicad_pro")
    shutil.copy2(PRO, bak_pro)

    st = pathlib.Path(f".copperpilot/tmp/st_{tag}.json")
    po = pathlib.Path(f".copperpilot/tmp/po_{tag}.txt")
    if po.exists():
        po.unlink()

    keep_str = ",".join(nets)
    cmd_sh = [
        "/usr/bin/python3", ".copperpilot/tools/via_shield.py", "shield",
        "--pcb", str(PCB), "--pro", str(PRO),
        "--keep-nets", keep_str,
        "--temp-novia-box", "105.00,39.00,115.00,49.00",
        "--temp-novia-box", "103.80,37.30,116.20,50.70",
        "--temp-novia-box", "103.30,39.60,116.70,48.40",
        "--temp-novia-box", "166.00,59.00,180.00,62.30",
        "--temp-novia-box", "48.00,59.00,62.00,62.30",
        "--temp-novia-box", "95.20,21.20,97.50,24.80",
        "--temp-fcu-box", "105.60,61.08,110.05,72.05",
        "--temp-fcu-box", "110.05,59.95,123.70,72.05",
        "--temp-fcu-box", "97.65,60.25,98.75,61.35",
        "--temp-fcu-box", "104.50,65.95,105.75,66.95",
        "--temp-bcu-box", "105.35,61.08,123.55,72.05",
        "--temp-fcu-box", "112.00,72.05,112.60,75.30",
        "--temp-bcu-box", "112.00,72.05,112.60,75.30",
        "--temp-fcu-box", "119.05,71.25,123.35,75.15",
        "--temp-bcu-box", "119.05,71.25,123.35,75.15",
        "--temp-fcu-box", "123.55,63.50,124.10,64.10",
        "--temp-bcu-box", "123.55,63.50,124.10,64.10",
        "--temp-fcu-box", "110.00,80.20,124.50,88.80",
        "--temp-bcu-box", "110.00,80.20,124.50,88.80",
        "--temp-fcu-box", "10.50,75.50,35.85,88.75",
        "--temp-fcu-box", "41.90,75.50,65.85,88.75",
        "--temp-fcu-box", "67.30,75.50,95.45,88.75",
        "--temp-fcu-box", "128.50,75.50,153.85,88.75",
        "--temp-fcu-box", "159.90,75.50,183.85,88.75",
        "--temp-fcu-box", "185.30,75.50,213.55,88.75",
        "--temp-fcu-box", "98.45,69.00,100.10,70.00",
        "--temp-fcu-box", "109.50,67.20,111.30,70.50",
        "--temp-fcu-box", "78.00,53.05,78.30,53.48",
        "--temp-fcu-box", "83.00,51.95,83.30,52.25",
        "--temp-fcu-box", "90.00,51.48,90.30,51.90",
        "--temp-fcu-box", "103.85,53.90,104.85,54.50",
        "--temp-fcu-box", "86.00,49.95,89.00,50.75",
        "--temp-fcu-box", "51.05,60.50,62.00,62.30",
        "--temp-fcu-box", "169.05,60.50,180.00,62.30",
        "--temp-fcu-box", "123.50,60.80,140.00,64.80",
        "--temp-bcu-box", "45.00,58.85,63.00,69.00",
        "--temp-bcu-box", "163.00,58.85,181.00,69.00",
        "--temp-bcu-box", "103.22,53.25,104.15,54.20",
        "--temp-bcu-box", "109.80,49.40,110.20,49.90",
        "--temp-bcu-box", "97.80,49.15,98.20,49.70",
        "--temp-bcu-box", "107.65,28.35,109.10,32.20",
        "--temp-bcu-box", "96.25,23.80,97.10,24.65",
        "--temp-bcu-box", "99.85,38.10,101.00,38.90",
        "--temp-bcu-box", "93.20,28.50,94.05,29.40",
        "--temp-bcu-box", "125.80,23.80,126.65,24.65",
        "--temp-bcu-box", "101.55,52.05,102.55,53.65",
        "--temp-bcu-box", "104.80,54.65,105.30,56.20",
        "--temp-bcu-box", "59.10,26.65,60.10,27.45",
        "--temp-bcu-box", "57.25,32.55,58.15,33.45",
        "--temp-bcu-box", "93.50,51.20,94.00,51.70",
        "--pairs-out", str(po), "--state", str(st),
    ]
    if target_pads_box:
        cmd_sh.extend(["--target-pads-box", target_pads_box])
    if local_via_pairs:
        cmd_sh.extend(["--local-via-pairs", local_via_pairs])
    for fb in extra_fcu_boxes or []:
        cmd_sh.extend(["--temp-fcu-box", fb])
    for nvb in extra_novia_boxes or []:
        cmd_sh.extend(["--temp-novia-box", nvb])

    try:
        subprocess.run(cmd_sh, check=True)
        subprocess.run([
            "/usr/bin/python3", ".copperpilot/tools/chain_pcb_segments.py", str(PCB),
            "--t-tag",
        ], check=True)

        extra = po.read_text().strip() if po.exists() else ""
        target_list = [n for n in nets if n != "GND"]
        nets_arg = ",".join(target_list)
        if extra:
            nets_arg = (nets_arg + "," + extra) if nets_arg else extra

        r_fr = subprocess.run([
            "/usr/bin/python3", ".copperpilot/skills/kicad_autorouter/main.py", "route",
            "--platform", "linux",
            "--project-dir", str(CAND_DIR),
            "--pcb", "bldc_motor_cntroller_v9_6.kicad_pcb",
            "--nets", nets_arg,
            "--max-passes", str(max_passes),
            "--timeout-sec", str(timeout_sec),
            "--extra-freerouting-arg=--router.optimizer.enabled=false",
        ], capture_output=True, text=True)
    finally:
        subprocess.run([
            "/usr/bin/python3", ".copperpilot/tools/via_shield.py", "restore",
            "--pcb", str(PCB), "--pro", str(PRO), "--state", str(st),
        ], check=True)
        subprocess.run(["/usr/bin/python3", ".copperpilot/tools/chain_pcb_segments.py", str(PCB)], check=True)

    pathlib.Path(f".copperpilot/tmp/res_{tag}.json").write_text(r_fr.stdout)
    j = json.loads(r_fr.stdout)
    ng = j.get("net_group") or {}
    dd = ng.get("drc_delta") or {}
    tel = j.get("freerouting_telemetry") or {}
    still = dd.get("still_unconnected_nets")
    status = j.get("status")
    dec = ng.get("decision")
    new_err = dd.get("new_errors")
    print(
        f"[{tag}] {time.time()-t0:.1f}s | status={status} | dec={dec} "
        f"| passes={tel.get('total_passes')} unr={tel.get('final_unrouted')} "
        f"| still_unconn={still} | new_err={new_err}",
        flush=True,
    )
    if target_pads_box or local_via_pairs:
        ok = (
            status == "routed"
            and dec == "kept"
            and new_err == 0
            and tel.get("final_unrouted") == 0
        )
    else:
        import pcbnew as _pcbnew
        _b = _pcbnew.LoadBoard(str(PCB))
        _conn = _b.GetConnectivity()
        _conn.Build(_b)
        pcb_open: list[str] = []
        for _nn in nets:
            if _nn in ("GND", "+3.3V"):
                continue
            _pads = [_pd for _fp in _b.GetFootprints() for _pd in _fp.Pads() if _pd.GetNetname() == _nn]
            if len(_pads) <= 1:
                continue
            _seen = {_pads[0].m_Uuid.AsString()}
            _q = [_pads[0]]
            while _q:
                _c = _q.pop()
                for _it in _conn.GetConnectedItems(_c):
                    _u = _it.m_Uuid.AsString()
                    if _u not in _seen:
                        _seen.add(_u)
                        _q.append(_it)
            if any(_p.m_Uuid.AsString() not in _seen for _p in _pads):
                pcb_open.append(_nn)
        if pcb_open:
            print(f"  pcb_open={pcb_open}", flush=True)
        ok = (
            status == "routed"
            and dec == "kept"
            and still == []
            and new_err == 0
            and pcb_open == []
        )
    if ok:
        shutil.copy2(PCB, f".copperpilot/tmp/v9_6_ckpt_{tag}.kicad_pcb")
    else:
        for c in j.get("commands", []):
            if c.get("stderr_tail"):
                print("  stderr_tail:", c["stderr_tail"][-350:], flush=True)
            if c.get("stdout_tail"):
                print("  stdout_tail:", c["stdout_tail"][-350:], flush=True)
        shutil.copy2(bak, PCB)
        shutil.copy2(bak_pro, PRO)
        print(f"  -> Restored pre-{tag} baseline because ok={ok}", flush=True)
    return ok


GROUPS: dict[str, tuple[list[str], int, int, str | None, str | None]] = {
    "s_auxh": ([
        "/Microcontroller Interface/AUX_H",
    ], 10, 95, None, None, ["111.70,50.70,112.30,56.80"], ["111.35,50.70,112.70,57.20"]),
    "s_auxl": ([
        "/Microcontroller Interface/AUX_L",
    ], 10, 95, None, None, [], []),
    "s_gpio6_s": ([
        "/I{slash}O Interface/GPIO_6",
    ], 10, 105, None, None, ["118.15,20.40,120.85,23.60", "107.70,50.70,110.30,52.00"], []),
    "s_m0temp_g": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 10, 95, None, None, ["107.70,50.70,109.80,52.00"], []),
    "s_gpio5_s": ([
        "/I{slash}O Interface/GPIO_5",
    ], 10, 105, None, None, ["119.15,20.40,120.85,23.60", "107.70,50.70,109.30,52.00"], []),
    "s_m1al_g": ([
        "/Microcontroller Interface/M1_AL",
    ], 10, 95, None, None, ["107.70,50.70,108.80,52.00"], []),
    "s_vbuss_g": ([
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None, None, ["107.70,50.70,108.30,52.00"], []),
    "s_auxtemp_g": ([
        "/Microcontroller Interface/AUX_TEMP",
    ], 10, 95, None, None, ["107.70,50.70,107.80,52.00"], []),
    "s_m1temp_g": ([
        "/Microcontroller Interface/M1_TEMP",
    ], 10, 95, None, None, [], []),
    "sa_m1temp": ([
        "/Microcontroller Interface/M1_TEMP",
    ], 10, 95, None, None, [], []),
    "g1_m1temp": ([
        "/Microcontroller Interface/M1_TEMP",
    ], 10, 95, None, None, [
        "108.35,52.30,113.05,55.20",
        "47.90,54.30,48.60,55.20",
        "66.00,50.35,66.25,50.65",
        "78.00,50.35,78.25,50.65",
        "93.00,50.35,93.25,50.65",
        "66.00,51.48,66.30,51.90",
        "78.00,53.05,78.30,53.48",
        "90.00,51.48,90.30,51.90",
    ], ["108.20,51.00,113.05,55.20", "47.60,53.20,51.00,56.50"]),
    "m1_al_via_open": ([
        "/Microcontroller Interface/M1_AL",
    ], 6, 95, None, None, [
        "54.50,56.55,55.30,57.10",
        "108.10,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "engate_u2_stub": ([
        "/Microcontroller Interface/EN_GATE",
    ], 4, 65, None, "53.80,54.90,54.70,60.10", [], []),
    "m1_al_first": ([
        "/Microcontroller Interface/M1_AL",
    ], 4, 80, None, None, [
        "107.60,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "66.00,51.05,66.30,51.90",
        "80.00,51.05,80.30,51.90",
        "94.00,51.05,94.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "m1_bh_second": ([
        "/Microcontroller Interface/M1_BH",
    ], 6, 95, None, None, [
        "107.60,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "118.60,44.40,120.20,46.00",
        "66.00,51.05,66.30,51.90",
        "80.00,51.05,80.30,51.90",
        "94.00,51.05,94.30,51.90",
    ], []),
    "pair_m1_al_bh": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
    ], 12, 125, None, None, [
        "107.60,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "118.60,44.40,120.20,46.00",
        "66.00,51.05,66.30,51.90",
        "80.00,51.05,80.30,51.90",
        "94.00,51.05,94.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "m1_al_1": ([
        "/Microcontroller Interface/M1_AL",
    ], 10, 100, None, None, [
        "52.55,55.20,52.90,58.80",
        "108.10,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "66.00,51.48,66.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "m1_bh_1": ([
        "/Microcontroller Interface/M1_BH",
    ], 12, 115, None, None, [
        "108.10,50.65,108.82,55.55",
        "109.62,50.65,110.55,53.80",
        "118.40,45.10,118.95,45.65",
        "66.00,51.05,66.30,51.40",
        "80.00,51.05,80.30,51.40",
        "94.00,51.05,94.30,51.40",
    ], []),
    "m1_3pwm_re": ([
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_AL",
    ], 14, 145, None, None, [
        "108.10,50.65,108.82,55.55",
        "109.62,50.65,110.55,55.20",
        "66.00,51.48,66.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "sa_m0temp_right": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 10, 95, None, None, [
        "107.60,50.65,110.02,54.75",
        "107.60,54.75,109.48,56.50",
    ], ["109.30,50.65,110.70,54.92"]),
    "sa_gpio5_left": ([
        "/I{slash}O Interface/GPIO_5",
    ], 12, 115, None, None, [
        "107.60,50.65,108.82,54.45",
        "119.15,20.40,120.85,23.60",
    ], []),
    "pair_gpio5_m0temp": ([
        "/I{slash}O Interface/GPIO_5",
        "/Microcontroller Interface/M0_TEMP",
    ], 14, 135, None, None, [
        "107.60,50.65,108.82,54.55",
        "119.15,20.40,120.85,23.60",
    ], ["109.30,50.65,110.70,53.95"]),
    "sb_gpio6_via": ([
        "/I{slash}O Interface/GPIO_6",
    ], 12, 115, None, None, [
        "107.60,50.65,108.82,54.45",
        "112.10,50.65,114.50,59.95",
        "105.60,60.05,110.05,61.08",
        "105.60,58.80,108.15,59.95",
        "118.15,20.40,120.85,23.60",
    ], ["110.10,50.65,114.50,59.95"]),
    "sb_auxl_fcu": ([
        "/Microcontroller Interface/AUX_L",
    ], 10, 100, None, None, [
        "112.55,50.65,113.20,54.50",
        "105.60,60.45,110.05,61.08",
        "104.80,60.20,105.60,64.00",
    ], ["106.00,50.65,114.50,61.05"]),
    "sb_auxh_fcu": ([
        "/Microcontroller Interface/AUX_H",
    ], 10, 100, None, None, [], ["106.00,50.65,114.50,61.05"]),
    "trio_b": ([
        "/I{slash}O Interface/GPIO_6",
        "/Microcontroller Interface/AUX_L",
        "/Microcontroller Interface/AUX_H",
    ], 16, 165, None, None, [
        "107.60,50.65,108.82,54.45",
        "118.15,20.40,120.85,23.60",
    ], ["111.30,50.65,114.50,58.50"]),
    "pair_gpio56": ([
        "/I{slash}O Interface/GPIO_5",
        "/I{slash}O Interface/GPIO_6",
    ], 14, 140, None, None, [
        "107.60,50.65,108.82,54.45",
        "110.22,50.65,110.65,53.50",
        "112.15,50.65,116.50,58.18",
        "119.15,20.40,120.85,23.60",
    ], ["109.20,50.65,116.50,58.50"]),
    "sa_gpio5": ([
        "/I{slash}O Interface/GPIO_5",
    ], 12, 115, None, None, [
        "107.60,50.65,108.82,54.45",
        "110.22,50.65,110.65,53.50",
        "119.15,20.40,120.85,23.60",
    ], ["109.50,50.65,110.80,56.20"]),
    "sa_m0temp": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 12, 115, None, None, [
        "107.60,50.65,108.82,54.45",
        "109.45,54.15,110.10,54.82",
    ], ["109.30,50.65,110.70,54.85"]),
    "sb_gpio6": ([
        "/I{slash}O Interface/GPIO_6",
    ], 10, 105, None, None, [
        "107.60,50.65,108.82,54.45",
        "109.20,55.60,111.42,57.60",
        "112.22,50.65,114.00,53.50",
        "118.15,20.40,120.85,23.60",
    ], ["111.30,50.65,114.50,56.50"]),
    "sb_auxh": ([
        "/Microcontroller Interface/AUX_H",
    ], 10, 95, None, None, [
        "107.60,50.65,108.82,54.45",
        "111.40,50.65,112.48,53.50",
    ], ["111.30,50.65,114.50,53.95", "111.30,53.95,112.90,56.50"]),
    "sb_auxl": ([
        "/Microcontroller Interface/AUX_L",
    ], 10, 105, None, None, [
        "107.60,50.65,108.82,54.45",
    ], ["111.30,50.65,114.50,53.95"]),
    "pair_aux_hl": ([
        "/Microcontroller Interface/AUX_L",
        "/Microcontroller Interface/AUX_H",
    ], 14, 140, None, None, [], ["111.30,50.65,116.20,58.85"]),
    "sa_vbuss": ([
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None, None, [
        "107.60,50.65,108.30,53.50",
    ], ["107.50,50.65,109.20,53.45"]),
    "sa_auxtemp": ([
        "/Microcontroller Interface/AUX_TEMP",
    ], 10, 95, None, None, [
        "107.55,50.65,107.82,53.50",
    ], ["107.50,50.65,109.20,53.45"]),
    "pa_3": ([
        "/Microcontroller Interface/M1_AL",
        "/I{slash}O Interface/GPIO_5",
        "/Microcontroller Interface/M0_TEMP",
    ], 14, 140, None, None, [
        "108.10,50.65,108.82,55.55",
        "119.15,20.40,120.85,23.60",
        "66.00,51.48,66.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], []),
    "pb_3": ([
        "/I{slash}O Interface/GPIO_6",
        "/Microcontroller Interface/AUX_L",
        "/Microcontroller Interface/AUX_H",
    ], 14, 140, None, None, [
        "108.10,50.65,108.82,55.55",
        "118.15,20.40,120.85,23.60",
    ], []),
    "pa_west2": ([
        "/Microcontroller Interface/VBUS_S",
        "/Microcontroller Interface/AUX_TEMP",
    ], 12, 120, None, None, [], []),
    "g2_auxtemp": ([
        "/Microcontroller Interface/AUX_TEMP",
    ], 10, 95, None, None, ["108.85,52.30,113.05,55.20"], ["108.70,51.00,113.05,55.20"]),
    "g3_vbuss": ([
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None, None, ["109.35,52.30,113.05,55.20"], ["109.20,51.00,113.05,55.20"]),
    "g4_m1al": ([
        "/Microcontroller Interface/M1_AL",
    ], 10, 95, None, None, [
        "109.52,50.65,113.05,55.40",
        "66.00,51.48,66.30,51.90",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], ["108.85,51.00,110.75,55.40"]),
    "g5_gpio5": ([
        "/I{slash}O Interface/GPIO_5",
    ], 12, 115, None, None, [
        "109.95,50.65,113.05,54.35",
        "119.15,20.40,120.85,23.60",
    ], ["109.45,51.00,110.75,54.45"]),
    "g6_m0temp": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 10, 95, None, None, ["111.60,50.65,113.05,51.65"], []),
    "g7_gpio6": ([
        "/I{slash}O Interface/GPIO_6",
    ], 10, 105, None, None, ["112.15,50.65,113.05,54.50", "118.15,20.40,120.85,23.60"], []),
    "g8_auxl": ([
        "/Microcontroller Interface/AUX_L",
    ], 10, 95, None, None, ["112.65,50.65,113.05,53.50"], []),
    "g9_auxh": ([
        "/Microcontroller Interface/AUX_H",
    ], 10, 95, None, None, [], []),
    "r_m0temp": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 10, 95, None, None, ["108.00,50.70,109.90,56.80"], ["108.00,50.70,109.90,56.80"]),
    "r_gpio5": ([
        "/I{slash}O Interface/GPIO_5",
    ], 12, 115, None, None, ["108.00,50.70,109.40,56.80", "119.15,20.40,120.85,23.60"], ["108.00,50.70,109.40,56.80"]),
    "r_m1al": ([
        "/Microcontroller Interface/M1_AL",
    ], 10, 95, None, None, [
        "108.00,50.70,108.90,56.80",
        "66.00,59.40,66.30,59.90",
        "80.00,60.10,80.30,60.60",
        "94.00,59.40,94.30,59.90",
    ], ["108.00,50.70,108.90,56.80"]),
    "r_vbuss": ([
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None, None, ["108.00,50.70,108.40,55.50"], ["108.00,50.70,108.45,56.80"]),
    "r_auxtemp": ([
        "/Microcontroller Interface/AUX_TEMP",
    ], 10, 95, None, None, [], []),
    "l_m1temp": ([
        "/Microcontroller Interface/M1_TEMP",
    ], 10, 95, None, None, [
        "108.35,52.30,110.50,57.30",
        "47.90,54.30,48.60,55.20",
        "66.00,50.35,66.25,50.65",
        "78.00,50.35,78.25,50.65",
        "93.00,50.35,93.25,50.65",
        "66.00,51.48,66.30,51.90",
        "78.00,53.05,78.30,53.48",
        "90.00,51.48,90.30,51.90",
    ], ["108.20,51.00,110.50,57.30", "47.60,53.20,51.00,56.50"]),
    "l_auxtemp": ([
        "/Microcontroller Interface/AUX_TEMP",
    ], 10, 95, None, None, ["108.85,52.30,110.50,57.30"], ["108.70,51.00,110.50,57.30"]),
    "l_vbuss": ([
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None, None, ["109.35,52.30,110.50,57.30"], ["109.20,51.00,110.50,57.30"]),
    "l_m1al": ([
        "/Microcontroller Interface/M1_AL",
    ], 10, 95, None, None, [
        "109.85,52.30,110.50,57.30",
        "66.00,50.35,66.25,50.65",
        "78.00,50.35,78.25,50.65",
        "93.00,50.35,93.25,50.65",
        "66.00,51.48,66.30,51.90",
        "78.00,53.05,78.30,53.48",
        "90.00,51.48,90.30,51.90",
    ], ["109.70,51.00,110.50,57.30"]),
    "l_gpio5": ([
        "/I{slash}O Interface/GPIO_5",
    ], 12, 115, None, None, ["110.30,52.30,110.55,57.30", "119.15,20.40,120.85,23.60"], ["110.20,51.00,110.55,57.30"]),
    "l_m0temp": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 12, 115, None, None, [], []),
    "south_temp4": ([
        "/Microcontroller Interface/M1_TEMP",
        "/Microcontroller Interface/AUX_TEMP",
        "/Microcontroller Interface/VBUS_S",
        "/Microcontroller Interface/M0_TEMP",
    ], 14, 150, None, None),
    "s_swdio": ([
        "/I{slash}O Interface/DEBUG_SWDIO",
    ], 10, 105, None, None, ["88.20,20.40,89.80,22.80", "115.20,20.60,120.80,23.20"]),
    "gpio78_first": ([
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
    ], 10, 105, None, None, ["117.20,20.60,120.80,23.20"]),
    "s_swclk": ([
        "/I{slash}O Interface/DEBUG_SWCLK",
    ], 10, 105, None, None, ["117.20,20.60,120.80,23.20"]),
    "swclk_gpio78": ([
        "/I{slash}O Interface/DEBUG_SWCLK",
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
    ], 12, 135, None, None, ["117.20,20.60,120.80,23.20"]),
    "swd_gpio78": ([
        "/I{slash}O Interface/DEBUG_SWCLK",
        "/I{slash}O Interface/DEBUG_SWDIO",
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
    ], 12, 135, None, None, ["117.20,20.60,120.80,23.20"]),
    "s_gpio6": ([
        "/I{slash}O Interface/GPIO_6",
    ], 10, 105, None, None, ["118.15,20.40,120.85,23.60"]),
    "s_gpio5": ([
        "/I{slash}O Interface/GPIO_5",
    ], 10, 105, None, None, ["119.15,20.40,120.85,23.60"]),
    "s_gpio4": ([
        "/I{slash}O Interface/GPIO_4",
    ], 10, 105, None, None, ["120.15,20.40,120.85,23.60"]),
    "s_gpio3": ([
        "/I{slash}O Interface/GPIO_3",
    ], 10, 105, None, None),
    "j6_gpio3456": ([
        "/I{slash}O Interface/GPIO_3",
        "/I{slash}O Interface/GPIO_4",
        "/I{slash}O Interface/GPIO_5",
        "/I{slash}O Interface/GPIO_6",
    ], 14, 150, None, None, ["109.05,49.80,109.45,52.60", "110.55,49.80,111.45,52.60"]),
    "west_gpio12": ([
        "/I{slash}O Interface/GPIO_1",
        "/I{slash}O Interface/GPIO_2",
    ], 10, 105, None, None),
    "south_left4": ([
        "/I{slash}O Interface/GPIO_4",
        "/Microcontroller Interface/M1_TEMP",
        "/Microcontroller Interface/AUX_TEMP",
        "/Microcontroller Interface/VBUS_S",
    ], 12, 140, None, None, ["110.55,49.80,111.45,52.80"]),
    "south_right5": ([
        "/I{slash}O Interface/GPIO_5",
        "/Microcontroller Interface/M0_TEMP",
        "/I{slash}O Interface/GPIO_6",
        "/Microcontroller Interface/AUX_L",
        "/Microcontroller Interface/AUX_H",
    ], 12, 150, None, None, ["110.55,49.80,111.45,52.80"]),
    "north_j6_j9_chute": ([
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
        "/I{slash}O Interface/DEBUG_SWCLK",
        "/I{slash}O Interface/DEBUG_SWDIO",
    ], 12, 140, None, None, ["111.05,35.40,112.95,38.20"]),
    "west_gpio123": ([
        "/I{slash}O Interface/GPIO_1",
        "/I{slash}O Interface/GPIO_2",
        "/I{slash}O Interface/GPIO_3",
    ], 10, 120, None, None),
    "m1_re5_clean": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 16, 175, None, None),
    "m0_re4_clean": ([
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CH",
        "/Microcontroller Interface/M0_CL",
    ], 16, 175, None, None),
    "spi7_clean": ([
        "Net-(U1-DC_CAL)",
        "Net-(U2-DC_CAL)",
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 18, 210, None, None),
    "3v3a_full": (["+3.3VA"], 26, 240, None, None, [
        "51.05,57.60,59.45,60.90",
        "169.05,57.60,177.45,60.90",
        "111.05,36.20,112.90,38.20",
        "115.70,40.95,118.20,41.55",
        "106.05,49.80,106.45,50.65",
        "109.05,49.80,109.95,50.65",
        "110.55,49.80,111.95,50.65",
        "103.10,46.50,104.20,48.00",
    ]),
    "m1_re5": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 16, 175, None, None, ["50.05,57.60,50.45,59.50", "56.05,57.60,59.45,58.95", "168.05,57.60,168.45,59.50", "174.05,57.60,177.45,58.95", "111.05,36.20,112.90,38.20"]),
    "m1_re3": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_CH",
    ], 14, 140, None, None),
    "m0_re3": ([
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CL",
    ], 14, 140, None, None, ["50.05,57.60,50.45,59.50", "56.05,57.60,59.45,58.95", "168.05,57.60,168.45,59.50", "174.05,57.60,177.45,58.95", "111.05,36.20,112.90,38.20"]),
    "b10_aux_hl": ([
        "/Microcontroller Interface/AUX_H",
        "/Microcontroller Interface/AUX_L",
    ], 10, 95, None, None),
    "s_m0temp": ([
        "/Microcontroller Interface/M0_TEMP",
    ], 8, 85, None, None),
    "south_m1al_3": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/VBUS_S",
        "/Microcontroller Interface/AUX_TEMP",
        "/Microcontroller Interface/M1_TEMP",
    ], 14, 150, None, None),
    "north_j6_j9": ([
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
        "/I{slash}O Interface/DEBUG_SWCLK",
        "/I{slash}O Interface/DEBUG_SWDIO",
    ], 14, 150, None, None),
    "spi4_only": ([
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/nFAULT",
    ], 18, 210, None, None),
    "enc0_bz": ([
        "/I{slash}O Interface/ENC0_B",
        "/I{slash}O Interface/ENC0_Z",
    ], 12, 110, None, None),
    "spi7_full": ([
        "Net-(U1-DC_CAL)",
        "Net-(U2-DC_CAL)",
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 18, 210, None, None, ["50.05,57.60,50.45,59.50", "168.05,57.60,168.45,59.50"]),
    "swd_pair": ([
        "/I{slash}O Interface/DEBUG_SWCLK",
        "/I{slash}O Interface/DEBUG_SWDIO",
    ], 10, 95, None, None),
    "spi6_full": ([
        "Net-(U1-DC_CAL)",
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 16, 180, None, None),
    "spi_east_6": ([
        "Net-(U1-DC_CAL)",
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 16, 170, None, "95.0,15.0,219.0,75.0"),
    "u1_dccal": (["Net-(U1-DC_CAL)"], 6, 75, None, None),
    "spi_east_5": ([
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 14, 150, None, "95.0,15.0,219.0,75.0"),
    "spi_u6_fan": ([
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 8, 85, None, "108.0,32.5,116.0,40.0"),
    "spi_east": ([
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 14, 150, None, "108.0,15.0,219.0,75.0"),
    "nfl_u2_r39": (["/Microcontroller Interface/nFAULT"], 4, 65, None, "58.0,56.5,62.0,60.8"),
    "s_west_miso": (["/Microcontroller Interface/SPI_MISO"], 6, 75, None, None),
    "s_west_mosi": (["/Microcontroller Interface/SPI_MOSI"], 6, 75, None, None),
    "s_west_sck": (["/Microcontroller Interface/SPI_SCK"], 6, 75, None, None),
    "spi_west_3": ([
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
    ], 12, 130, None, None),
    "nfl_west": (["/Microcontroller Interface/nFAULT"], 8, 95, None, None),
    "3v3a_u6": (["+3.3VA"], 6, 75, None, "95.0,45.0,105.5,50.5"),
    "3v3a_ldo": (["+3.3VA"], 6, 75, None, "124.5,50.5,132.5,55.5"),
    "3v3a_all": (["+3.3VA"], 14, 150, None, None, [
        "51.05,57.60,59.45,58.95",
        "169.05,57.60,177.45,58.95",
        "111.05,36.20,112.90,38.20",
        "109.05,49.80,109.45,50.65",
        "110.55,49.80,111.40,50.65",
    ]),
    "spi_west": ([
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 14, 150, None, None),
    "s_swclk": (["/I{slash}O Interface/DEBUG_SWCLK"], 6, 75, None, None),
    "spi5_all": ([
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_M1_nCS",
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/SPI_MISO",
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/nFAULT",
    ], 18, 220, None),
    "fix_dccal_m1a": ([
        "Net-(U2-DC_CAL)",
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_AL",
    ], 12, 110, None),
    "s_u2_dccal": (["Net-(U2-DC_CAL)"], 6, 75, None),
    "b5_cs_swclk_only": ([
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_M1_nCS",
        "/I{slash}O Interface/DEBUG_SWCLK",
    ], 10, 95, None),
    "east14": ([
        "/I{slash}O Interface/ENC0_Z",
        "/Microcontroller Interface/EN_GATE",
        "/Microcontroller Interface/M0_AH",
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BH",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CH",
        "/Microcontroller Interface/M0_CL",
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 22, 260, None),
    "pwm_all12": ([
        "/Microcontroller Interface/M0_AH",
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BH",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CH",
        "/Microcontroller Interface/M0_CL",
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 18, 240, None),
    "m1_bl_ch_cl": ([
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 12, 125, None),
    "s_m1_bh": (["/Microcontroller Interface/M1_BH"], 6, 75, None),
    "s_m1_bl": (["/Microcontroller Interface/M1_BL"], 6, 75, None),
    "s_m1_ch": (["/Microcontroller Interface/M1_CH"], 6, 75, None),
    "s_m1_cl": (["/Microcontroller Interface/M1_CL"], 6, 75, None),
    "s_enc0z": (["/I{slash}O Interface/ENC0_Z"], 6, 75, None),
    "m0_c": (["/Microcontroller Interface/M0_CH", "/Microcontroller Interface/M0_CL"], 8, 90, None),
    "m0_b": (["/Microcontroller Interface/M0_BH", "/Microcontroller Interface/M0_BL"], 8, 90, None),
    "m0_a": (["/Microcontroller Interface/M0_AH", "/Microcontroller Interface/M0_AL"], 8, 90, None),
    "s_engate": (["/Microcontroller Interface/EN_GATE"], 8, 95, None),
    "m1_bc_enc0z": ([
        "/I{slash}O Interface/ENC0_Z",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 14, 150, None),
    "m1_bh_c": ([
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 12, 115, None),
    "m1_c": ([
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 8, 95, None),
    "m1_b": ([
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
    ], 8, 95, None),
    "m1_a": ([
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_AL",
    ], 8, 95, None),
    "b12_m1_all6": ([
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CH",
        "/Microcontroller Interface/M1_CL",
    ], 16, 220, None),
    "b3_m0_all6": ([
        "/Microcontroller Interface/M0_AH",
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BH",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CH",
        "/Microcontroller Interface/M0_CL",
    ], 14, 150, None),
    "b34_m0_all6_en": ([
        "/Microcontroller Interface/M0_AH",
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BH",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CH",
        "/Microcontroller Interface/M0_CL",
        "/Microcontroller Interface/EN_GATE",
    ], 16, 220, None),
    "b1_m1h": ([
        "/Microcontroller Interface/M1_AH",
        "/Microcontroller Interface/M1_BH",
        "/Microcontroller Interface/M1_CH",
    ], 8, 95, None),
    "b2_m1l": ([
        "/Microcontroller Interface/M1_AL",
        "/Microcontroller Interface/M1_BL",
        "/Microcontroller Interface/M1_CL",
    ], 8, 95, None),
    "b3_m0h": ([
        "/Microcontroller Interface/M0_AH",
        "/Microcontroller Interface/M0_BH",
        "/Microcontroller Interface/M0_CH",
    ], 8, 95, None),
    "b4_m0l_en": ([
        "/Microcontroller Interface/M0_AL",
        "/Microcontroller Interface/M0_BL",
        "/Microcontroller Interface/M0_CL",
        "/Microcontroller Interface/EN_GATE",
    ], 10, 105, None),
    "b5_cs_swclk": ([
        "/Microcontroller Interface/SPI_M0_nCS",
        "/Microcontroller Interface/SPI_M1_nCS",
        "/I{slash}O Interface/DEBUG_SWCLK",
        "Net-(U2-DC_CAL)",
    ], 8, 95, None),
    "b6a_spi2": ([
        "/Microcontroller Interface/SPI_SCK",
        "/Microcontroller Interface/SPI_MISO",
    ], 10, 105, None),
    "b6b_mosi_flt": ([
        "/Microcontroller Interface/SPI_MOSI",
        "/Microcontroller Interface/nFAULT",
    ], 10, 105, None),
    "b7a_gpio78": ([
        "/I{slash}O Interface/GPIO_7",
        "/I{slash}O Interface/GPIO_8",
    ], 8, 85, None),
    "b7b_gpio56": ([
        "/I{slash}O Interface/GPIO_5",
        "/I{slash}O Interface/GPIO_6",
    ], 8, 85, None),
    "b7c_gpio34": ([
        "/I{slash}O Interface/GPIO_3",
        "/I{slash}O Interface/GPIO_4",
    ], 8, 85, None),
    "b7d_gpio12": ([
        "/I{slash}O Interface/GPIO_1",
        "/I{slash}O Interface/GPIO_2",
    ], 8, 85, None),
    "enc0z_only": ([
        "/I{slash}O Interface/ENC0_Z",
    ], 10, 95, None, None),
    "b8a_m1so_step": ([
        "/Microcontroller Interface/M1_SO1",
        "/Microcontroller Interface/M1_SO2",
    ], 10, 95, None, None, ["73.80,47.20,74.20,50.10", "61.80,47.20,62.20,50.60"]),
    "b8b_m0so_step": ([
        "/Microcontroller Interface/M0_SO1",
        "/Microcontroller Interface/M0_SO2",
    ], 10, 95, None, None, ["146.80,55.50,147.20,58.20", "157.80,55.50,158.20,58.20"]),
    "b8a_m1so": ([
        "/Microcontroller Interface/M1_SO1",
        "/Microcontroller Interface/M1_SO2",
    ], 10, 95, None),
    "b8b_m0so": ([
        "/Microcontroller Interface/M0_SO1",
        "/Microcontroller Interface/M0_SO2",
    ], 10, 95, None),
    "b9_3v3a": ([
        "+3.3VA",
    ], 12, 110, None),
    "b10a_aux": ([
        "/Microcontroller Interface/AUX_H",
        "/Microcontroller Interface/AUX_L",
        "/Microcontroller Interface/VBUS_S",
    ], 10, 95, None),
    "b10b_temp": ([
        "/Microcontroller Interface/AUX_TEMP",
        "/Microcontroller Interface/M0_TEMP",
        "/Microcontroller Interface/M1_TEMP",
    ], 10, 95, None),
    "3v3a_rest": (["+3.3VA"], 20, 195, None, None),
    "b11_gnd2": ([
        "GND",
    ], 8, 85, "GND:97.0,32.0,108.0,47.0"),
}


def main() -> None:
    if sys.argv[1] == "reset_mh1a":
        shutil.copy2(".copperpilot/tmp/v9_6_ckpt_mh1A_local_so_dvdd.kicad_pcb", PCB)
        print("Reset candidate PCB to v9_6_ckpt_mh1A_local_so_dvdd.kicad_pcb")
        return
    for gname in sys.argv[1:]:
        entry = GROUPS[gname]
        fcu_b = None
        nvb = None
        if len(entry) == 7:
            nets, mp, to_s, lvp, tpbox, fcu_b, nvb = entry
        elif len(entry) == 6:
            nets, mp, to_s, lvp, tpbox, fcu_b = entry
        elif len(entry) == 5:
            nets, mp, to_s, lvp, tpbox = entry
        else:
            nets, mp, to_s, lvp = entry
            tpbox = None
        if not run_group(
            gname, nets, max_passes=mp, timeout_sec=to_s,
            local_via_pairs=lvp, target_pads_box=tpbox, extra_fcu_boxes=fcu_b, extra_novia_boxes=nvb,
        ):
            sys.exit(2)


if __name__ == "__main__":
    main()
