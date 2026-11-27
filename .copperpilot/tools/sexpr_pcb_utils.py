#!/usr/bin/env python3
"""
Clean S-expression utilities for KiCad 10 .kicad_pcb files:
- set_footprint_pose(txt, ref, x, y, rot=None)
- remove_vias_pred(txt, pred_fn)   # pred_fn(net, x, y) -> bool
- mark_all_vias_free(txt)
- add_vias(txt, via_list)          # [(net, x, y, size, drill), ...]
- remove_zones_pred(txt, pred_fn)  # pred_fn(net, layer, pts) -> bool
- strip_all_filled_polygons(txt)
- add_zones(txt, zone_list)        # [(net, layer, prio, clr, min_thick, pts), ...]
- add_board_only_0603_cap(txt, ref, val, x, y, rot, pad1_net, pad2_net)
"""
import re, uuid


def _find_top_blocks(txt, head_token):
    """Return list of (start_idx, end_idx, block_str) for top-level `(head_token ...)` blocks (depth 1 inside `(kicad_pcb ...)`)."""
    out = []
    n = len(txt)
    depth = 0
    in_str = False
    esc = False
    tok_len = len(head_token)
    b_start = -1
    i = 0
    while i < n:
        ch = txt[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "(":
                depth += 1
                if depth == 2:
                    if txt[i + 1 : i + 1 + tok_len] == head_token and (
                        i + 1 + tok_len < n and txt[i + 1 + tok_len] in (" ", "\t", "\n", "\r")
                    ):
                        b_start = i
                    else:
                        b_start = -1
            elif ch == ")":
                if depth == 2 and b_start != -1:
                    out.append((b_start, i + 1, txt[b_start : i + 1]))
                    b_start = -1
                depth -= 1
        i += 1
    return out


def set_footprint_poses_batch(txt, pose_map):
    """Single-pass batch pose update: pose_map = {ref: (x, y, rot_or_None)}."""
    blocks = _find_top_blocks(txt, "footprint")
    pieces = []
    last = 0
    found = set()
    for s, e, blk in blocks:
        p_idx = blk.find('(property "Reference" "')
        if p_idx != -1:
            q0 = p_idx + len('(property "Reference" "')
            q1 = blk.find('"', q0)
            ref = blk[q0:q1]
            if ref in pose_map:
                found.add(ref)
                x, y, rot = pose_map[ref]
                first_p = blk.find('(property "')
                head = blk[:first_p]
                m = re.search(r"\(at\s+[-0-9.]+\s+[-0-9.]+(?:\s+[-0-9.]+)?\)", head)
                assert m is not None, f"No (at ...) in {ref}"
                if rot is None:
                    parts = m.group(0)[1:-1].split()
                    new_at = f"(at {x:g} {y:g}" + (f" {parts[3]})" if len(parts) > 3 else ")")
                else:
                    new_at = f"(at {x:g} {y:g})" if rot == 0 else f"(at {x:g} {y:g} {rot:g})"
                blk = head[: m.start()] + new_at + head[m.end() :] + blk[first_p:]
        pieces.append(txt[last:s])
        pieces.append(blk)
        last = e
    pieces.append(txt[last:])
    missing = set(pose_map.keys()) - found
    if missing:
        raise KeyError(f"Footprints not found: {sorted(missing)}")
    return "".join(pieces)


def set_footprint_pose(txt, ref, x, y, rot=None):
    blocks = _find_top_blocks(txt, "footprint")
    target_prop = f'(property "Reference" "{ref}"'
    for s, e, blk in blocks:
        if target_prop in blk:
            # Replace first (at X Y [ROT]) at footprint level (before first property)
            p_idx = blk.find('(property "')
            head = blk[:p_idx]
            m = re.search(r"\(at\s+[-0-9.]+\s+[-0-9.]+(?:\s+[-0-9.]+)?\)", head)
            assert m is not None, f"No (at ...) in {ref}"
            if rot is None:
                # keep existing rot if present
                parts = m.group(0)[1:-1].split()
                new_at = f"(at {x:g} {y:g}" + (f" {parts[3]})" if len(parts) > 3 else ")")
            else:
                new_at = f"(at {x:g} {y:g})" if rot == 0 else f"(at {x:g} {y:g} {rot:g})"
            new_blk = head[:m.start()] + new_at + head[m.end():] + blk[p_idx:]
            return txt[:s] + new_blk + txt[e:]
    raise KeyError(f"Footprint {ref} not found")


def remove_vias_pred(txt, pred_fn):
    blocks = _find_top_blocks(txt, "via")
    if not blocks:
        return txt
    pieces = []
    last = 0
    for s, e, blk in blocks:
        m_at = re.search(r"\(at\s+([-0-9.]+)\s+([-0-9.]+)\)", blk)
        m_net = re.search(r'\(net\s+"([^"]*)"\)', blk)
        vx = float(m_at.group(1))
        vy = float(m_at.group(2))
        vnet = m_net.group(1) if m_net else ""
        if pred_fn(vnet, vx, vy):
            # also trim leading \n\t if present
            cut_s = s - 2 if s >= 2 and txt[s - 2:s] == "\n\t" else s
            pieces.append(txt[last:cut_s])
            last = e
    pieces.append(txt[last:])
    return "".join(pieces)


def mark_all_vias_free(txt):
    blocks = _find_top_blocks(txt, "via")
    if not blocks:
        return txt
    pieces = []
    last = 0
    for s, e, blk in blocks:
        pieces.append(txt[last:s])
        if "(free yes)" not in blk:
            blk = blk.replace('(layers "F.Cu" "B.Cu")', '(layers "F.Cu" "B.Cu")\n\t\t(free yes)', 1)
        pieces.append(blk)
        last = e
    pieces.append(txt[last:])
    return "".join(pieces)


def add_vias(txt, via_list):
    chunks = []
    for (net, x, y, size, drill) in via_list:
        u = str(uuid.uuid4())
        chunks.append(
            f'\n\t(via\n\t\t(at {x:g} {y:g})\n\t\t(size {size:g})\n\t\t(drill {drill:g})\n'
            f'\t\t(layers "F.Cu" "B.Cu")\n\t\t(free yes)\n\t\t(net "{net}")\n\t\t(uuid "{u}")\n\t)'
        )
    end_pos = txt.rfind(")")
    return txt[:end_pos] + "".join(chunks) + "\n" + txt[end_pos:]


def remove_zones_pred(txt, pred_fn):
    blocks = _find_top_blocks(txt, "zone")
    if not blocks:
        return txt
    pieces = []
    last = 0
    for s, e, blk in blocks:
        # Read header before (polygon
        p_poly = blk.find("(polygon")
        hdr = blk[:p_poly] if p_poly != -1 else blk
        m_net = re.search(r'\(net\s+"([^"]*)"\)', hdr)
        m_lay = re.search(r'\(layer\s+"([^"]*)"\)', hdr)
        znet = m_net.group(1) if m_net else ""
        zlay = m_lay.group(1) if m_lay else ""
        poly_sec = blk[p_poly:blk.find("(filled_polygon")] if "(filled_polygon" in blk else blk[p_poly:]
        pts = [(float(a), float(b)) for a, b in re.findall(r"\(xy\s+([-0-9.]+)\s+([-0-9.]+)\)", poly_sec)]
        if pred_fn(znet, zlay, pts):
            cut_s = s - 2 if s >= 2 and txt[s - 2:s] == "\n\t" else s
            pieces.append(txt[last:cut_s])
            last = e
    pieces.append(txt[last:])
    return "".join(pieces)


def strip_all_filled_polygons(txt):
    """Remove all `(filled_polygon ...)` sub-blocks inside zones so kicad-cli --refill-zones starts cleanly."""
    out = []
    idx = 0
    n = len(txt)
    pat = "(filled_polygon"
    while True:
        pos = txt.find(pat, idx)
        if pos == -1:
            break
        # trim preceding tabs/newline
        cut_s = pos
        while cut_s > idx and txt[cut_s - 1] in (" ", "\t"):
            cut_s -= 1
        if cut_s > idx and txt[cut_s - 1] == "\n":
            cut_s -= 1
        depth = 0
        in_str = False
        esc = False
        i = pos
        while i < n:
            ch = txt[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
            i += 1
        out.append(txt[idx:cut_s])
        idx = i
    out.append(txt[idx:])
    return "".join(out)


def add_zones(txt, zone_list):
    chunks = []
    for (net, layer, prio, clr, min_thick, pts) in zone_list:
        u = str(uuid.uuid4())
        pts_str = " ".join(f"(xy {x:g} {y:g})" for (x, y) in pts)
        chunks.append(
            f'\n\t(zone\n\t\t(net "{net}")\n\t\t(layer "{layer}")\n\t\t(uuid "{u}")\n'
            f'\t\t(hatch edge 0.5)\n\t\t(priority {prio})\n'
            f'\t\t(connect_pads yes\n\t\t\t(clearance {clr:g})\n\t\t)\n'
            f'\t\t(min_thickness {min_thick:g})\n'
            f'\t\t(fill yes\n\t\t\t(thermal_gap 0.5)\n\t\t\t(thermal_bridge_width 0.8)\n\t\t\t(island_removal_mode 0)\n\t\t)\n'
            f'\t\t(polygon\n\t\t\t(pts\n\t\t\t\t{pts_str}\n\t\t\t)\n\t\t)\n\t)'
        )
    end_pos = txt.rfind(")")
    return txt[:end_pos] + "".join(chunks) + "\n" + txt[end_pos:]


def add_board_only_0603_cap(txt, ref, val, x, y, rot, pad1_net, pad2_net):
    """Insert exact stock KiCad 10 Capacitor_SMD:C_0603_1608Metric footprint as board_only SMD capacitor."""
    from pathlib import Path
    mod = Path("/usr/share/kicad/footprints/Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod").read_text()
    # Convert library header to placed board footprint
    mod = mod.replace('(footprint "C_0603_1608Metric"', '(footprint "Capacitor_SMD:C_0603_1608Metric"', 1)
    # Remove library version/generator lines
    mod = re.sub(r'\n\t\(version\s+[0-9]+\)', '', mod, count=1)
    mod = re.sub(r'\n\t\(generator\s+"[^"]*"\)', '', mod, count=1)
    mod = re.sub(r'\n\t\(generator_version\s+"[^"]*"\)', '', mod, count=1)
    at_str = f"(at {x:g} {y:g})" if rot == 0 else f"(at {x:g} {y:g} {rot:g})"
    mod = mod.replace('\t(layer "F.Cu")', f'\t(layer "F.Cu")\n\t(uuid "{uuid.uuid4()}")\n\t{at_str}', 1)
    # Set Reference and Value, and ensure silk text height >= 0.8 mm, thickness >= 0.08 mm (stock is 1.0 / 0.15 -> clean!)
    # Hide silk Reference or place safely? Wait: stock C_0603 Reference is size 1x1, thickness 0.15; hide Reference on SilkS?
    # Wait: if Reference sits over adjacent copper pad it causes silk_over_copper warning! Putting (hide yes) on Reference or placing cleanly avoids silk_over_copper!
    # Wait: let's check if hiding Reference causes any DRC warning: NO! KiCad DRC does not require visible Reference on board_only decoupling caps!
    # Even better: keep Reference on F.Fab or hidden on F.SilkS so zero silk_over_copper / silk_overlap warnings!
    mod = re.sub(
        r'\(property "Reference" "REF\*\*"(.*?)\n\t\)',
        f'(property "Reference" "{ref}"\\1\n\t)',
        mod, count=1, flags=re.S
    )
    mod = re.sub(
        r'\(property "Value" "C_0603_1608Metric"(.*?)\n\t\)',
        f'(property "Value" "{val}"\\1\n\t)',
        mod, count=1, flags=re.S
    )
    mod = mod.replace("(attr smd)", "(attr smd board_only exclude_from_pos_files exclude_from_bom)", 1)
    # Hide silk Reference so zero silk_over_copper risk; keep Value on F.Fab
    mod = mod.replace('(property "Reference"', '(property "Reference"', 1)
    mod = re.sub(r'(\(property "Reference" "[^"]*"\n\t\t\(at [^\n]+\n\t\t\(layer "F\.SilkS"\))', r'\1\n\t\t(hide yes)', mod, count=1)
    # Assign nets and uuids to pads 1 and 2
    def _repl_pad(m):
        pnum = m.group(1)
        body = m.group(2)
        pnet = pad1_net if pnum == "1" else pad2_net
        return f'(pad "{pnum}"{body}\n\t\t(net "{pnet}")\n\t\t(uuid "{uuid.uuid4()}")\n\t)'
    mod = re.sub(r'\(pad "(1|2)"(.*?)\n\t\)', _repl_pad, mod, flags=re.S)
    # Indent top-level footprint by 1 tab
    indented = "\n".join("\t" + line if line else "" for line in mod.strip().splitlines())
    end_pos = txt.rfind(")")
    return txt[:end_pos] + "\n" + indented + "\n" + txt[end_pos:]
