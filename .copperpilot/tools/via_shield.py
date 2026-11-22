#!/usr/bin/env python3
"""Connected-copper-island isolator for surgical FreeRouting runs on staged .kicad_pcb files.

Why this exists:
When `kicad_autorouter/main.py route --nets ...` strips non-target component pads
into `CP_SKIP_PIN_*`, any non-target net whose copper tracks/vias/zones were bridged
through component pads (e.g. +5V across L1/U4, /Motor Driver/SH_C across C15/U1, or
unrouted U6 fanout vias) splits into disconnected copper components. FreeRouting 2.2.4
still queues multi-component copper nets even when their class is in `-inc`, causing
180s maze-search stalls on power/driver nets.

`shield` uses KiCad's native `pcbnew` connectivity graph (with pads temporarily detached
in memory) to find exact copper-only connected components on non-target nets:
  - Component #0 of each non-target net keeps its original net name.
  - Disconnected copper components #1..#k (including unattached fanout/stitching vias)
    and any pads touching them are temporarily assigned unique 1-component nets
    `__CP_ISO_<id>__` mapped to the same netclass in `.kicad_pro` (preserving 100% of
    physical copper obstacles and clearance rules with 0 DRC shorts and 0 non-target
    FreeRouting incompletes).
  - Pure footprint-keepout rule areas (`footprints not_allowed`, `tracks allowed`,
    `vias allowed`) are stashed because `pcbnew.ExportSpecctraDSN` mis-exports them
    as `F.Cu` wire keepouts.

`restore` restores all original net names on tracks, vias, zones, and pads, removes
temporary `(net N "__CP_ISO_*__")` declarations, restores `.kicad_pro`, and restores
stashed footprint-keepout rule areas.

Strictly refuses to touch any path outside `.copperpilot/tmp/staging/`.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import pcbnew


def check_staging(p: str) -> Path:
    path = Path(p)
    if ".copperpilot/tmp/staging/" not in str(path):
        raise RuntimeError(f"Refusing to run outside staging: {path}")
    return path


def shield(
    pcb_path: Path,
    pro_path: Path,
    keep_nets: set[str],
    state_path: Path,
    temp_fcu_boxes: list[tuple[float, float, float, float]] = (),
    temp_bcu_boxes: list[tuple[float, float, float, float]] = (),
    temp_novia_boxes: list[tuple[float, float, float, float]] = (),
    target_pads_box: tuple[float, float, float, float] | None = None,
    local_via_pairs: tuple[str, float, float, float, float] | None = None,
    pairs_out: Path | None = None,
) -> None:
    keep_nets = set(keep_nets) | {k.replace("{slash}", "/") for k in keep_nets} | {k.replace("/", "{slash}") for k in keep_nets}
    pro_orig_text = pro_path.read_text()

    # Pre-scan S-expression to stash pure footprint-keepout rule areas AND inner power-plane
    # zones (In1.Cu / In2.Cu) BEFORE LoadBoard so zero SWIG board.Remove(z) calls are needed.
    raw_txt = pcb_path.read_text()
    stashed_blocks: list[str] = []

    def strip_stashed_zones(src_txt: str) -> str:
        pieces: list[str] = []
        pos = 0
        n = len(src_txt)
        i = 0
        in_str = False
        depth = 0
        b_start = -1
        while i < n:
            ch = src_txt[i]
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
                    if depth == 2 and src_txt.startswith("zone", i + 1) and src_txt[i + 5] in " \t\r\n":
                        b_start = i
                elif ch == ")":
                    if depth == 2 and b_start != -1:
                        blk = src_txt[b_start : i + 1]
                        hdr = blk[:600]
                        is_fp_ko = (
                            "(keepout" in hdr
                            and bool(re.search(r"\(tracks\s+allowed\)", hdr))
                            and bool(re.search(r"\(vias\s+allowed\)", hdr))
                            and bool(re.search(r"\(footprints\s+not_allowed\)", hdr))
                        )
                        is_pair_zone = (
                            local_via_pairs is not None
                            and "(keepout" not in hdr
                            and f'(net_name "{local_via_pairs[0]}")' in hdr
                        )
                        is_inner_plane = (
                            "(keepout" not in hdr
                            and bool(re.search(r'\(layer\s+"In[12]\.Cu"\)', hdr))
                            and not ({"GND", "+3.3V", "VDC"} & keep_nets)
                        )
                        if is_fp_ko or is_pair_zone or is_inner_plane:
                            stashed_blocks.append("\n\t" + blk)
                            pieces.append(src_txt[pos:b_start])
                            pos = i + 1
                        b_start = -1
                    depth -= 1
            i += 1
        pieces.append(src_txt[pos:])
        return "".join(pieces)

    pcb_path.write_text(strip_stashed_zones(raw_txt))
    board = pcbnew.LoadBoard(str(pcb_path))

    # Build full connectivity first so we know which pads touch which copper items
    conn_full = board.GetConnectivity()
    conn_full.Build(board)

    # Save pad nets and temporarily detach pads in-memory to find copper-only islands
    pad_orig_net: dict[str, str] = {}
    pad_by_uuid: dict[str, pcbnew.PAD] = {}
    pad_touching_copper: dict[str, list[str]] = defaultdict(list)

    copper_types = {pcbnew.PCB_TRACE_T, pcbnew.PCB_VIA_T, pcbnew.PCB_ZONE_T}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pu = pad.m_Uuid.AsString()
            nname = pad.GetNetname()
            pad_orig_net[pu] = nname
            pad_by_uuid[pu] = pad
            if nname and nname not in keep_nets:
                for ci in conn_full.GetConnectedItems(pad):
                    if ci.Type() in copper_types:
                        pad_touching_copper[pu].append(ci.m_Uuid.AsString())

    # Move all footprints off-board in a scratch reload to compute pure copper+zone components
    # (matching Specctra DSN after kicad_autorouter reassigns non-target pads to CP_SKIP_PIN_*)
    scratch = pcbnew.LoadBoard(str(pcb_path))
    off_vec = pcbnew.VECTOR2I(pcbnew.FromMM(-999.0), pcbnew.FromMM(-999.0))
    for fp in scratch.GetFootprints():
        fp.Move(off_vec)
    conn_cu = scratch.GetConnectivity()
    conn_cu.Build(scratch)

    scratch_items: list[pcbnew.BOARD_CONNECTED_ITEM] = []
    for t in scratch.GetTracks():
        scratch_items.append(t)
    for z in scratch.Zones():
        if not z.GetIsRuleArea():
            scratch_items.append(z)

    visited: set[str] = set()
    net_clusters: dict[str, list[list[str]]] = defaultdict(list)
    for item in scratch_items:
        uid = item.m_Uuid.AsString()
        if uid in visited:
            continue
        nname = item.GetNetname()
        if not nname or nname in keep_nets:
            visited.add(uid)
            continue
        comp = [ uid ]
        visited.add(uid)
        queue = [item]
        while queue:
            cur = queue.pop()
            for nb in conn_cu.GetConnectedItems(cur):
                if nb.Type() not in copper_types:
                    continue
                nu = nb.m_Uuid.AsString()
                if nu not in visited and nb.GetNetname() == nname:
                    visited.add(nu)
                    comp.append(nu)
                    queue.append(nb)
        net_clusters[nname].append(comp)

    # Map live board items by UUID
    live_items: dict[str, pcbnew.BOARD_CONNECTED_ITEM] = {}
    for t in board.GetTracks():
        live_items[t.m_Uuid.AsString()] = t
    for z in board.Zones():
        if not z.GetIsRuleArea():
            live_items[z.m_Uuid.AsString()] = z

    # Determine original net -> netclass from .kicad_pro
    pro_data = json.loads(pro_orig_text)
    ds = pro_data.get("board", {}).get("design_settings", {})
    nc_assign = pro_data.get("net_settings", {}).get("netclass_assignments") or {}
    nc_patterns = pro_data.get("net_settings", {}).get("netclass_patterns") or []

    def class_for_net(net_name: str) -> str:
        if net_name in nc_assign and nc_assign[net_name]:
            return nc_assign[net_name]
        import fnmatch
        for pat in nc_patterns:
            p = pat.get("pattern", "")
            nc = pat.get("netclass", "")
            if p and nc and fnmatch.fnmatchcase(net_name, p):
                return nc
        return "Default"

    item_restore: dict[str, dict] = {}
    pad_restore: dict[str, str] = {}
    iso_net_to_class: dict[str, str] = {}
    cu_uid_to_iso: dict[str, str] = {}

    iso_counter = 0
    for nname, clusters in net_clusters.items():
        # Sort largest cluster first so main plane/pour keeps original net name
        clusters.sort(key=len, reverse=True)
        # Note: even a 1-cluster net with 1 unattached via and unrouted pins has 0 pins once
        # main.py strips non-target pins into CP_SKIP_PIN_*, EXCEPT when a single via has no
        # other copper items (len==1, 1 cluster -> already 1/1 connected once pins are stripped!).
        # Only clusters[1:] create multi-component copper splits!
        if len(clusters) <= 1:
            continue
        nclass = class_for_net(nname)
        for comp in clusters[1:]:
            iso_counter += 1
            iso_name = f"__CP_ISO_{iso_counter}__"
            ni = pcbnew.NETINFO_ITEM(board, iso_name)
            board.Add(ni)
            if nclass != "Default":
                iso_net_to_class[iso_name] = nclass
            for uid in comp:
                cu_uid_to_iso[uid] = iso_name
                obj = live_items[uid]
                was_free = obj.GetIsFree() if obj.GetClass() == "PCB_VIA" else False
                item_restore[uid] = {"net": nname, "free": was_free}
                obj.SetNet(ni)
                if obj.GetClass() == "PCB_VIA":
                    obj.SetIsFree(True)

    # Update any non-target pads touching reassigned copper clusters so pre/post DRC has 0 shorts
    for pu, touched_uids in pad_touching_copper.items():
        isos = {cu_uid_to_iso[u] for u in touched_uids if u in cu_uid_to_iso}
        if len(isos) == 1:
            iso_name = next(iter(isos))
            ni = board.FindNet(iso_name)
            pad_restore[pu] = pad_orig_net[pu]
            pad_by_uuid[pu].SetNet(ni)

    # Optional: isolate any disconnected target-net sub-components whose pads all lie outside target_pads_box
    if target_pads_box is not None:
        bx1, by1, bx2, by2 = target_pads_box
        t_seen: set[str] = set()
        for tname in sorted(keep_nets):
            t_comps: list[tuple[int, bool, list[pcbnew.BOARD_CONNECTED_ITEM]]] = []
            seeds: list[pcbnew.BOARD_CONNECTED_ITEM] = []
            for fp in board.GetFootprints():
                for pad in fp.Pads():
                    if pad.GetNetname() == tname:
                        seeds.append(pad)
            for t in board.GetTracks():
                if t.GetNetname() == tname:
                    seeds.append(t)
            for z in board.Zones():
                if not z.GetIsRuleArea() and z.GetNetname() == tname:
                    seeds.append(z)
            for sd in seeds:
                su = sd.m_Uuid.AsString()
                if su in t_seen:
                    continue
                t_seen.add(su)
                members = [sd]
                q = [sd]
                in_box = False
                while q:
                    cur = q.pop()
                    if cur.Type() in (pcbnew.PCB_PAD_T, pcbnew.PCB_VIA_T):
                        px, py = pcbnew.ToMM(cur.GetPosition().x), pcbnew.ToMM(cur.GetPosition().y)
                        if bx1 <= px <= bx2 and by1 <= py <= by2:
                            in_box = True
                    for nb in conn_full.GetConnectedItems(cur):
                        if nb.GetNetname() != tname:
                            continue
                        nu = nb.m_Uuid.AsString()
                        if nu not in t_seen:
                            t_seen.add(nu)
                            members.append(nb)
                            q.append(nb)
                t_comps.append((len(members), in_box, members))
            if len(t_comps) > 1 and any(ib for _, ib, _ in t_comps):
                nclass = class_for_net(tname)
                for _, in_box, members in t_comps:
                    if in_box:
                        continue
                    iso_counter += 1
                    iso_name = f"__CP_ISO_{iso_counter}__"
                    ni = pcbnew.NETINFO_ITEM(board, iso_name)
                    board.Add(ni)
                    if nclass != "Default":
                        iso_net_to_class[iso_name] = nclass
                    for m in members:
                        mu = m.m_Uuid.AsString()
                        if m.Type() == pcbnew.PCB_PAD_T:
                            pad_restore[mu] = tname
                            m.SetNet(ni)
                        elif m.Type() in copper_types:
                            was_free = (m.Type() == pcbnew.PCB_VIA_T)
                            item_restore[mu] = {"net": tname, "free": was_free}
                            m.SetNet(ni)

    pair_net_restore: dict[str, str] = {}
    if local_via_pairs is not None:
        import math as _math
        pname, lx1, ly1, lx2, ly2 = local_via_pairs
        cand_vias = [
            t for t in board.GetTracks()
            if t.GetClass() == "PCB_VIA"
            and item_restore.get(t.m_Uuid.AsString(), {}).get("net", t.GetNetname()) == pname
            and lx1 <= pcbnew.ToMM(t.GetPosition().x) <= lx2
            and ly1 <= pcbnew.ToMM(t.GetPosition().y) <= ly2
        ]
        via_to_pair: dict[str, str] = {}
        pair_idx = 0
        # Walk connected F.Cu pad+track islands (excluding zones) inside box and attach to nearest cand_via
        non_zone_types = {pcbnew.PCB_TRACE_T, pcbnew.PCB_ARC_T, pcbnew.PCB_VIA_T}
        p_seen: set[str] = set()
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetname() != pname:
                    continue
                px, py = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
                if not (lx1 <= px <= lx2 and ly1 <= py <= ly2):
                    continue
                pu = pad.m_Uuid.AsString()
                if pu in p_seen:
                    continue
                # BFS only across pads + tracks + vias (skipping zones!)
                q = [pad]
                p_seen.add(pu)
                members = [pad]
                has_via = False
                while q:
                    cur = q.pop()
                    if cur.Type() == pcbnew.PCB_VIA_T:
                        has_via = True
                    for nb in conn_full.GetConnectedItems(cur):
                        if nb.Type() == pcbnew.PCB_ZONE_T or nb.GetNetname() != pname:
                            continue
                        nu = nb.m_Uuid.AsString()
                        if nu not in p_seen:
                            p_seen.add(nu)
                            members.append(nb)
                            q.append(nb)
                if has_via or not cand_vias:
                    continue
                best_v = min(
                    cand_vias,
                    key=lambda v: _math.hypot(pcbnew.ToMM(v.GetPosition().x) - px, pcbnew.ToMM(v.GetPosition().y) - py),
                )
                vu = best_v.m_Uuid.AsString()
                if vu not in via_to_pair:
                    pair_idx += 1
                    pair_name = f"__CP_PAIR_{pair_idx}__"
                    ni = pcbnew.NETINFO_ITEM(board, pair_name)
                    board.Add(ni)
                    nclass = class_for_net(pname)
                    if nclass != "Default":
                        iso_net_to_class[pair_name] = nclass
                    pair_net_restore[pair_name] = pname
                    via_to_pair[vu] = pair_name
                    keep_nets.add(pair_name)
                    item_restore[vu] = {"net": pname, "free": True}
                    best_v.SetNet(ni)
                pair_name = via_to_pair[vu]
                ni = board.FindNet(pair_name)
                for m in members:
                    mu = m.m_Uuid.AsString()
                    if m.Type() == pcbnew.PCB_PAD_T:
                        pad_restore[mu] = pname
                        m.SetNet(ni)
                    elif m.Type() in non_zone_types:
                        item_restore[mu] = {"net": pname, "free": m.GetClass() == "PCB_VIA"}
                        m.SetNet(ni)
        if pairs_out is not None:
            pairs_out.write_text(",".join(sorted(pair_net_restore.keys())))

    # Eliminate false CP_SKIP_PIN_* vs fixed-wire overlaps near target pins/footprints:
    # Any non-target pure (pad + track/via, 0-zone) connected cluster touching a target footprint
    # or within 3.5 mm of a target pad/via gets a unified __CP_FIX_k__ net passed in --pairs-out.
    if pairs_out is not None:
        import math as _math
        conn_full.Build(board)
        active_targets = set(keep_nets) | set(pair_net_restore.keys())
        target_pts: list[tuple[float, float]] = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetname() in active_targets:
                    target_pts.append((pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)))

        f_seen: set[str] = set()
        fix_idx = 0
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                cnet = pad.GetNetname()
                if not cnet or cnet in active_targets:
                    continue
                pu = pad.m_Uuid.AsString()
                if pu in f_seen:
                    continue
                f_seen.add(pu)
                members = [pad]
                q = [pad]
                has_cu = False
                has_zone = False
                near_target = False
                while q:
                    cur = q.pop()
                    if cur.Type() == pcbnew.PCB_ZONE_T:
                        has_zone = True
                    elif cur.Type() in (pcbnew.PCB_TRACE_T, pcbnew.PCB_ARC_T, pcbnew.PCB_VIA_T):
                        has_cu = True
                    if cur.Type() == pcbnew.PCB_PAD_T and not near_target:
                        cx, cy = pcbnew.ToMM(cur.GetPosition().x), pcbnew.ToMM(cur.GetPosition().y)
                        for tx, ty in target_pts:
                            if abs(cx - tx) <= 0.62 and abs(cy - ty) <= 0.62 and _math.hypot(cx - tx, cy - ty) <= 0.62:
                                near_target = True
                                break
                    for nb in conn_full.GetConnectedItems(cur):
                        if nb.GetNetname() != cnet:
                            continue
                        nu = nb.m_Uuid.AsString()
                        if nu not in f_seen:
                            f_seen.add(nu)
                            members.append(nb)
                            q.append(nb)
                has_jumper57 = any(m.Type() == pcbnew.PCB_PAD_T and m.GetNumber() == "57" for m in members)
                # Ensure every pad in __CP_FIX_k__ has a segment/via endpoint at its exact center so FreeRouting sees 0 unrouted items
                ep_pts: list[tuple[float, float]] = []
                for m in members:
                    if m.Type() == pcbnew.PCB_VIA_T:
                        ep_pts.append((pcbnew.ToMM(m.GetPosition().x), pcbnew.ToMM(m.GetPosition().y)))
                    elif m.Type() == pcbnew.PCB_TRACE_T:
                        ep_pts.append((pcbnew.ToMM(m.GetStart().x), pcbnew.ToMM(m.GetStart().y)))
                        ep_pts.append((pcbnew.ToMM(m.GetEnd().x), pcbnew.ToMM(m.GetEnd().y)))
                pads_in_m = [m for m in members if m.Type() == pcbnew.PCB_PAD_T]
                all_centered = all(
                    any(abs(pcbnew.ToMM(p.GetPosition().x) - ex) <= 0.02 and abs(pcbnew.ToMM(p.GetPosition().y) - ey) <= 0.02 for ex, ey in ep_pts)
                    for p in pads_in_m
                )
                if has_cu and not has_zone and not has_jumper57 and len(members) <= 25 and near_target and all_centered:
                    orig_net = pad_restore.get(pu, cnet)
                    fix_idx += 1
                    fix_name = f"__CP_FIX_{fix_idx}__"
                    ni = pcbnew.NETINFO_ITEM(board, fix_name)
                    board.Add(ni)
                    pair_net_restore[fix_name] = orig_net
                    nclass = class_for_net(orig_net)
                    if nclass != "Default":
                        iso_net_to_class[fix_name] = nclass
                    for m in members:
                        mu = m.m_Uuid.AsString()
                        if m.Type() == pcbnew.PCB_PAD_T:
                            pad_restore.setdefault(mu, orig_net)
                            m.SetNet(ni)
                        elif m.Type() in copper_types:
                            was_free = (m.Type() == pcbnew.PCB_VIA_T)
                            item_restore.setdefault(mu, {"net": orig_net, "free": was_free})
                            m.SetNet(ni)
                            m.SetLocked(True)
        # Any __CP_ISO_*__ net with 0 pads and 0 zones is omitted from (network ...) by
        # pcbnew.ExportSpecctraDSN, causing FreeRouting write_wire_scope warnings. Stash those
        # standalone vias into stashed_blocks and guard their exact 0.48mm (0.30 + 0.18) circle!
        nets_with_pad_or_zone: set[str] = {
            pad.GetNetname() for fp in board.GetFootprints() for pad in fp.Pads() if pad.GetNetCode() > 0
        }
        for z in board.Zones():
            if not z.GetIsRuleArea() and z.GetNetCode() > 0:
                nets_with_pad_or_zone.add(z.GetNetname())
        lone_via_circles: list[tuple[float, float, float]] = []
        lone_via_uuids: set[str] = set()
        for t in list(board.GetTracks()):
            nn = t.GetNetname()
            if nn.startswith("__CP_ISO_") and nn not in nets_with_pad_or_zone:
                uid = t.m_Uuid.AsString()
                orig_n = item_restore.pop(uid, {}).get("net", nn)
                if t.GetClass() == "PCB_VIA":
                    vx, vy = round(pcbnew.ToMM(t.GetPosition().x), 4), round(pcbnew.ToMM(t.GetPosition().y), 4)
                    vd = round(pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)), 4)
                    vdr = round(pcbnew.ToMM(t.GetDrillValue()), 4)
                    stashed_blocks.append(
                        f'\n\t(via\n\t\t(at {vx} {vy})\n\t\t(size {vd})\n\t\t(drill {vdr})'
                        f'\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(free)\n\t\t(net "{orig_n}")\n\t\t(uuid "{uid}")\n\t)'
                    )
                    lone_via_circles.append((vx, vy, 0.5 * vd + 0.185))
                    lone_via_uuids.add(uid)

        pairs_out.write_text(",".join(sorted(pair_net_restore.keys())))

    else:
        lone_via_circles = []
        lone_via_uuids = set()

    # Ensure every via retains its assigned net across DSN export; lock non-target vias ((type fix))
    # while leaving target-net vias unlocked so FreeRouting can route out on B.Cu/F.Cu freely!
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            t.SetIsFree(True)
            t.SetLocked((target_pads_box is not None) or (t.GetNetname() not in keep_nets))

    roundrect_pads: list[str] = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetShape() == pcbnew.PAD_SHAPE_ROUNDRECT:
                roundrect_pads.append(pad.m_Uuid.AsString())
                pad.SetShape(pcbnew.PAD_SHAPE_RECT)

    pcbnew.SaveBoard(str(pcb_path), board)
    if lone_via_uuids:
        vtxt = pcb_path.read_text()
        vpieces: list[str] = []
        vpos = 0
        vn = len(vtxt)
        vi = 0
        vin_str = False
        vdepth = 0
        vb_start = -1
        while vi < vn:
            vch = vtxt[vi]
            if vin_str:
                if vch == "\\":
                    vi += 2
                    continue
                if vch == '"':
                    vin_str = False
            else:
                if vch == '"':
                    vin_str = True
                elif vch == "(":
                    vdepth += 1
                    if vdepth == 2 and vtxt.startswith("via", vi + 1) and vtxt[vi + 4] in " \t\r\n":
                        vb_start = vi
                elif vch == ")":
                    if vdepth == 2 and vb_start != -1:
                        vblk = vtxt[vb_start : vi + 1]
                        vm = re.search(r'\(uuid\s+"([^"]+)"\)', vblk)
                        if vm and vm.group(1) in lone_via_uuids:
                            vpieces.append(vtxt[vpos:vb_start])
                            vpos = vi + 1
                        vb_start = -1
                    vdepth -= 1
            vi += 1
        vpieces.append(vtxt[vpos:])
        pcb_path.write_text("".join(vpieces))

    temp_zone_uuids: list[str] = []
    if temp_fcu_boxes or temp_bcu_boxes or temp_novia_boxes or lone_via_circles:
        import math as _math
        import uuid as _uuid
        saved_txt = pcb_path.read_text()
        extra_zones: list[str] = []
        for (vx, vy, rad) in lone_via_circles:
            zu = str(_uuid.uuid4())
            temp_zone_uuids.append(zu)
            x1, y1 = round(vx - rad, 4), round(vy - rad, 4)
            x2, y2 = round(vx + rad, 4), round(vy + rad, 4)
            pts_str = f"(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})"
            extra_zones.append(
                f'\n\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(uuid "{zu}")'
                f'\n\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)'
                f'\n\t\t(min_thickness 0.25)\n\t\t(keepout\n\t\t\t(tracks not_allowed)'
                f'\n\t\t\t(copperpour allowed)\n\t\t\t(vias not_allowed)\n\t\t\t(pads allowed)'
                f'\n\t\t\t(footprints allowed)\n\t\t)\n\t\t(polygon\n\t\t\t(pts\n\t\t\t\t{pts_str}\n\t\t\t)\n\t\t)\n\t)'
            )
        for (x1, y1, x2, y2) in temp_fcu_boxes:
            zu = str(_uuid.uuid4())
            temp_zone_uuids.append(zu)
            extra_zones.append(
                f'\n\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layer "F.Cu")\n\t\t(uuid "{zu}")'
                f'\n\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)'
                f'\n\t\t(min_thickness 0.25)\n\t\t(keepout\n\t\t\t(tracks not_allowed)'
                f'\n\t\t\t(copperpour allowed)\n\t\t\t(vias allowed)\n\t\t\t(pads allowed)'
                f'\n\t\t\t(footprints allowed)\n\t\t)\n\t\t(polygon\n\t\t\t(pts'
                f'\n\t\t\t\t(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})'
                f'\n\t\t\t)\n\t\t)\n\t)'
            )
        for (x1, y1, x2, y2) in temp_bcu_boxes:
            zu = str(_uuid.uuid4())
            temp_zone_uuids.append(zu)
            extra_zones.append(
                f'\n\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layer "B.Cu")\n\t\t(uuid "{zu}")'
                f'\n\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)'
                f'\n\t\t(min_thickness 0.25)\n\t\t(keepout\n\t\t\t(tracks not_allowed)'
                f'\n\t\t\t(copperpour allowed)\n\t\t\t(vias allowed)\n\t\t\t(pads allowed)'
                f'\n\t\t\t(footprints allowed)\n\t\t)\n\t\t(polygon\n\t\t\t(pts'
                f'\n\t\t\t\t(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})'
                f'\n\t\t\t)\n\t\t)\n\t)'
            )
        for (x1, y1, x2, y2) in temp_novia_boxes:
            zu = str(_uuid.uuid4())
            temp_zone_uuids.append(zu)
            extra_zones.append(
                f'\n\t(zone\n\t\t(net 0)\n\t\t(net_name "")\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(uuid "{zu}")'
                f'\n\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)'
                f'\n\t\t(min_thickness 0.25)\n\t\t(keepout\n\t\t\t(tracks allowed)'
                f'\n\t\t\t(copperpour allowed)\n\t\t\t(vias not_allowed)\n\t\t\t(pads allowed)'
                f'\n\t\t\t(footprints allowed)\n\t\t)\n\t\t(polygon\n\t\t\t(pts'
                f'\n\t\t\t\t(xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2})'
                f'\n\t\t\t)\n\t\t)\n\t)'
            )
        close_idx = saved_txt.rfind(")")
        pcb_path.write_text(saved_txt[:close_idx] + "".join(extra_zones) + "\n" + saved_txt[close_idx:])

    if iso_net_to_class:
        pro_data.setdefault("net_settings", {}).setdefault("netclass_patterns", [])
        for iso_name, nclass in iso_net_to_class.items():
            pro_data["net_settings"]["netclass_patterns"].append(
                {"netclass": nclass, "pattern": iso_name}
            )
        pro_path.write_text(json.dumps(pro_data, indent=2) + "\n")

    state_path.write_text(
        json.dumps(
            {
                "pro_orig_text": pro_orig_text,
                "item_restore": item_restore,
                "pad_restore": pad_restore,
                "stashed_blocks": stashed_blocks,
                "temp_zone_uuids": temp_zone_uuids,
                "pair_net_restore": pair_net_restore,
                "roundrect_pads": roundrect_pads,
            }
        )
    )
    print(
        f"Isolated {iso_counter} split copper islands ({len(item_restore)} copper items, "
        f"{len(pad_restore)} pads, {len(stashed_blocks)} blocks stashed)."
    )


def restore(pcb_path: Path, pro_path: Path, state_path: Path) -> None:
    st = json.loads(state_path.read_text())
    pro_path.write_text(st["pro_orig_text"])

    board = pcbnew.LoadBoard(str(pcb_path))
    temp_zone_uuids: set[str] = set(st.get("temp_zone_uuids", []))
    item_restore: dict[str, dict] = st["item_restore"]
    pad_restore: dict[str, str] = st["pad_restore"]
    pair_net_restore: dict[str, str] = st.get("pair_net_restore", {})

    def get_or_add_net(nname: str):
        ni = board.FindNet(nname)
        if ni is None and nname:
            ni = pcbnew.NETINFO_ITEM(board, nname)
            board.Add(ni)
        return ni

    restored_items = 0
    for t in board.GetTracks():
        uid = t.m_Uuid.AsString()
        if uid in item_restore:
            info = item_restore[uid]
            ni = get_or_add_net(info["net"])
            if ni is not None:
                t.SetNet(ni)
            if t.GetClass() == "PCB_VIA":
                t.SetIsFree(True)
            restored_items += 1
        elif t.GetNetname() in pair_net_restore:
            ni = get_or_add_net(pair_net_restore[t.GetNetname()])
            if ni is not None:
                t.SetNet(ni)
            if t.GetClass() == "PCB_VIA":
                t.SetIsFree(True)
            restored_items += 1

    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            t.SetIsFree(True)

    for z in board.Zones():
        uid = z.m_Uuid.AsString()
        if uid in item_restore:
            ni = get_or_add_net(item_restore[uid]["net"])
            if ni is not None:
                z.SetNet(ni)
            restored_items += 1

    roundrect_set: set[str] = set(st.get("roundrect_pads", []))
    restored_pads = 0
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pu = pad.m_Uuid.AsString()
            if pu in roundrect_set:
                pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
            if pu in pad_restore:
                ni = get_or_add_net(pad_restore[pu])
                if ni is not None:
                    pad.SetNet(ni)
                    restored_pads += 1

    pcbnew.SaveBoard(str(pcb_path), board)

    # Strip temporary `(net N "__CP_ISO_...__")` header declarations, temp keepouts, and restore stashed zones
    txt = pcb_path.read_text()
    txt = re.sub(r'\n\t\(net\s+\d+\s+"__CP_(?:ISO|PAIR|FIX)_\d+__"\)', "", txt)
    if temp_zone_uuids:
        pieces: list[str] = []
        pos = 0
        n = len(txt)
        i = 0
        in_str = False
        depth = 0
        b_start = -1
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
                    if depth == 2 and txt.startswith("zone", i + 1) and txt[i + 5] in " \t\r\n":
                        b_start = i
                elif ch == ")":
                    if depth == 2 and b_start != -1:
                        blk = txt[b_start : i + 1]
                        m = re.search(r'\(uuid\s+"([^"]+)"\)', blk[:300])
                        if m and m.group(1) in temp_zone_uuids:
                            pieces.append(txt[pos:b_start])
                            pos = i + 1
                        b_start = -1
                    depth -= 1
            i += 1
        pieces.append(txt[pos:])
        txt = "".join(pieces)
    stashed_blocks: list[str] = st.get("stashed_blocks", [])
    if stashed_blocks:
        close_idx = txt.rfind(")")
        txt = txt[:close_idx] + "".join(stashed_blocks) + "\n" + txt[close_idx:]
    pcb_path.write_text(txt)
    print(
        f"Restored {restored_items}/{len(item_restore)} copper items, "
        f"{restored_pads}/{len(pad_restore)} pads, and {len(stashed_blocks)} fp-keepouts."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_sh = sub.add_parser("shield")
    p_sh.add_argument("--pcb", required=True)
    p_sh.add_argument("--pro", required=True)
    p_sh.add_argument("--keep-nets", default="")
    p_sh.add_argument("--temp-fcu-box", action="append", default=[])
    p_sh.add_argument("--temp-bcu-box", action="append", default=[])
    p_sh.add_argument("--temp-novia-box", action="append", default=[])
    p_sh.add_argument("--target-pads-box", default="")
    p_sh.add_argument("--local-via-pairs", default="")
    p_sh.add_argument("--pairs-out", default="")
    p_sh.add_argument("--state", required=True)

    p_re = sub.add_parser("restore")
    p_re.add_argument("--pcb", required=True)
    p_re.add_argument("--pro", required=True)
    p_re.add_argument("--state", required=True)

    args = ap.parse_args()
    pcb_path = check_staging(args.pcb)
    pro_path = check_staging(args.pro)
    state_path = Path(args.state)

    if args.cmd == "shield":
        keep = {s.strip() for s in args.keep_nets.split(",") if s.strip()}
        boxes = [tuple(float(v) for v in b.split(",")) for b in args.temp_fcu_box]
        bboxes = [tuple(float(v) for v in b.split(",")) for b in args.temp_bcu_box]
        nvboxes = [tuple(float(v) for v in b.split(",")) for b in args.temp_novia_box]
        tpbox = tuple(float(v) for v in args.target_pads_box.split(",")) if args.target_pads_box else None
        lvp = None
        if args.local_via_pairs:
            pn, coords = args.local_via_pairs.split(":", 1)
            cvals = [float(v) for v in coords.split(",")]
            lvp = (pn, cvals[0], cvals[1], cvals[2], cvals[3])
        pout = Path(args.pairs_out) if args.pairs_out else None
        shield(pcb_path, pro_path, keep, state_path, boxes, bboxes, nvboxes, tpbox, lvp, pout)
    else:
        restore(pcb_path, pro_path, state_path)


if __name__ == "__main__":
    main()
