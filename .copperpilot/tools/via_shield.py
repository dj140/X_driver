#!/usr/bin/env python3
"""O(N) S-expression non-target via shield/restore for staged .kicad_pcb files.

Uses a linear balanced-parenthesis scanner (0.03s on 3 MB .kicad_pcb, zero regex
backtracking and zero KiCad SWIG ZONE destructor segfaults).
"""
from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path

AT_RE = re.compile(r"\(at\s+([-\d.]+)\s+([-\d.]+)\)")
SIZE_RE = re.compile(r"\(size\s+([-\d.]+)\)")
UUID_RE = re.compile(r'\(uuid\s+"([^"]+)"\)')
NET_RE = re.compile(r'\(net\s+"([^"]*)"\)')
SEG_ENDPOINTS_RE = re.compile(
    r"\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)"
)
FP_KEEPOUT_SUB = "(keepout\n\t\t\t(tracks allowed)\n\t\t\t(copperpour allowed)\n\t\t\t(vias allowed)\n\t\t\t(pads allowed)\n\t\t\t(footprints not_allowed)"


def iter_top_blocks(txt: str, head_tokens: tuple[str, ...]):
    """Yield (start, end, kind, block_text) for top-level (via ...) / (zone ...) blocks in O(N)."""
    n = len(txt)
    i = 0
    in_str = False
    depth = 0
    blk_start = -1
    blk_kind = ""
    while i < n:
        ch = txt[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "(":
                depth += 1
                if depth == 2:
                    for tok in head_tokens:
                        if txt.startswith(tok, i + 1) and txt[i + 1 + len(tok)] in " \t\r\n":
                            blk_start = i
                            blk_kind = tok
                            break
            elif ch == ")":
                if depth == 2 and blk_start != -1:
                    yield (blk_start, i + 1, blk_kind, txt[blk_start : i + 1])
                    blk_start = -1
                    blk_kind = ""
                depth -= 1
        i += 1


def fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def make_box_keepout(cx: float, cy: float, r: float, kind: str, uid: str) -> str:
    x1, x2 = fmt(cx - r), fmt(cx + r)
    y1, y2 = fmt(cy - r), fmt(cy + r)
    tracks_rule = "not_allowed" if kind == "wire" else "allowed"
    vias_rule = "not_allowed" if kind == "via" else "allowed"
    return (
        f'\n\t(zone\n'
        f'\t\t(net 0)\n'
        f'\t\t(net_name "")\n'
        f'\t\t(layers "F.Cu" "B.Cu")\n'
        f'\t\t(uuid "{uid}")\n'
        f'\t\t(hatch edge 0.5)\n'
        f'\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)\n'
        f'\t\t(min_thickness 0.25)\n'
        f'\t\t(filled_areas_thickness no)\n'
        f'\t\t(keepout\n'
        f'\t\t\t(tracks {tracks_rule})\n'
        f'\t\t\t(copperpour allowed)\n'
        f'\t\t\t(vias {vias_rule})\n'
        f'\t\t\t(pads allowed)\n'
        f'\t\t\t(footprints allowed)\n'
        f'\t\t)\n'
        f'\t\t(fill\n\t\t\t(thermal_gap 0.5)\n\t\t\t(thermal_bridge_width 0.5)\n\t\t)\n'
        f'\t\t(polygon\n\t\t\t(pts\n'
        f'\t\t\t\t(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})\n'
        f'\t\t\t)\n\t\t)\n'
        f'\t)'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_sh = sub.add_parser("shield")
    p_sh.add_argument("--pcb", required=True)
    p_sh.add_argument("--keep-nets", default="")
    p_sh.add_argument("--state", required=True)

    p_re = sub.add_parser("restore")
    p_re.add_argument("--pcb", required=True)
    p_re.add_argument("--state", required=True)

    args = ap.parse_args()
    if ".copperpilot/tmp/staging/" not in args.pcb:
        raise RuntimeError(f"Refusing outside staging: {args.pcb}")

    pcb_path = Path(args.pcb)
    txt = pcb_path.read_text()

    if args.cmd == "shield":
        keep = {s.strip() for s in args.keep_nets.split(",") if s.strip()}
        seg_pts = []
        for sm in SEG_ENDPOINTS_RE.finditer(txt):
            seg_pts.append((float(sm.group(1)), float(sm.group(2))))
            seg_pts.append((float(sm.group(3)), float(sm.group(4))))

        saved_vias = []
        guard_zones = []
        guard_uuids = []
        stashed_fp_zones = []
        pieces = []
        pos = 0

        for b_start, b_end, kind, blk in iter_top_blocks(txt, ("via", "zone")):
            pieces.append(txt[pos:b_start])
            pos = b_end
            if kind == "zone":
                if "footprints not_allowed" in blk and "(tracks allowed)" in blk and "(vias allowed)" in blk:
                    stashed_fp_zones.append("\n\t" + blk)
                    continue
                pieces.append(blk)
            else:
                nm = NET_RE.search(blk)
                am = AT_RE.search(blk)
                sm = SIZE_RE.search(blk)
                um = UUID_RE.search(blk)
                if not (nm and am and sm and um):
                    pieces.append(blk)
                    continue
                net_name = nm.group(1)
                if not net_name or net_name in keep:
                    pieces.append(blk)
                    continue
                vx, vy = float(am.group(1)), float(am.group(2))
                vsz = float(sm.group(1))
                v_uid = um.group(1)
                saved_vias.append({"uuid": v_uid, "x": round(vx, 4), "y": round(vy, 4), "net": net_name})
                if vy <= 78.0:
                    attached = any(abs(px - vx) < 0.05 and abs(py - vy) < 0.05 for px, py in seg_pts)
                    if not attached:
                        r = round(vsz * 0.5 + 0.01, 4)
                        for gkind in ("wire", "via"):
                            z_uid = str(uuid.uuid4())
                            guard_uuids.append(z_uid)
                            guard_zones.append(make_box_keepout(vx, vy, r, gkind, z_uid))
                pieces.append(blk[: nm.start()] + '(net "")' + blk[nm.end() :])

        pieces.append(txt[pos:])
        new_txt = "".join(pieces)
        if guard_zones:
            close_idx = new_txt.rfind(")")
            new_txt = new_txt[:close_idx] + "".join(guard_zones) + "\n" + new_txt[close_idx:]

        pcb_path.write_text(new_txt)
        Path(args.state).write_text(
            json.dumps({"vias": saved_vias, "zones": guard_uuids, "fp_zones": stashed_fp_zones})
        )
        print(
            f"Shielded {len(saved_vias)} vias (+{len(guard_uuids)} IntBox guards, "
            f"stashed {len(stashed_fp_zones)} fp-keepouts)."
        )

    elif args.cmd == "restore":
        st = json.loads(Path(args.state).read_text())
        by_uid = {it["uuid"]: it["net"] for it in st["vias"]}
        by_xy = {(it["x"], it["y"]): it["net"] for it in st["vias"]}
        zone_uuids = set(st["zones"])
        fp_zones = st.get("fp_zones", [])

        removed_z = 0
        restored = 0
        pieces = []
        pos = 0

        for b_start, b_end, kind, blk in iter_top_blocks(txt, ("via", "zone")):
            pieces.append(txt[pos:b_start])
            pos = b_end
            if kind == "zone":
                um = UUID_RE.search(blk)
                if um and um.group(1) in zone_uuids:
                    removed_z += 1
                    continue
                pieces.append(blk)
            else:
                nm = NET_RE.search(blk)
                am = AT_RE.search(blk)
                um = UUID_RE.search(blk)
                if not (nm and am and um):
                    pieces.append(blk)
                    continue
                v_uid = um.group(1)
                key_xy = (round(float(am.group(1)), 4), round(float(am.group(2)), 4))
                orig_net = by_uid.get(v_uid) or by_xy.get(key_xy)
                if orig_net:
                    restored += 1
                    esc = orig_net.replace('"', '\\"')
                    pieces.append(blk[: nm.start()] + f'(net "{esc}")' + blk[nm.end() :])
                else:
                    pieces.append(blk)

        pieces.append(txt[pos:])
        new_txt = "".join(pieces)
        if fp_zones:
            close_idx = new_txt.rfind(")")
            new_txt = new_txt[:close_idx] + "".join(fp_zones) + "\n" + new_txt[close_idx:]
        pcb_path.write_text(new_txt)
        if restored != len(st["vias"]):
            raise RuntimeError(f"Expected to restore {len(st['vias'])} vias, got {restored}!")
        print(
            f"Restored {restored}/{len(st['vias'])} vias, removed {removed_z}/{len(zone_uuids)} IntBox guards, "
            f"and restored {len(fp_zones)} fp-keepouts."
        )


if __name__ == "__main__":
    main()
