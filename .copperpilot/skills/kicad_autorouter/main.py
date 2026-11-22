#!/usr/bin/env python3
"""KiCad FreeRouting autorouter skill installed by CopperPilot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Literal, Optional

Platform = Literal["win", "mac", "linux"]

DEFAULT_SKILL_MAIN_PY = ".copperpilot/skills/kicad_autorouter/main.py"

DEFAULT_FREEROUTING_VERSION = "2.2.4"
MIN_JAVA_MAJOR = 25


def default_freerouting_url(version: str = DEFAULT_FREEROUTING_VERSION) -> str:
    return (
        f"https://github.com/freerouting/freerouting/releases/download/"
        f"v{version}/freerouting-{version}.jar"
    )


def default_freerouting_jar_name(
    version: str = DEFAULT_FREEROUTING_VERSION,
) -> str:
    return f"freerouting-{version}.jar"


def default_skill_cache_dir(project_dir: Path) -> Path:
    return project_dir / ".copperpilot" / "skills" / "kicad_autorouter" / "cache"


def pcbnew_sys_path_candidates(platform: Platform) -> List[Path]:
    """Candidate directories to prepend to sys.path for importing pcbnew."""
    env = os.environ.get("KICAD_PYTHON_SITE_PACKAGES")
    candidates: List[Path] = []
    if env:
        candidates.append(Path(env))

    if platform == "mac":
        candidates.extend(
            [
                Path(
                    "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
                    "Python.framework/Versions/Current/lib/python3.11/"
                    "site-packages"
                ),
                Path(
                    "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
                    "Python.framework/Versions/3.11/lib/python3.11/"
                    "site-packages"
                ),
            ]
        )
    elif platform == "win":
        candidates.extend(
            [
                Path(r"C:\Program Files\KiCad\10.0\bin\Lib\site-packages"),
                Path(r"C:\Program Files\KiCad\9.0\bin\Lib\site-packages"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("/usr/lib/kicad/lib/python3/dist-packages"),
                Path("/usr/lib/kicad/lib/python3/site-packages"),
                Path("/usr/share/kicad/scripting/plugins"),
            ]
        )
    return candidates


def kicad_bundled_python_candidates(platform: Platform) -> List[Path]:
    """Candidate KiCad-bundled Python executables for importing pcbnew."""
    env = os.environ.get("KICAD_PYTHON")
    candidates: List[Path] = []
    if env:
        candidates.append(Path(env))

    if platform == "mac":
        framework_root = Path(
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
            "Python.framework/Versions"
        )
        version_dirs = ["Current", "3.11", "3.10", "3.9"]
        for version in version_dirs:
            base = framework_root / version / "bin"
            candidates.extend(
                [
                    base / "python3",
                    base / "python3.11",
                    base / "python3.10",
                    base / "python3.9",
                ]
            )
    elif platform == "win":
        for version in ("10.0", "9.0", "8.0"):
            candidates.extend(
                [
                    Path(rf"C:\Program Files\KiCad\{version}\bin\python.exe"),
                    Path(rf"C:\Program Files\KiCad\{version}\bin\python3.exe"),
                ]
            )
    else:
        candidates.extend(
            [
                Path("/usr/bin/python3"),
                Path("/usr/share/kicad/bin/python3"),
                Path("/usr/share/kicad/bin/python"),
            ]
        )

    deduped: List[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def kicad_cli_candidates(platform: Platform) -> List[str]:
    """Candidate kicad-cli executables for local post-route actions."""
    if platform == "mac":
        return [
            "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
            "/opt/homebrew/bin/kicad-cli",
            "/usr/local/bin/kicad-cli",
            "kicad-cli",
        ]
    if platform == "win":
        return [
            r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
            r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe",
            r"C:\Program Files\KiCad\8.0\bin\kicad-cli.exe",
            "kicad-cli.exe",
            "kicad-cli",
        ]
    return [
        "/usr/bin/kicad-cli",
        "/usr/local/bin/kicad-cli",
        "/app/bin/kicad-cli",
        "kicad-cli",
    ]


def resolve_project_path(
    value: Optional[str | Path],
    project_dir: Path,
) -> Optional[Path]:
    """Resolve a user path relative to project_dir unless already absolute."""
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (project_dir / path).resolve()


def quote_shell_arg(value: str) -> str:
    if not value:
        return '""'
    if any(ch.isspace() for ch in value) or '"' in value:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def build_skill_command(
    python_executable: Path,
    *,
    subcommand: str,
    platform: Platform,
    script_path: str = DEFAULT_SKILL_MAIN_PY,
    project_dir: Optional[str] = None,
    pcb_path: Optional[str] = None,
    java_bin: str = "java",
) -> str:
    parts = [
        quote_shell_arg(str(python_executable)),
        quote_shell_arg(script_path),
    ]
    parts.append(subcommand)
    parts.extend(["--platform", platform])
    if subcommand == "route":
        parts.extend(["--project-dir", quote_shell_arg(project_dir or ".")])
        if pcb_path is not None:
            parts.extend(["--pcb", quote_shell_arg(pcb_path)])
    if java_bin != "java":
        parts.extend(["--java-bin", quote_shell_arg(java_bin)])
    return " ".join(parts)


def get_platform_defaults(
    platform: Platform,
    *,
    freerouting_version: str = DEFAULT_FREEROUTING_VERSION,
) -> Dict[str, str]:
    return {
        "platform": platform,
        "freerouting_version": freerouting_version,
        "freerouting_url": default_freerouting_url(freerouting_version),
        "freerouting_jar_name": default_freerouting_jar_name(freerouting_version),
        "skill_cache_dir": ".copperpilot/skills/kicad_autorouter/cache",
        "pcbnew_site_paths": ", ".join(
            str(path) for path in pcbnew_sys_path_candidates(platform)
        ),
        "kicad_bundled_python_paths": ", ".join(
            str(path) for path in kicad_bundled_python_candidates(platform)
        ),
        "java_bin": "java",
    }

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SKIP_CLASS_SUFFIX = "__CP_SKIP"
UNCLASSED_SKIP_CLASS = f"cp_unclassed{SKIP_CLASS_SUFFIX}"
SKIP_PIN_NET_PREFIX = "CP_SKIP_PIN_"
KICAD_DEFAULT_CLASS = "kicad_default"
# DSN coordinates are 0.1 um; a KiCad -> DSN -> SES -> KiCad round trip
# can move a point by up to ~100 nm. Anything past this is real motion.
COPPER_MATCH_TOLERANCE_NM = 500


def split_name_list(values: Optional[Iterable[str]]) -> List[str]:
    """Flatten ``["A,B", "C"]`` into ``["A", "B", "C"]`` keeping order."""
    out: List[str] = []
    for value in values or []:
        for part in str(value).split(","):
            name = part.strip()
            if name and name not in out:
                out.append(name)
    return out


# ---------------------------------------------------------------------------
# Specctra DSN scanning
# ---------------------------------------------------------------------------


def _sexpr_end(text: str, start: int) -> int:
    """Return the index just past the ``)`` closing the ``(`` at start."""
    if text[start] != "(":
        raise ValueError(f"expected '(' at offset {start}")
    depth = 0
    index = start
    in_quote = False
    length = len(text)
    while index < length:
        char = text[index]
        if in_quote:
            if char == '"':
                in_quote = False
        elif char == '"':
            in_quote = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError("unbalanced parentheses in DSN")


def _children(text: str, start: int, end: int) -> List[Tuple[int, int]]:
    """Direct child ``(...)`` spans of the block ``text[start:end]``."""
    spans: List[Tuple[int, int]] = []
    index = start + 1
    in_quote = False
    while index < end - 1:
        char = text[index]
        if in_quote:
            if char == '"':
                in_quote = False
            index += 1
            continue
        if char == '"':
            in_quote = True
            index += 1
            continue
        if char == "(":
            child_end = _sexpr_end(text, index)
            spans.append((index, child_end))
            index = child_end
            continue
        index += 1
    return spans


_TOKEN = re.compile(r'"[^"]*"|[^\s()"]+')


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]
    return token


def _quote_like(raw: str, name: str) -> str:
    if raw.startswith('"') or re.search(r'[\s()"]', name):
        return f'"{name}"'
    return name


@dataclass
class DsnNet:
    name: str
    raw: str
    pins: List[str]  # raw pin tokens
    span: Tuple[int, int]

    @property
    def pin_count(self) -> int:
        return len(self.pins)


@dataclass
class DsnClass:
    name: str
    raw_name: str
    nets: List[Tuple[str, str]]  # (name, raw token)
    body: str
    span: Tuple[int, int]


@dataclass
class DsnNetwork:
    span: Tuple[int, int]
    nets: List[DsnNet]
    classes: List[DsnClass]


def _head(text: str, start: int, end: int) -> Tuple[str, List[str], int]:
    """Keyword, header tokens, and offset of first nested ``(``."""
    inner_start = start + 1
    index = inner_start
    in_quote = False
    while index < end - 1:
        char = text[index]
        if in_quote:
            if char == '"':
                in_quote = False
        elif char == '"':
            in_quote = True
        elif char == "(":
            break
        index += 1
    tokens = _TOKEN.findall(text[inner_start:index])
    keyword = tokens[0] if tokens else ""
    return keyword, tokens[1:], index


def parse_dsn_network(dsn_text: str) -> DsnNetwork:
    """Locate ``(network ...)`` and read its nets and classes."""
    match = re.search(r"\(network\b", dsn_text)
    if match is None:
        raise ValueError("DSN has no (network ...) section")
    start = match.start()
    end = _sexpr_end(dsn_text, start)
    nets: List[DsnNet] = []
    classes: List[DsnClass] = []
    for child_start, child_end in _children(dsn_text, start, end):
        keyword, tokens, nested = _head(dsn_text, child_start, child_end)
        if keyword == "net" and tokens:
            pins: List[str] = []
            for sub_start, sub_end in _children(
                dsn_text, child_start, child_end
            ):
                sub_kw, sub_tokens, _ = _head(dsn_text, sub_start, sub_end)
                if sub_kw == "pins":
                    pins.extend(sub_tokens)
            nets.append(
                DsnNet(
                    name=_unquote(tokens[0]),
                    raw=tokens[0],
                    pins=pins,
                    span=(child_start, child_end),
                )
            )
        elif keyword == "class" and tokens:
            body = dsn_text[nested : child_end - 1].strip()
            classes.append(
                DsnClass(
                    name=_unquote(tokens[0]),
                    raw_name=tokens[0],
                    nets=[(_unquote(tok), tok) for tok in tokens[1:]],
                    body=body,
                    span=(child_start, child_end),
                )
            )
    return DsnNetwork(span=(start, end), nets=nets, classes=classes)


@dataclass
class NetGroupPlan:
    """Result of restricting a DSN to one net group."""

    dsn_text: str
    target_nets: List[str]
    target_classes: List[str]
    skip_classes: List[str]
    skipped_net_count: int
    single_pin_targets: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_nets": list(self.target_nets),
            "target_classes": list(self.target_classes),
            "skip_classes": list(self.skip_classes),
            "skipped_net_count": self.skipped_net_count,
            "single_pin_targets": list(self.single_pin_targets),
        }


def _format_class(raw_name: str, raw_nets: Sequence[str], body: str) -> str:
    lines = [f"(class {raw_name}"]
    for index in range(0, len(raw_nets), 8):
        lines.append("      " + " ".join(raw_nets[index : index + 8]))
    if body:
        lines.append("      " + body)
    return "\n".join(lines) + "\n    )"


def _resolve_class_name(requested: str, names: Sequence[str]) -> Optional[str]:
    if requested in names:
        return requested
    if requested.lower() == "default" and KICAD_DEFAULT_CLASS in names:
        return KICAD_DEFAULT_CLASS
    lowered = {name.lower(): name for name in names}
    return lowered.get(requested.lower())


def _suggest(name: str, known: Sequence[str], limit: int = 5) -> List[str]:
    needle = name.lower().strip("/")
    hits = [k for k in known if needle and needle in k.lower()]
    return hits[:limit]


def restrict_dsn_to_nets(
    dsn_text: str,
    target_nets: Sequence[str] = (),
    target_classes: Sequence[str] = (),
    exclude_classes: Sequence[str] = (),
) -> NetGroupPlan:
    """Rewrite a DSN so FreeRouting routes only the target nets.

    The group is ``target_nets`` plus every net of ``target_classes``;
    with neither given it is every net. Nets of ``exclude_classes`` are
    then removed from it. Every other net loses its pins to one-pin
    ``CP_SKIP_PIN_<n>`` nets, and all of them move into
    ``<class>__CP_SKIP`` (same circuit and rule body as their class).
    Existing wiring is untouched; KiCad exports it as fixed/protected so
    FreeRouting routes around it. Raises ``ValueError`` for unknown
    nets/classes or an empty group.
    """
    network = parse_dsn_network(dsn_text)
    known_nets = [net.name for net in network.nets]
    for klass in network.classes:
        for name, _raw in klass.nets:
            if name not in known_nets:
                known_nets.append(name)
    class_names = [klass.name for klass in network.classes]

    def resolve_classes(requested_names: Sequence[str]) -> List[str]:
        resolved_names: List[str] = []
        for requested in split_name_list(requested_names):
            resolved = _resolve_class_name(requested, class_names)
            if resolved is None:
                raise ValueError(
                    f"Unknown net class {requested!r}. DSN classes: "
                    f"{', '.join(class_names) or '(none)'}"
                )
            if resolved not in resolved_names:
                resolved_names.append(resolved)
        return resolved_names

    resolved_classes = resolve_classes(target_classes)
    excluded_classes = resolve_classes(exclude_classes)

    targets: List[str] = []
    unknown: List[str] = []
    for name in split_name_list(target_nets):
        if name in known_nets:
            if name not in targets:
                targets.append(name)
        else:
            unknown.append(name)
    if unknown:
        hints = []
        for name in unknown:
            close = _suggest(name, known_nets)
            hints.append(
                f"{name!r}" + (f" (did you mean {close})" if close else "")
            )
        raise ValueError(
            "Unknown net(s) for --nets: "
            + "; ".join(hints)
            + ". Use the exact KiCad net names from list_nets."
        )
    for klass in network.classes:
        if klass.name in resolved_classes:
            for name, _raw in klass.nets:
                if name not in targets:
                    targets.append(name)
    if not split_name_list(target_nets) and not resolved_classes:
        targets = list(known_nets)
    excluded = {
        name
        for klass in network.classes
        if klass.name in excluded_classes
        for name, _raw in klass.nets
    }
    targets = [name for name in targets if name not in excluded]
    if not targets:
        raise ValueError(
            "Net group is empty: pass --nets and/or --net-classes "
            "(and do not exclude every target with --ignore-net-class)."
        )

    target_set = set(targets)
    for name in targets:
        if "," in name:
            raise ValueError(f"Net name {name!r} contains ',' (unsupported).")

    # Non-target nets: keep the declaration (wiring and planes refer to
    # it by name) but hand each pin its own one-pin net.
    replacements: List[Tuple[Tuple[int, int], str]] = []
    pin_nets: Dict[str, List[str]] = {}
    counter = 0
    for net in network.nets:
        if net.name in target_set:
            continue
        own: List[str] = []
        lines = [f"(net {net.raw})"]
        for pin in net.pins:
            counter += 1
            pin_net = f"{SKIP_PIN_NET_PREFIX}{counter}"
            own.append(pin_net)
            lines.append(f"(net {pin_net} (pins {pin}))")
        pin_nets[net.name] = own
        replacements.append((net.span, "\n    ".join(lines)))

    skip_classes: List[str] = []
    skipped = 0
    classed: set = set()
    for klass in network.classes:
        keep = [raw for name, raw in klass.nets if name in target_set]
        skip: List[str] = []
        for name, raw in klass.nets:
            if name not in target_set:
                skip.append(raw)
                skip.extend(pin_nets.get(name, []))
                skipped += 1
        classed.update(name for name, _raw in klass.nets)
        blocks: List[str] = []
        if keep:
            blocks.append(_format_class(klass.raw_name, keep, klass.body))
        if skip:
            clone = f"{klass.name}{SKIP_CLASS_SUFFIX}"
            if "," in clone:
                raise ValueError(
                    f"Net class {klass.name!r} contains ',' and cannot be "
                    "passed to FreeRouting -inc."
                )
            blocks.append(
                _format_class(
                    _quote_like(klass.raw_name, clone), skip, klass.body
                )
            )
            if clone not in skip_classes:
                skip_classes.append(clone)
        replacements.append((klass.span, "\n    ".join(blocks)))

    unclassed: List[str] = []
    for net in network.nets:
        if net.name in classed or net.name in target_set:
            continue
        unclassed.append(net.raw)
        unclassed.extend(pin_nets.get(net.name, []))
        skipped += 1

    pieces: List[str] = []
    cursor = 0
    for (span_start, span_end), text in sorted(replacements):
        pieces.append(dsn_text[cursor:span_start])
        pieces.append(text)
        cursor = span_end
    insert_at = network.span[1] - 1
    pieces.append(dsn_text[cursor:insert_at])
    if unclassed:
        pieces.append(
            "  " + _format_class(UNCLASSED_SKIP_CLASS, unclassed, "") + "\n  "
        )
        skip_classes.append(UNCLASSED_SKIP_CLASS)
    pieces.append(dsn_text[insert_at:])

    pin_counts = {net.name: net.pin_count for net in network.nets}
    single_pin = [name for name in targets if pin_counts.get(name, 0) < 2]
    warnings: List[str] = []
    if single_pin:
        warnings.append(
            "Target net(s) with fewer than 2 pins need no routing: "
            + ", ".join(single_pin)
        )
    return NetGroupPlan(
        dsn_text="".join(pieces),
        target_nets=targets,
        target_classes=resolved_classes,
        skip_classes=skip_classes,
        skipped_net_count=skipped,
        single_pin_targets=single_pin,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Copper snapshots (records are plain dicts so comparisons are testable)
# ---------------------------------------------------------------------------


def _xy(point: Any) -> Tuple[int, int]:
    return int(point.x), int(point.y)


def snapshot_board_copper(board: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Tracks, arcs and vias per net name from a pcbnew BOARD.

    Each record keeps the live pcbnew item under ``_item`` so matched
    items can be snapped back after the SES round trip.
    """
    out: Dict[str, List[Dict[str, Any]]] = {}
    for item in board.GetTracks():
        kind_name = item.GetClass()
        record: Dict[str, Any] = {"_item": item}
        if kind_name == "PCB_VIA":
            record["kind"] = "via"
            record["at"] = _xy(item.GetPosition())
            try:  # KiCad 9+: per-layer via width; no-arg form asserts
                record["width"] = int(item.GetWidth(item.TopLayer()))
            except TypeError:
                record["width"] = int(item.GetWidth())
            record["drill"] = int(item.GetDrillValue())
            record["layer"] = f"{item.TopLayer()}-{item.BottomLayer()}"
        else:
            record["kind"] = "arc" if kind_name == "PCB_ARC" else "track"
            record["start"] = _xy(item.GetStart())
            record["end"] = _xy(item.GetEnd())
            if record["kind"] == "arc":
                record["mid"] = _xy(item.GetMid())
            record["width"] = int(item.GetWidth())
            record["layer"] = item.GetLayerName()
        try:
            record["length_nm"] = float(item.GetLength())
        except Exception:  # noqa: BLE001 - length is informational
            record["length_nm"] = 0.0
        out.setdefault(item.GetNetname(), []).append(record)
    return out


def _close(a: Tuple[int, int], b: Tuple[int, int], tol: int) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def _records_match(a: Dict[str, Any], b: Dict[str, Any], tol: int) -> bool:
    if a.get("kind") != b.get("kind") or a.get("layer") != b.get("layer"):
        return False
    if abs(int(a.get("width", 0)) - int(b.get("width", 0))) > tol:
        return False
    if a["kind"] == "via":
        return abs(
            int(a.get("drill", 0)) - int(b.get("drill", 0))
        ) <= tol and (_close(a["at"], b["at"], tol))
    same = _close(a["start"], b["start"], tol) and _close(
        a["end"], b["end"], tol
    )
    flipped = _close(a["start"], b["end"], tol) and _close(
        a["end"], b["start"], tol
    )
    if not (same or flipped):
        return False
    if a["kind"] == "arc":
        return _close(a.get("mid", (0, 0)), b.get("mid", (0, 0)), tol)
    return True


def match_copper(
    before: Sequence[Dict[str, Any]],
    after: Sequence[Dict[str, Any]],
    tol: int = COPPER_MATCH_TOLERANCE_NM,
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """Pair before/after items. Returns (pairs, missing, added) indexes."""
    used: set = set()
    pairs: List[Tuple[int, int]] = []
    missing: List[int] = []
    for b_index, record in enumerate(before):
        found = None
        for a_index, candidate in enumerate(after):
            if a_index in used:
                continue
            if _records_match(record, candidate, tol):
                found = a_index
                break
        if found is None:
            missing.append(b_index)
        else:
            used.add(found)
            pairs.append((b_index, found))
    added = [index for index in range(len(after)) if index not in used]
    return pairs, missing, added


def _public(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if not key.startswith("_") and key != "length_nm"
    }


def compare_copper(
    before: Dict[str, List[Dict[str, Any]]],
    after: Dict[str, List[Dict[str, Any]]],
    target_nets: Iterable[str],
    tol: int = COPPER_MATCH_TOLERANCE_NM,
) -> Dict[str, Any]:
    """Check non-target copper is unchanged and target copper only grew.

    ``pairs`` holds matched (before_record, after_record) tuples for
    every net so callers can snap round-trip drift back; ``duplicates``
    holds after-records that only repeat already matched copper.
    """
    targets = set(target_nets)
    changed: Dict[str, Any] = {}
    target_removed: Dict[str, int] = {}
    target_added: Dict[str, int] = {}
    pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    duplicates: List[Dict[str, Any]] = []
    for net in sorted(set(before) | set(after)):
        b_items = before.get(net, [])
        a_items = after.get(net, [])
        matched, missing, added = match_copper(b_items, a_items, tol)
        pairs.extend((b_items[i], a_items[j]) for i, j in matched)
        # FreeRouting can echo a protected wire twice in the SES (once
        # merged into a longer path, once as itself). A copy of an item
        # that is already matched is not new copper; drop it.
        kept_after = [a_items[j] for _i, j in matched]
        still_added: List[int] = []
        for index in added:
            if any(_records_match(a_items[index], k, tol) for k in kept_after):
                duplicates.append(a_items[index])
            else:
                still_added.append(index)
        added = still_added
        if net in targets:
            if missing:
                target_removed[net] = len(missing)
            if added:
                target_added[net] = len(added)
            continue
        if missing or added:
            changed[net] = {
                "missing": len(missing),
                "added": len(added),
                "examples_missing": [_public(b_items[i]) for i in missing[:3]],
                "examples_added": [_public(a_items[i]) for i in added[:3]],
            }
    return {
        "status": "changed" if changed else "unchanged",
        "changed_nets": changed,
        "target_items_added": target_added,
        "target_items_removed": target_removed,
        "duplicate_items": len(duplicates),
        "pairs": pairs,
        "duplicates": duplicates,
    }


def snap_back_drift(
    pcbnew_mod: Any,
    pairs: Sequence[Tuple[Dict[str, Any], Dict[str, Any]]],
) -> int:
    """Move matched after-items back onto their exact pre-route geometry."""
    moved = 0
    vector = getattr(pcbnew_mod, "VECTOR2I", None) or getattr(
        pcbnew_mod, "wxPoint"
    )
    for before, after in pairs:
        item = after.get("_item")
        if item is None:
            continue
        if before["kind"] == "via":
            if before["at"] != after["at"]:
                item.SetPosition(vector(*before["at"]))
                moved += 1
            continue
        if before["start"] == after["start"] and before["end"] == after["end"]:
            continue
        item.SetStart(vector(*before["start"]))
        item.SetEnd(vector(*before["end"]))
        if before["kind"] == "arc" and "mid" in before:
            item.SetMid(vector(*before["mid"]))
        moved += 1
    return moved


def net_lengths(
    snapshot: Dict[str, List[Dict[str, Any]]],
    nets: Sequence[str],
) -> Dict[str, Any]:
    """Routed copper length (mm) and via count per net, plus max skew."""
    per_net: Dict[str, Any] = {}
    for net in nets:
        records = snapshot.get(net, [])
        layers: Dict[str, float] = {}
        vias = 0
        for record in records:
            if record["kind"] == "via":
                vias += 1
                continue
            layers[record["layer"]] = layers.get(record["layer"], 0.0) + float(
                record.get("length_nm") or 0.0
            )
        total = sum(layers.values())
        per_net[net] = {
            "track_length_mm": round(total / 1e6, 4),
            "by_layer_mm": {k: round(v / 1e6, 4) for k, v in layers.items()},
            "via_count": vias,
            "routed": bool(records),
        }
    lengths = [entry["track_length_mm"] for entry in per_net.values()]
    skew = round(max(lengths) - min(lengths), 4) if len(lengths) >= 2 else 0.0
    return {"nets": per_net, "max_skew_mm": skew}


# ---------------------------------------------------------------------------
# DRC deltas (kicad-cli JSON)
# ---------------------------------------------------------------------------


def _item_key(item: Dict[str, Any]) -> Tuple[str, float, float]:
    pos = item.get("pos") or {}
    return (
        str(item.get("description", "")),
        round(float(pos.get("x", 0.0)), 3),
        round(float(pos.get("y", 0.0)), 3),
    )


def _violation_key(violation: Dict[str, Any]) -> Tuple[Any, ...]:
    items = tuple(
        sorted(_item_key(item) for item in violation.get("items", []))
    )
    return (violation.get("type", ""), violation.get("severity", ""), items)


def _mentions(violation: Dict[str, Any], nets: Iterable[str]) -> List[str]:
    hits: List[str] = []
    descriptions = [
        str(i.get("description", "")) for i in violation.get("items", [])
    ]
    for net in nets:
        tag = f"[{net}]"
        if any(tag in text for text in descriptions):
            hits.append(net)
    return hits


def unconnected_by_net(
    drc: Optional[Dict[str, Any]], nets: Sequence[str]
) -> Dict[str, int]:
    counts = {net: 0 for net in nets}
    for item in (drc or {}).get("unconnected_items", []) or []:
        for net in _mentions(item, nets):
            counts[net] += 1
    return counts


def drc_delta(
    before: Optional[Dict[str, Any]],
    after: Optional[Dict[str, Any]],
    target_nets: Sequence[str],
) -> Dict[str, Any]:
    """New/resolved violations and target-net connectivity, before vs after."""
    before_v = Counter(
        _violation_key(v) for v in (before or {}).get("violations", [])
    )
    after_list = list((after or {}).get("violations", []))
    after_v = Counter(_violation_key(v) for v in after_list)
    new_items: List[Dict[str, Any]] = []
    remaining = before_v.copy()
    for violation in after_list:
        key = _violation_key(violation)
        if remaining.get(key, 0) > 0:
            remaining[key] -= 1
        else:
            new_items.append(violation)
    resolved = sum((before_v - after_v).values())
    new_errors = [v for v in new_items if v.get("severity") == "error"]
    new_warnings = [v for v in new_items if v.get("severity") != "error"]
    before_unc = unconnected_by_net(before, target_nets)
    after_unc = unconnected_by_net(after, target_nets)
    return {
        "new_errors": len(new_errors),
        "new_warnings": len(new_warnings),
        "resolved_violations": resolved,
        "new_violations": [
            {
                "type": v.get("type"),
                "severity": v.get("severity"),
                "description": v.get("description"),
                "items": [i.get("description") for i in v.get("items", [])],
            }
            for v in new_items[:20]
        ],
        "target_unconnected_before": sum(before_unc.values()),
        "target_unconnected_after": sum(after_unc.values()),
        "still_unconnected_nets": sorted(n for n, c in after_unc.items() if c),
        "connected_nets": sorted(n for n, c in after_unc.items() if not c),
    }


def judge_net_group_route(
    copper: Dict[str, Any],
    delta: Optional[Dict[str, Any]],
) -> Tuple[str, List[str]]:
    """Return ("kept" | "reverted", reasons)."""
    reasons: List[str] = []
    if copper.get("status") != "unchanged":
        reasons.append(
            "Copper outside the net group changed on "
            + ", ".join(sorted(copper.get("changed_nets", {})))
            + "; reverted to the pre-route board."
        )
    if copper.get("target_items_removed"):
        reasons.append(
            "Existing copper on target nets was removed: "
            + ", ".join(sorted(copper["target_items_removed"]))
            + "; reverted to the pre-route board."
        )
    if delta is not None:
        if delta["new_errors"]:
            reasons.append(
                f"Route introduced {delta['new_errors']} new DRC error(s); "
                "reverted to the pre-route board."
            )
        if (
            delta["target_unconnected_after"]
            > delta["target_unconnected_before"]
        ):
            reasons.append(
                "Route left more unconnected target connections "
                f"({delta['target_unconnected_before']} -> "
                f"{delta['target_unconnected_after']}); reverted."
            )
    return ("reverted" if reasons else "kept"), reasons

import contextlib
import dataclasses
import importlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

BoardUpdateStrategy = Literal["greedy", "global", "hybrid"]
ItemSelectionStrategy = Literal["sequential", "random", "prioritized"]
FreeRoutingLogLevel = Literal[
    "ALL",
    "CONFIG",
    "FINE",
    "FINER",
    "FINEST",
    "INFO",
    "OFF",
    "SEVERE",
    "WARNING",
]


# FreeRouting 2.2.4 only parses -de -di -do -dr -drc -mp -mt -oit -us -hr
# -is -l -dl -da -host -help -inc -dct -ll (plus --key=value settings).
# Older docs/skills used these; 2.2.4 silently ignores them.
DEAD_FREEROUTING_FLAGS: Dict[str, str] = {
    "-fo": "fanout",
    "-ap": "autorouter passes (use --max-passes, -mp)",
    "-pp": "post-route passes",
    "-im": "save intermediate",
    "-trace": "trace",
    "-test": "experimental",
}


@dataclass
class FreeRoutingOptions:
    """Structured FreeRouting 2.2.4 CLI options for headless autorouting."""

    headless: bool = True
    max_passes: Optional[int] = None
    threads: Optional[int] = None
    optimization_threshold: Optional[float] = None
    board_update_strategy: Optional[BoardUpdateStrategy] = None
    hybrid_ratio: Optional[float] = None
    item_selection_strategy: Optional[ItemSelectionStrategy] = None
    ignore_net_classes: List[str] = field(default_factory=list)
    rules_file: Optional[Path] = None
    language: Optional[str] = None
    dialog_timeout: Optional[int] = None
    disable_analytics: bool = False
    disable_logging: bool = False
    log_level: Optional[FreeRoutingLogLevel] = None
    extra_args: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "headless": self.headless,
            "disable_analytics": self.disable_analytics,
            "disable_logging": self.disable_logging,
            "ignore_net_classes": list(self.ignore_net_classes),
            "extra_args": list(self.extra_args),
        }
        if self.max_passes is not None:
            payload["max_passes"] = self.max_passes
        if self.threads is not None:
            payload["threads"] = self.threads
        if self.optimization_threshold is not None:
            payload["optimization_threshold"] = self.optimization_threshold
        if self.board_update_strategy is not None:
            payload["board_update_strategy"] = self.board_update_strategy
        if self.hybrid_ratio is not None:
            payload["hybrid_ratio"] = self.hybrid_ratio
        if self.item_selection_strategy is not None:
            payload["item_selection_strategy"] = self.item_selection_strategy
        if self.rules_file is not None:
            payload["rules_file"] = str(self.rules_file)
        if self.language is not None:
            payload["language"] = self.language
        if self.dialog_timeout is not None:
            payload["dialog_timeout"] = self.dialog_timeout
        if self.log_level is not None:
            payload["log_level"] = self.log_level
        return payload


def build_freerouting_command(
    *,
    java_bin: str,
    jar_path: Path,
    dsn_path: Path,
    ses_path: Path,
    options: Optional[FreeRoutingOptions] = None,
) -> Tuple[List[str], Dict[str, Any], List[str]]:
    """Compose the FreeRouting Java command.

    Returns cmd, options payload, and warnings.
    """
    opts = options or FreeRoutingOptions()
    warnings: List[str] = []
    cmd: List[str] = [java_bin]

    if opts.headless:
        cmd.append("-Djava.awt.headless=true")

    cmd.extend(["-jar", str(jar_path)])

    if opts.headless:
        cmd.append("--gui.enabled=false")

    cmd.extend(["-de", str(dsn_path)])

    if opts.rules_file is not None:
        cmd.extend(["-dr", str(opts.rules_file)])

    cmd.extend(["-do", str(ses_path)])

    extras, extra_warnings, extra_inc = sanitize_extra_freerouting_args(
        opts.extra_args
    )
    warnings.extend(extra_warnings)

    if opts.max_passes is not None:
        cmd.extend(["-mp", str(opts.max_passes)])

    if opts.threads is not None:
        cmd.extend(["-mt", str(opts.threads)])

    if opts.optimization_threshold is not None:
        cmd.extend(["-oit", str(opts.optimization_threshold)])

    if opts.board_update_strategy is not None:
        cmd.extend(["-us", opts.board_update_strategy])

    if opts.hybrid_ratio is not None:
        cmd.extend(["-hr", str(opts.hybrid_ratio)])

    if opts.item_selection_strategy is not None:
        cmd.extend(["-is", opts.item_selection_strategy])

    # -inc takes ONE comma-separated list; a second -inc replaces the first.
    ignored = split_name_list(list(opts.ignore_net_classes) + extra_inc)
    if ignored:
        cmd.extend(["-inc", ",".join(ignored)])

    if opts.language is not None:
        cmd.extend(["-l", opts.language])

    if opts.dialog_timeout is not None:
        cmd.extend(["-dct", str(opts.dialog_timeout)])

    if opts.disable_analytics:
        cmd.append("-da")

    if opts.disable_logging:
        cmd.append("-dl")

    if opts.log_level is not None:
        cmd.extend(["-ll", opts.log_level])

    cmd.extend(extras)

    return cmd, opts.to_dict(), warnings


_PROTECTED_EXTRA_FLAGS = ("-dr", "--rules-file")


def sanitize_extra_freerouting_args(
    extras: Optional[Sequence[str]],
) -> Tuple[List[str], List[str], List[str]]:
    """Filter JAR passthrough tokens.

    Drops protected physical-rule flags and flags FreeRouting 2.2.4 does
    not parse, and pulls ``-inc`` values out so the command carries one
    merged ``-inc``. Returns (allowed, warnings, extra -inc classes).
    """
    allowed: List[str] = []
    warnings: List[str] = []
    inc_classes: List[str] = []
    items = [str(item) for item in (extras or [])]
    skip_next = False

    def value_follows(index: int) -> bool:
        return index + 1 < len(items) and not items[index + 1].startswith("-")

    for index, token in enumerate(items):
        if skip_next:
            skip_next = False
            continue
        lowered = token.lower()
        blocked = any(
            lowered == flag or lowered.startswith(f"{flag}=")
            for flag in _PROTECTED_EXTRA_FLAGS
        )
        if blocked:
            warnings.append(
                "Dropped protected extra FreeRouting arg "
                f"{token!r}; use named --rules-file only after "
                "ask_user_question (physical constraints)."
            )
            if "=" not in token and value_follows(index):
                skip_next = True
            continue
        if lowered == "-inc":
            if value_follows(index):
                inc_classes.extend(split_name_list([items[index + 1]]))
                skip_next = True
            warnings.append(
                "Merged extra -inc into the single -inc list; prefer "
                "--ignore-net-class."
            )
            continue
        if lowered in DEAD_FREEROUTING_FLAGS:
            warnings.append(
                f"Dropped extra FreeRouting arg {token!r} "
                f"({DEAD_FREEROUTING_FLAGS[lowered]}): FreeRouting 2.2.4 "
                "does not support it."
            )
            if lowered in ("-ap", "-pp") and value_follows(index):
                skip_next = True
            continue
        allowed.append(token)
    return allowed, warnings, inc_classes


class FreeRoutingError(RuntimeError):
    """FreeRouting failed; ``summary`` keeps command, tails, telemetry."""

    def __init__(self, message: str, summary: Dict[str, Any]):
        super().__init__(message)
        self.summary = summary


def _score_detail(detail: Optional[str]) -> Tuple[int, int]:
    """Read "(3 unrouted and 24 violations)" style score annotations."""
    text = detail or ""
    unrouted = re.search(r"(\d+) unrouted", text)
    violations = re.search(r"(\d+) violations?", text)
    return (
        int(unrouted.group(1)) if unrouted else 0,
        int(violations.group(1)) if violations else 0,
    )


def parse_freerouting_stdout(stdout_text: str) -> Dict[str, Any]:
    """Extract pass/score/unrouted metrics from FreeRouting INFO stdout."""
    text = stdout_text or ""
    metrics: Dict[str, Any] = {
        "started_unrouted": None,
        "final_score": None,
        "final_unrouted": 0,
        "total_passes": 0,
        "cpu_seconds": None,
        "peak_heap_mb": None,
        "pass_history": [],
        "board_unchanged": False,
    }
    start_match = re.search(r"started with (\d+) unrouted nets", text)
    if start_match:
        metrics["started_unrouted"] = int(start_match.group(1))
    # Older builds: "pass #1 completed in 0.22 s, score of 655.84 (1 unrouted)"
    # 2.2.4: "pass #1 on board '<hash>' was completed in 0.19 seconds with
    # the score of 998.45 (1 unrouted and 24 violations), using ..."
    pass_matches = re.findall(
        r"pass #(\d+)(?: on board '[^']*' was)? completed in ([\d.]+) "
        r"s(?:econds)?,? (?:with the )?score of (\d+(?:\.\d+)?)"
        r"(?: \(([^)]*)\))?",
        text,
    )
    for p_num, p_time, p_score, p_detail in pass_matches:
        unrouted, violations = _score_detail(p_detail)
        metrics["pass_history"].append(
            {
                "pass": int(p_num),
                "time_sec": float(p_time),
                "score": float(p_score),
                "unrouted": unrouted,
                "violations": violations,
            }
        )
    final_match = re.search(
        r"finished after (\d+) passes, final score: ([\d.]+), using "
        r"([\d.]+) CPU seconds, ([\d.]+) MB peak heap",
        text,
    )
    if final_match:
        metrics["total_passes"] = int(final_match.group(1))
        metrics["final_score"] = float(final_match.group(2))
        metrics["cpu_seconds"] = float(final_match.group(3))
        metrics["peak_heap_mb"] = float(final_match.group(4))
    session_match = re.search(
        r"session completed: started with \d+ unrouted nets, completed in "
        r"[\d.]+ seconds, final score: (\d+(?:\.\d+)?)(?: \(([^)]*)\))?, "
        r"using ([\d.]+) total CPU seconds, [\d.]+ GB total allocated, "
        r"and ([\d.]+) MB peak heap",
        text,
    )
    if session_match:
        metrics["total_passes"] = len(metrics["pass_history"])
        metrics["final_score"] = float(session_match.group(1))
        metrics["cpu_seconds"] = float(session_match.group(3))
        metrics["peak_heap_mb"] = float(session_match.group(4))
        unrouted, violations = _score_detail(session_match.group(2))
        metrics["final_unrouted"] = unrouted
        metrics["final_violations"] = violations
    elif metrics["pass_history"]:
        metrics["final_unrouted"] = metrics["pass_history"][-1]["unrouted"]
    elif metrics["started_unrouted"] is not None:
        metrics["final_unrouted"] = metrics["started_unrouted"]
    if re.search(r"Board state has not changed since pass", text):
        metrics["board_unchanged"] = True
    return metrics


def _decode_captured(blob: Any) -> str:
    if blob is None:
        return ""
    if isinstance(blob, bytes):
        return blob.decode("utf-8", errors="replace")
    return str(blob)


def _freerouting_proc_summary(
    *,
    cmd: List[str],
    options_payload: Dict[str, Any],
    option_warnings: List[str],
    returncode: Optional[int],
    stdout_text: str,
    stderr_text: str,
    elapsed: float,
) -> Dict[str, Any]:
    telemetry = parse_freerouting_stdout(stdout_text)
    return {
        "command": cmd,
        "freerouting_options": options_payload,
        "option_warnings": option_warnings,
        "returncode": returncode,
        "stdout_tail": (stdout_text or "")[-4000:],
        "stderr_tail": (stderr_text or "")[-4000:],
        "elapsed_sec": elapsed,
        "freerouting_telemetry": telemetry,
    }


def build_next_actions(
    telemetry: Optional[Dict[str, Any]] = None,
    *,
    timed_out: bool = False,
) -> List[str]:
    """Suggest allowed retunes; never auto-relax KiCad geometry."""
    tel = telemetry or {}
    history: List[Dict[str, Any]] = list(tel.get("pass_history") or [])
    final_unrouted = int(tel.get("final_unrouted") or 0)
    final_score = tel.get("final_score")
    actions: List[str] = [
        "Java exit 0 / status routed means SES imported or the process "
        "finished, not 100% connected. Inspect freerouting_telemetry, "
        "then run run_drc and list_nets.",
    ]
    if timed_out:
        actions.append(
            "Subprocess --timeout-sec elapsed. Re-run with a larger "
            "--timeout-sec and/or fewer --max-passes, or route a smaller "
            "--nets group; keep headless."
        )
    scores = [float(item.get("score") or 0) for item in history]
    if final_unrouted > 0 and (
        tel.get("board_unchanged")
        or (final_score is not None and float(final_score) <= 0.01)
    ):
        actions.append(
            "Telemetry looks geometrically infeasible (score ~0 or board "
            "unchanged with nets unrouted). If earlier groups' copper "
            "blocks this group, unroute_pcb_net the blocker and route the "
            "stuck nets first; otherwise stop mutating. RCA then "
            "ask_user_question with DFM-backed numbers. Do not silently "
            "enlarge Edge.Cuts or relax KiCad rules."
        )
    elif len(scores) >= 3:
        oscillating = False
        for index in range(2, len(scores)):
            if (
                abs(scores[index] - scores[index - 2]) < 1.0
                and abs(scores[index] - scores[index - 1]) > 20
            ):
                oscillating = True
                break
        rising = all(
            scores[index] + 0.01 >= scores[index - 1]
            for index in range(1, len(scores))
        )
        if oscillating and final_unrouted > 0:
            actions.append(
                "Score oscillation / rip-up thrashing: retry with "
                "--item-selection-strategy random. Engine-only extras "
                "(via/ripup costs) are allowed if the JAR accepts them."
            )
        elif rising and final_unrouted > 0:
            actions.append(
                "Pass starvation: score still rising with unrouted nets. "
                "Increase --max-passes and --timeout-sec."
            )
        elif (
            final_unrouted > 0
            and len(set(round(s, 1) for s in scores[-3:])) == 1
        ):
            actions.append(
                "Early plateau on incomplete routing: unroute_pcb_net the "
                "blocking partial routes and re-route that net group, or "
                "re-order groups (route the stuck nets first)."
            )
    if final_unrouted == 0 and history:
        actions.append(
            "Telemetry shows 0 unrouted nets. If DRC still fails, "
            "unroute_pcb_net the offending net and re-route it with "
            "--nets; do not invent copper."
        )
    elif final_unrouted > 0:
        actions.append(
            "Retune allowed flags in order: --max-passes/--timeout-sec, "
            "then optimizer strategy (-us/-is/-hr) and --threads, then "
            "a smaller --nets group or a different group order."
        )
    actions.append(
        "Do not relax KiCad rules, --rules-file, Edge.Cuts, stackup, or "
        "via/track geometry as a routing lever without exhausted "
        "hyperparameter retries, RCA, DFM evidence, and ask_user_question."
    )
    return actions


@dataclass
class AutorouteResult:
    status: str
    pcb_path: str
    dsn_path: str
    ses_path: str
    jar_path: str
    output_pcb_path: str
    segment_count_before: int
    segment_count_after: int
    timings_sec: Dict[str, float] = field(default_factory=dict)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    native_stdout_tail: Optional[str] = None
    native_stderr_tail: Optional[str] = None
    drc_summary: Optional[Dict[str, Any]] = None
    refill_zones: Optional[Dict[str, Any]] = None
    freerouting_telemetry: Optional[Dict[str, Any]] = None
    next_actions: List[str] = field(default_factory=list)
    net_group: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "status": self.status,
            "pcb_path": self.pcb_path,
            "dsn_path": self.dsn_path,
            "ses_path": self.ses_path,
            "jar_path": self.jar_path,
            "output_pcb_path": self.output_pcb_path,
            "segment_count_before": self.segment_count_before,
            "segment_count_after": self.segment_count_after,
            "timings_sec": self.timings_sec,
            "commands": self.commands,
            "warnings": self.warnings,
            "notes": self.notes,
            "next_actions": list(self.next_actions),
        }
        if self.native_stdout_tail:
            payload["native_stdout_tail"] = self.native_stdout_tail
        if self.native_stderr_tail:
            payload["native_stderr_tail"] = self.native_stderr_tail
        if self.drc_summary is not None:
            payload["drc_summary"] = self.drc_summary
        if self.refill_zones is not None:
            payload["refill_zones"] = self.refill_zones
        if self.freerouting_telemetry is not None:
            payload["freerouting_telemetry"] = self.freerouting_telemetry
        if self.net_group is not None:
            payload["net_group"] = self.net_group
        if self.error is not None:
            payload["error"] = self.error
        return payload


def count_pcb_segments(pcb_path: Path) -> int:
    text = pcb_path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^\s*\(segment\b", text, flags=re.MULTILINE))


def _prepend_sys_paths(candidates: Sequence[Path]) -> List[str]:
    added: List[str] = []
    for candidate in candidates:
        path_str = str(candidate.expanduser())
        if path_str not in sys.path and candidate.exists():
            sys.path.insert(0, path_str)
            added.append(path_str)
    return added


def import_pcbnew(platform: Platform) -> Tuple[Any, List[str], List[str]]:
    """Import pcbnew, probing platform-specific KiCad Python paths first."""
    tried: List[str] = []
    warnings: List[str] = []
    first_error: Optional[ImportError] = None

    _prepend_sys_paths(pcbnew_sys_path_candidates(platform))
    tried.extend(str(path) for path in pcbnew_sys_path_candidates(platform))

    try:
        return importlib.import_module("pcbnew"), tried, warnings
    except ImportError as exc:
        first_error = exc
        warnings.append(f"Initial pcbnew import failed: {exc}")

    # Some installs only expose pcbnew when launched with KiCad's
    # bundled python.
    for candidate in pcbnew_sys_path_candidates(platform):
        if not candidate.exists():
            continue
        warnings.append(
            "pcbnew is not importable from the current Python interpreter. "
            "Run this skill with KiCad's bundled Python when available."
        )
        break

    guidance = (
        "KiCad pcbnew module is unavailable. Install KiCad and run this "
        "script with KiCad's bundled Python, or set "
        "KICAD_PYTHON_SITE_PACKAGES to the "
        "directory containing pcbnew. Do not pip install pcbnew. "
        "KiCad 10 removed `kicad-cli pcb export specctradsn`; use "
        "pcbnew.ExportSpecctraDSN instead."
    )
    raise RuntimeError(guidance) from first_error


def _python_can_import_pcbnew(
    python_executable: Path,
    platform: Platform,
) -> Tuple[bool, str]:
    """Return whether a Python executable can import pcbnew."""
    if not python_executable.is_file():
        return False, "executable not found"

    site_paths = [
        str(path.expanduser())
        for path in pcbnew_sys_path_candidates(platform)
        if path.exists()
    ]
    probe = (
        "import importlib, sys\n"
        f"paths = {site_paths!r}\n"
        "for path in paths:\n"
        "    if path not in sys.path:\n"
        "        sys.path.insert(0, path)\n"
        "importlib.import_module('pcbnew')\n"
        "print('ok')\n"
    )
    proc = subprocess.run(
        [str(python_executable), "-c", probe],
        capture_output=True,
        text=True,
        timeout=20,
    )
    if proc.returncode == 0 and "ok" in proc.stdout:
        return True, "import ok"
    detail = (proc.stderr or proc.stdout or "import failed").strip()
    return False, detail[-500:]


def discover_recommended_python(
    platform: Platform,
) -> Tuple[Optional[Path], List[Dict[str, str]]]:
    """Find the first KiCad bundled Python that can import pcbnew."""
    probes: List[Dict[str, str]] = []
    for candidate in kicad_bundled_python_candidates(platform):
        ok, detail = _python_can_import_pcbnew(candidate, platform)
        probes.append(
            {
                "python": str(candidate),
                "available": str(ok).lower(),
                "detail": detail,
            }
        )
        if ok:
            return candidate, probes
    return None, probes


def _diagnose_guidance_notes(
    *,
    platform: Platform,
    pcbnew_ok: bool,
    recommended_python: Optional[Path],
) -> List[str]:
    notes = [
        "Run route only after Java and KiCad pcbnew are available.",
        "Use fill_pcb_zones after importing SES routes.",
        "KiCad 10 removed `kicad-cli pcb export specctradsn`; this skill uses "
        "pcbnew.ExportSpecctraDSN and pcbnew.ImportSpecctraSES.",
    ]
    if not pcbnew_ok:
        notes.append(
            "The current Python interpreter cannot import pcbnew. "
            "Run diagnose first and use recommended_python when provided."
        )
        if platform == "mac" and recommended_python is not None:
            notes.append(
                "On macOS, prefer KiCad bundled Python at "
                f"{recommended_python}."
            )
    return notes


def tail_text(text: str, limit: int = 4000) -> str:
    if not text:
        return ""
    return text[-limit:]


@contextlib.contextmanager
def capture_native_streams():
    """Capture native stdout/stderr emitted during pcbnew operations."""
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    with contextlib.redirect_stdout(
        stdout_capture
    ), contextlib.redirect_stderr(stderr_capture):
        yield stdout_capture, stderr_capture


_JAVA_VERSION = re.compile(r'version "(?:1\.)?(\d+)')


def resolve_java_bin(java_bin: str = "java") -> str:
    """Prefer CopperPilot's managed Java when the caller left the default."""
    explicit = (java_bin or "").strip() or "java"
    if explicit != "java":
        return explicit
    managed = os.environ.get("COPPERPILOT_JAVA", "").strip()
    return managed or "java"


def java_major_from_output(text: str) -> Optional[int]:
    match = _JAVA_VERSION.search(text or "")
    if not match:
        return None
    return int(match.group(1))


def ensure_java(java_bin: str = "java") -> str:
    java_bin = resolve_java_bin(java_bin)
    resolved = shutil.which(java_bin) or java_bin
    proc = subprocess.run(
        [resolved, "-version"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Java runtime check failed for '{java_bin}'. "
            f"Java {MIN_JAVA_MAJOR}+ is required."
        )
    major = java_major_from_output((proc.stderr or "") + (proc.stdout or ""))
    if major is None or major < MIN_JAVA_MAJOR:
        found = "unknown" if major is None else str(major)
        raise RuntimeError(
            f"Java {MIN_JAVA_MAJOR}+ is required (found {found}) "
            f"for '{resolved}'. {java_install_hint()}"
        )
    return resolved


def java_install_hint() -> str:
    """What the user must do; what the agent must not do instead.

    A benchmark agent on a CLI machine with Java 21 lowered this skill's
    version check, then hand-routed the board with pcbnew scripts.
    """
    return (
        f"Install a Java {MIN_JAVA_MAJOR} runtime (for example Eclipse "
        f"Temurin {MIN_JAVA_MAJOR}: https://adoptium.net/temurin/releases/"
        f"?version={MIN_JAVA_MAJOR}), or open the CopperPilot desktop app "
        "once (its setup installs it), then run diagnose again or pass "
        "--java-bin with its path. Agent: stop here and tell the user; do "
        "not edit this skill, lower the version check, or route by hand."
    )


def _validate_downloaded_jar(dest: Path, url: str) -> None:
    if not dest.is_file() or dest.stat().st_size == 0:
        raise RuntimeError(
            f"Downloaded FreeRouting JAR from {url} was empty or missing."
        )


def _download_jar_with_urllib(
    dest: Path,
    *,
    url: str,
    timeout_sec: int,
) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "CopperPilot-KiCad-Autorouter/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout_sec) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"Downloaded FreeRouting JAR from {url} was empty.")
    dest.write_bytes(data)


def _download_jar_with_curl(
    dest: Path,
    *,
    url: str,
    timeout_sec: int,
) -> None:
    curl = shutil.which("curl")
    if curl is None:
        raise RuntimeError("curl is not available on PATH")
    proc = subprocess.run(
        [
            curl,
            "-L",
            "--fail",
            "--silent",
            "--show-error",
            "--output",
            str(dest),
            url,
        ],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"curl download failed with exit code {proc.returncode}: "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )


def _download_jar_with_wget(
    dest: Path,
    *,
    url: str,
    timeout_sec: int,
) -> None:
    wget = shutil.which("wget")
    if wget is None:
        raise RuntimeError("wget is not available on PATH")
    proc = subprocess.run(
        [wget, "-O", str(dest), url],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"wget download failed with exit code {proc.returncode}: "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )


def download_freerouting_jar(
    dest: Path,
    *,
    url: str,
    timeout_sec: int = 120,
) -> Tuple[Path, Optional[str]]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest, None

    errors: List[str] = []
    for downloader_name, downloader in (
        ("urllib", _download_jar_with_urllib),
        ("curl", _download_jar_with_curl),
        ("wget", _download_jar_with_wget),
    ):
        try:
            if dest.exists():
                dest.unlink()
            downloader(dest, url=url, timeout_sec=timeout_sec)
            _validate_downloaded_jar(dest, url)
            return dest, downloader_name
        except Exception as exc:  # noqa: BLE001 - try next downloader
            errors.append(f"{downloader_name}: {exc}")
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass

    raise RuntimeError(
        f"Failed to download FreeRouting JAR from {url}. "
        f"Tried urllib, curl, and wget. Details: {' | '.join(errors)}"
    )


def discover_kicad_cli(
    platform: Platform,
    explicit_path: Optional[str] = None,
) -> str:
    if explicit_path:
        return explicit_path
    for candidate in kicad_cli_candidates(platform):
        path = Path(candidate)
        if path.is_file():
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError(
        "kicad-cli not found. Install KiCad or pass "
        "--kicad-cli-path explicitly."
    )


def summarize_drc_report(drc_data: Dict[str, Any]) -> Dict[str, Any]:
    violations = drc_data.get("violations", [])
    errors = sum(1 for item in violations if item.get("severity") == "error")
    warnings = sum(
        1 for item in violations if item.get("severity") == "warning"
    )
    return {
        "report_type": "DRC",
        "total_violations": len(violations),
        "errors": errors,
        "warnings": warnings,
        "violations": violations,
        "kicad_version": drc_data.get("kicad_version", ""),
        "date": drc_data.get("date", ""),
        "unconnected_items": drc_data.get("unconnected_items", []),
    }


def run_kicad_cli_drc(
    *,
    platform: Platform,
    pcb_path: Path,
    project_dir: Path,
    cli_path: str,
    timeout_sec: int = 120,
    refill_zones: bool = False,
    label: str = "post-route",
) -> Dict[str, Any]:
    """Run kicad-cli DRC to JSON. ``refill_zones`` refills in memory only."""
    del platform
    drc_output = (
        default_skill_cache_dir(project_dir)
        / f"{pcb_path.stem}-{label}-drc.json"
    )
    drc_output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [cli_path, "pcb", "drc", "--format", "json"]
    if refill_zones:
        cmd.append("--refill-zones")
    cmd.extend(["--output", str(drc_output), str(pcb_path)])
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    summary: Dict[str, Any] = {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout_tail": tail_text(proc.stdout),
        "stderr_tail": tail_text(proc.stderr),
        "output_path": str(drc_output),
    }
    if proc.returncode != 0:
        summary["status"] = "failed"
        return summary
    if not drc_output.is_file():
        summary["status"] = "failed"
        summary["error"] = f"DRC output not found at {drc_output}"
        return summary
    drc_data = json.loads(drc_output.read_text(encoding="utf-8"))
    summary.update(summarize_drc_report(drc_data))
    summary["status"] = "ok"
    return summary


def run_kicad_cli_refill_zones(
    *,
    platform: Platform,
    pcb_path: Path,
    cli_path: str,
    timeout_sec: int = 120,
) -> Dict[str, Any]:
    del platform
    cmd = [
        cli_path,
        "pcb",
        "drc",
        "--refill-zones",
        "--save-board",
        str(pcb_path),
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "command": cmd,
        "returncode": proc.returncode,
        "stdout_tail": tail_text(proc.stdout),
        "stderr_tail": tail_text(proc.stderr),
    }


def export_specctra_dsn(
    pcbnew_mod: Any, board_path: Path, dsn_path: Path
) -> None:
    board = pcbnew_mod.LoadBoard(str(board_path))
    dsn_path.parent.mkdir(parents=True, exist_ok=True)

    export_fn = getattr(pcbnew_mod, "ExportSpecctraDSN", None)
    if export_fn is None:
        raise RuntimeError(
            "pcbnew.ExportSpecctraDSN is unavailable in this KiCad build. "
            "KiCad 10 removed `kicad-cli pcb export specctradsn`; use the "
            "pcbnew Python API instead."
        )

    try:
        ok = export_fn(board, str(dsn_path))
    except TypeError:
        ok = export_fn(str(dsn_path))

    if ok is False:
        raise RuntimeError(f"pcbnew.ExportSpecctraDSN failed for {board_path}")

    if not dsn_path.is_file() or dsn_path.stat().st_size == 0:
        raise RuntimeError(
            f"DSN export did not produce a non-empty file at {dsn_path}"
        )


def run_freerouting(
    *,
    java_bin: str,
    jar_path: Path,
    dsn_path: Path,
    ses_path: Path,
    timeout_sec: int,
    options: Optional[FreeRoutingOptions] = None,
) -> Dict[str, Any]:
    ses_path.parent.mkdir(parents=True, exist_ok=True)
    cmd, options_payload, option_warnings = build_freerouting_command(
        java_bin=java_bin,
        jar_path=jar_path,
        dsn_path=dsn_path,
        ses_path=ses_path,
        options=options,
    )
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - started
        stdout_text = _decode_captured(exc.stdout)
        stderr_text = _decode_captured(exc.stderr)
        summary = _freerouting_proc_summary(
            cmd=cmd,
            options_payload=options_payload,
            option_warnings=option_warnings,
            returncode=None,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            elapsed=elapsed,
        )
        summary["timed_out"] = True
        raise FreeRoutingError(
            f"FreeRouting timed out after {timeout_sec}s "
            "(subprocess --timeout-sec; not FreeRouting -t).",
            summary,
        ) from exc
    elapsed = time.monotonic() - started
    summary = _freerouting_proc_summary(
        cmd=cmd,
        options_payload=options_payload,
        option_warnings=option_warnings,
        returncode=proc.returncode,
        stdout_text=proc.stdout or "",
        stderr_text=proc.stderr or "",
        elapsed=elapsed,
    )
    if proc.returncode != 0:
        raise FreeRoutingError(
            "FreeRouting failed with exit code "
            f"{proc.returncode}. stderr tail: {(proc.stderr or '')[-1000:]}",
            summary,
        )
    if not ses_path.is_file() or ses_path.stat().st_size == 0:
        raise FreeRoutingError(
            f"FreeRouting did not produce a non-empty SES at {ses_path}",
            summary,
        )
    return summary


def import_specctra_ses(
    pcbnew_mod: Any,
    board_path: Path,
    ses_path: Path,
    output_pcb_path: Path,
) -> None:
    board = pcbnew_mod.LoadBoard(str(board_path))
    import_fn = getattr(pcbnew_mod, "ImportSpecctraSES", None)
    if import_fn is None:
        raise RuntimeError(
            "pcbnew.ImportSpecctraSES is unavailable in this KiCad build. "
            "KiCad 10 removed `kicad-cli pcb export specctradsn`; use the "
            "pcbnew Python API instead."
        )

    import_fn(board, str(ses_path))
    output_pcb_path.parent.mkdir(parents=True, exist_ok=True)
    pcbnew_mod.SaveBoard(str(output_pcb_path), board)


def resolve_artifact_paths(
    *,
    pcb_path: Path,
    project_dir: Path,
    dsn_path: Optional[Path],
    ses_path: Optional[Path],
    jar_path: Optional[Path],
    freerouting_version: str,
    cache_dir: Optional[Path],
) -> Tuple[Path, Path, Path]:
    stem = pcb_path.stem
    scratch = cache_dir or default_skill_cache_dir(project_dir)
    resolved_dsn = dsn_path or (scratch / f"{stem}.dsn")
    resolved_ses = ses_path or (scratch / f"{stem}.ses")
    resolved_jar = jar_path or (
        scratch / default_freerouting_jar_name(freerouting_version)
    )
    return resolved_dsn, resolved_ses, resolved_jar


def _restore_file(path: Path, backup: Optional[bytes]) -> None:
    if backup is None:
        path.unlink(missing_ok=True)
    else:
        path.write_bytes(backup)


def _discover_cli_or_warn(
    platform: Platform,
    kicad_cli_path: Optional[str],
    warnings: List[str],
) -> Optional[str]:
    try:
        return discover_kicad_cli(platform, kicad_cli_path)
    except RuntimeError as exc:
        warnings.append(str(exc))
        return None


def _import_net_group_ses(
    pcbnew_mod: Any,
    *,
    pcb_path: Path,
    ses_path: Path,
    output_path: Path,
    before: Dict[str, List[Dict[str, Any]]],
    target_nets: Sequence[str],
) -> Tuple[Dict[str, Any], Optional[bytes], bool]:
    """Import SES, verify non-target copper, save only if it is intact.

    Returns (copper report, backup of the prior output file, saved).
    """
    ses_text = ses_path.read_text(encoding="utf-8", errors="replace")
    if SKIP_PIN_NET_PREFIX in ses_text:
        return (
            {
                "status": "changed",
                "changed_nets": {"(placeholder pin nets)": {"added": 1}},
                "error": "FreeRouting wrote copper on a placeholder pin net.",
            },
            None,
            False,
        )
    board = pcbnew_mod.LoadBoard(str(pcb_path))
    pcbnew_mod.ImportSpecctraSES(board, str(ses_path))
    after = snapshot_board_copper(board)
    copper = compare_copper(before, after, target_nets)
    for record in copper.pop("duplicates"):
        board.Remove(record["_item"])
    pairs = copper.pop("pairs")
    copper["snapped_drift_items"] = 0
    if copper["status"] != "unchanged" or copper["target_items_removed"]:
        return copper, None, False
    copper["snapped_drift_items"] = snap_back_drift(pcbnew_mod, pairs)
    backup = output_path.read_bytes() if output_path.is_file() else None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pcbnew_mod.SaveBoard(str(output_path), board)
    return copper, backup, True


def run_autoroute(
    *,
    platform: Platform,
    pcb_path: Path,
    project_dir: Path,
    output_pcb_path: Optional[Path] = None,
    dsn_path: Optional[Path] = None,
    ses_path: Optional[Path] = None,
    jar_path: Optional[Path] = None,
    freerouting_version: str = "2.2.4",
    freerouting_url: Optional[str] = None,
    java_bin: str = "java",
    timeout_sec: int = 600,
    keep_artifacts: bool = True,
    cache_dir: Optional[Path] = None,
    freerouting_options: Optional[FreeRoutingOptions] = None,
    run_drc: bool = False,
    refill_zones: bool = False,
    kicad_cli_path: Optional[str] = None,
    kicad_cli_timeout_sec: int = 120,
    target_nets: Sequence[str] = (),
    target_classes: Sequence[str] = (),
) -> AutorouteResult:
    """Export DSN, run FreeRouting, import SES.

    With ``target_nets``/``target_classes`` (or ignored net classes) the
    route is a net-group route: only that group is routed, every other
    net's copper must come back unchanged, and the result is reverted
    if it adds DRC errors or leaves more target connections open.
    """
    pcb_path = pcb_path.resolve()
    project_dir = project_dir.resolve()
    if not pcb_path.is_file():
        raise FileNotFoundError(str(pcb_path))

    options = freerouting_options or FreeRoutingOptions()
    group_mode = bool(
        split_name_list(target_nets)
        or split_name_list(target_classes)
        or split_name_list(options.ignore_net_classes)
    )

    resolved_dsn, resolved_ses, resolved_jar = resolve_artifact_paths(
        pcb_path=pcb_path,
        project_dir=project_dir,
        dsn_path=dsn_path,
        ses_path=ses_path,
        jar_path=jar_path,
        freerouting_version=freerouting_version,
        cache_dir=cache_dir,
    )
    output_path = (output_pcb_path or pcb_path).resolve()
    url = freerouting_url or default_freerouting_url(freerouting_version)

    timings: Dict[str, float] = {}
    commands: List[Dict[str, Any]] = []
    warnings: List[str] = []
    notes: List[str] = []

    segment_before = count_pcb_segments(pcb_path)

    t0 = time.monotonic()
    pcbnew_mod, _, import_warnings = import_pcbnew(platform)
    warnings.extend(import_warnings)
    timings["import_pcbnew_sec"] = time.monotonic() - t0

    t0 = time.monotonic()
    resolved_java = ensure_java(java_bin)
    timings["java_check_sec"] = time.monotonic() - t0

    t0 = time.monotonic()
    resolved_jar, downloader = download_freerouting_jar(
        resolved_jar,
        url=url,
        timeout_sec=min(timeout_sec, 120),
    )
    timings["download_jar_sec"] = time.monotonic() - t0
    notes.append(f"Using FreeRouting JAR at {resolved_jar}")
    if downloader is not None:
        notes.append(f"Downloaded FreeRouting JAR using {downloader}.")

    t0 = time.monotonic()
    export_specctra_dsn(pcbnew_mod, pcb_path, resolved_dsn)
    timings["export_dsn_sec"] = time.monotonic() - t0

    net_group: Optional[Dict[str, Any]] = None
    group_targets: List[str] = []
    before_copper: Dict[str, List[Dict[str, Any]]] = {}
    baseline_drc: Optional[Dict[str, Any]] = None
    resolved_cli: Optional[str] = None
    if group_mode:
        plan = restrict_dsn_to_nets(
            resolved_dsn.read_text(encoding="utf-8", errors="replace"),
            target_nets,
            target_classes,
            exclude_classes=options.ignore_net_classes,
        )
        resolved_dsn.write_text(plan.dsn_text, encoding="utf-8")
        warnings.extend(plan.warnings)
        group_targets = list(plan.target_nets)
        net_group = plan.to_dict()
        options = dataclasses.replace(
            options, ignore_net_classes=list(plan.skip_classes)
        )
        before_copper = snapshot_board_copper(
            pcbnew_mod.LoadBoard(str(pcb_path))
        )
        resolved_cli = _discover_cli_or_warn(
            platform, kicad_cli_path, warnings
        )
        if resolved_cli is not None:
            t0 = time.monotonic()
            baseline_drc = run_kicad_cli_drc(
                platform=platform,
                pcb_path=pcb_path,
                project_dir=project_dir,
                cli_path=resolved_cli,
                timeout_sec=kicad_cli_timeout_sec,
                refill_zones=True,
                label="pre-route",
            )
            timings["pre_route_drc_sec"] = time.monotonic() - t0
            if baseline_drc.get("status") != "ok":
                warnings.append(
                    "Pre-route DRC failed; the DRC/connectivity delta for "
                    "this net group is unavailable."
                )
                baseline_drc = None
        else:
            warnings.append(
                "kicad-cli not found: the net-group route cannot check new "
                "DRC violations or target connectivity; run run_drc."
            )

    t0 = time.monotonic()
    route_summary = run_freerouting(
        java_bin=resolved_java,
        jar_path=resolved_jar,
        dsn_path=resolved_dsn,
        ses_path=resolved_ses,
        timeout_sec=timeout_sec,
        options=options,
    )
    timings["freerouting_sec"] = route_summary["elapsed_sec"]
    commands.append(route_summary)
    warnings.extend(route_summary.get("option_warnings", []))
    telemetry = route_summary.get("freerouting_telemetry") or {}
    next_actions = build_next_actions(telemetry)

    status = "routed"
    error: Optional[str] = None
    drc_summary: Optional[Dict[str, Any]] = None
    t0 = time.monotonic()
    if net_group is not None:
        copper, backup, saved = _import_net_group_ses(
            pcbnew_mod,
            pcb_path=pcb_path,
            ses_path=resolved_ses,
            output_path=output_path,
            before=before_copper,
            target_nets=group_targets,
        )
        timings["import_ses_sec"] = time.monotonic() - t0
        net_group["non_target_copper"] = copper
        delta: Optional[Dict[str, Any]] = None
        if saved and resolved_cli is not None and baseline_drc is not None:
            t0 = time.monotonic()
            drc_summary = run_kicad_cli_drc(
                platform=platform,
                pcb_path=output_path,
                project_dir=project_dir,
                cli_path=resolved_cli,
                timeout_sec=kicad_cli_timeout_sec,
                refill_zones=True,
            )
            timings["post_route_drc_sec"] = time.monotonic() - t0
            commands.append(drc_summary)
            if drc_summary.get("status") == "ok":
                delta = drc_delta(baseline_drc, drc_summary, group_targets)
            else:
                warnings.append(
                    "Post-route DRC failed; inspect drc_summary in the "
                    "route JSON."
                )
        net_group["drc_delta"] = delta
        decision, reasons = judge_net_group_route(copper, delta)
        net_group["decision"] = decision
        net_group["reasons"] = reasons
        if decision == "reverted":
            if saved:
                _restore_file(output_path, backup)
            status = "reverted"
            error = " ".join(reasons)
            next_actions = [
                "The board is back to its pre-route state. Count this as "
                "one attempt for this net group.",
                *next_actions,
            ]
        elif delta is not None and delta["still_unconnected_nets"]:
            next_actions = [
                "Still unconnected in this group: "
                + ", ".join(delta["still_unconnected_nets"])
                + ". unroute_pcb_net any bad partial route, then re-route "
                "those nets with --nets (counts toward the 3-attempt "
                "group budget).",
                *next_actions,
            ]
        notes.append(
            "Net-group route: only net_group.target_nets were routed; all "
            "other copper was verified unchanged before saving."
        )
    else:
        import_specctra_ses(pcbnew_mod, pcb_path, resolved_ses, output_path)
        timings["import_ses_sec"] = time.monotonic() - t0

    segment_after = (
        count_pcb_segments(output_path) if output_path.is_file() else 0
    )
    notes.append(
        "After import, run fill_pcb_zones / kicad-cli pcb drc --refill-zones "
        "to regenerate copper pours."
    )
    notes.append(
        "status: routed means SES imported, not 100% connected. "
        "segment_count_* is not connectivity. Inspect "
        "freerouting_telemetry (final_unrouted, pass_history) "
        "before waiting on later DRC."
    )

    refill_zones_summary: Optional[Dict[str, Any]] = None
    if status == "routed" and (
        refill_zones or (run_drc and drc_summary is None)
    ):
        if resolved_cli is None:
            resolved_cli = _discover_cli_or_warn(
                platform, kicad_cli_path, warnings
            )

        if resolved_cli is not None and refill_zones:
            t0 = time.monotonic()
            refill_zones_summary = run_kicad_cli_refill_zones(
                platform=platform,
                pcb_path=output_path,
                cli_path=resolved_cli,
                timeout_sec=kicad_cli_timeout_sec,
            )
            timings["refill_zones_sec"] = time.monotonic() - t0
            commands.append(refill_zones_summary)
            if refill_zones_summary.get("status") != "ok":
                warnings.append(
                    "Zone refill failed; inspect refill_zones in the "
                    "route JSON."
                )

        if resolved_cli is not None and run_drc and drc_summary is None:
            t0 = time.monotonic()
            drc_summary = run_kicad_cli_drc(
                platform=platform,
                pcb_path=output_path,
                project_dir=project_dir,
                cli_path=resolved_cli,
                timeout_sec=kicad_cli_timeout_sec,
            )
            timings["post_route_drc_sec"] = time.monotonic() - t0
            commands.append(drc_summary)
            if drc_summary.get("status") != "ok":
                warnings.append(
                    "Post-route DRC failed; inspect drc_summary in the "
                    "route JSON."
                )

    if not keep_artifacts:
        for artifact in (resolved_dsn, resolved_ses):
            try:
                artifact.unlink(missing_ok=True)
            except OSError as exc:
                warnings.append(f"Could not delete artifact {artifact}: {exc}")

    return AutorouteResult(
        status=status,
        pcb_path=str(pcb_path),
        dsn_path=str(resolved_dsn),
        ses_path=str(resolved_ses),
        jar_path=str(resolved_jar),
        output_pcb_path=str(output_path),
        segment_count_before=segment_before,
        segment_count_after=segment_after,
        timings_sec=timings,
        commands=commands,
        warnings=warnings,
        notes=notes,
        drc_summary=drc_summary,
        refill_zones=refill_zones_summary,
        freerouting_telemetry=telemetry,
        next_actions=next_actions,
        net_group=net_group,
        error=error,
    )


def measure_net_lengths(
    *,
    platform: Platform,
    pcb_path: Path,
    nets: Sequence[str],
    target_skew_mm: Optional[float] = None,
) -> Dict[str, Any]:
    """Routed copper length per net and the max skew across them."""
    pcbnew_mod, _, warnings = import_pcbnew(platform)
    board = pcbnew_mod.LoadBoard(str(pcb_path.resolve()))
    snapshot = snapshot_board_copper(board)
    names = split_name_list(nets)
    known = {str(name) for name in board.GetNetsByName().keys()}
    unknown = [name for name in names if name not in known]
    if unknown:
        raise ValueError(
            f"Unknown net(s): {', '.join(unknown)}. Use exact KiCad names."
        )
    payload: Dict[str, Any] = {"status": "ok", "pcb_path": str(pcb_path)}
    payload.update(net_lengths(snapshot, names))
    payload["note"] = (
        "track_length_mm sums every track/arc on the net (no via barrel "
        "or pad-to-die length). Compare nets of one pair or bus."
    )
    if target_skew_mm is not None:
        payload["target_skew_mm"] = target_skew_mm
        payload["within_target"] = payload["max_skew_mm"] <= target_skew_mm
    if warnings:
        payload["warnings"] = warnings
    return payload


def diagnose_environment(
    *,
    platform: Platform,
    java_bin: str = "java",
    script_path: str = DEFAULT_SKILL_MAIN_PY,
    pcb_path: Optional[str] = None,
    project_dir: str = ".",
) -> Dict[str, Any]:
    java_ok = False
    java_detail = ""
    try:
        resolved = ensure_java(java_bin)
        java_ok = True
        java_detail = resolved
    except Exception as exc:  # noqa: BLE001 - diagnostic surface
        java_detail = str(exc)

    pcbnew_ok = False
    pcbnew_detail = ""
    tried_paths: List[str] = []
    try:
        _, tried_paths, _ = import_pcbnew(platform)
        pcbnew_ok = True
        pcbnew_detail = "import ok"
    except Exception as exc:  # noqa: BLE001 - diagnostic surface
        pcbnew_detail = str(exc)
        tried_paths = [
            str(path) for path in pcbnew_sys_path_candidates(platform)
        ]

    recommended_python: Optional[Path] = None
    python_probes: List[Dict[str, str]] = []
    if not pcbnew_ok:
        recommended_python, python_probes = discover_recommended_python(
            platform
        )

    recommended_python_str = (
        str(recommended_python) if recommended_python is not None else None
    )
    recommended_diagnose_command = None
    recommended_route_command = None
    if recommended_python is not None:
        recommended_diagnose_command = build_skill_command(
            recommended_python,
            subcommand="diagnose",
            platform=platform,
            script_path=script_path,
            java_bin=java_bin,
        )
        recommended_route_command = build_skill_command(
            recommended_python,
            subcommand="route",
            platform=platform,
            script_path=script_path,
            project_dir=project_dir,
            pcb_path=pcb_path,
            java_bin=java_bin,
        )

    return {
        "status": "ok" if java_ok and pcbnew_ok else "missing_dependencies",
        "platform": platform,
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "java_available": java_ok,
        "java_detail": java_detail,
        "java_required": MIN_JAVA_MAJOR,
        "pcbnew_available": pcbnew_ok,
        "pcbnew_detail": pcbnew_detail,
        "pcbnew_site_paths": tried_paths,
        "recommended_python": recommended_python_str,
        "recommended_diagnose_command": recommended_diagnose_command,
        "recommended_route_command": recommended_route_command,
        "python_probes": python_probes,
        **({} if java_ok else {"java_install_hint": java_install_hint()}),
        "notes": _diagnose_guidance_notes(
            platform=platform,
            pcbnew_ok=pcbnew_ok,
            recommended_python=recommended_python,
        ),
    }

import argparse
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Flags older skills documented that FreeRouting 2.2.4 does not parse.
# Accepted so old commands still run, then reported as warnings.
_LEGACY_ROUTE_FLAGS = {
    "post_route_passes": "--post-route-passes (-pp)",
    "fanout": "--fanout (-fo)",
    "save_intermediate": "--save-intermediate (-im)",
    "trace": "--trace",
    "experimental": "--experimental (-test)",
}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run KiCad Specctra DSN export, FreeRouting, and SES import on "
            "the user's machine."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    route = subparsers.add_parser(
        "route",
        help="Export DSN, run FreeRouting, and import SES into the PCB.",
        description=(
            "Export Specctra DSN, run FreeRouting, and import SES. "
            "Headless by default "
            "(-Djava.awt.headless=true, --gui.enabled=false). "
            "Missing JARs are auto-downloaded and cached. "
            "--timeout-sec is the Java subprocess wall-clock bound, "
            "not FreeRouting -t. Java exit 0 / status routed means SES "
            "imported, not 100% connected; inspect "
            "freerouting_telemetry. Route surgically: --nets A,B (or "
            "--net-classes) routes only that net group while every other "
            "net's copper stays fixed; the result is reverted if it "
            "changes other copper, adds DRC errors, or leaves more target "
            "connections open. Engine knobs (--max-passes, optimizer "
            "strategies, threads) may be iterated freely. --rules-file is "
            "a protected physical constraint. --hybrid-ratio is a float "
            "(-hr)."
        ),
    )
    route.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        required=True,
        help="Host platform for pcbnew path probing.",
    )
    route.add_argument(
        "--pcb",
        required=True,
        help=(
            "Path to the .kicad_pcb file. Relative paths resolve against "
            "--project-dir, not the shell CWD."
        ),
    )
    route.add_argument(
        "--project-dir",
        default=".",
        help="Project root used for cache/artifact paths and relative inputs.",
    )
    route.add_argument(
        "--output-pcb",
        default=None,
        help="Optional output PCB path. Defaults to overwriting --pcb.",
    )
    route.add_argument(
        "--dsn",
        default=None,
        help="Optional DSN output path. Defaults to skill cache directory.",
    )
    route.add_argument(
        "--ses",
        default=None,
        help="Optional SES output path. Defaults to skill cache directory.",
    )
    route.add_argument(
        "--jar-path",
        default=None,
        help="Optional FreeRouting JAR path. Defaults to cached skill JAR.",
    )
    route.add_argument(
        "--freerouting-version",
        default="2.2.4",
        help="FreeRouting release version used for default JAR naming/URL.",
    )
    route.add_argument(
        "--freerouting-url",
        default=None,
        help="Override FreeRouting JAR download URL.",
    )
    route.add_argument(
        "--java-bin",
        default=os.environ.get("COPPERPILOT_JAVA", "java"),
        help="Java executable used to run FreeRouting.",
    )
    route.add_argument(
        "--timeout-sec",
        type=int,
        default=600,
        help=(
            "Java subprocess wall-clock timeout in seconds (default 600). "
            "Not FreeRouting -t."
        ),
    )
    route.add_argument(
        "--cache-dir",
        default=None,
        help="Optional cache directory for DSN/SES/JAR artifacts.",
    )
    route.add_argument(
        "--keep-artifacts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep DSN/SES artifacts after a successful route.",
    )
    route.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Run FreeRouting headless (default). Use --no-headless only for "
            "local GUI debugging."
        ),
    )
    route.add_argument(
        "--nets",
        action="append",
        default=[],
        metavar="NET1,NET2",
        help=(
            "Route only these nets (exact KiCad names, comma separated, "
            "repeatable). All other copper stays fixed and is verified "
            "unchanged."
        ),
    )
    route.add_argument(
        "--net-classes",
        action="append",
        default=[],
        metavar="CLASS1,CLASS2",
        help=(
            "Add every net of these KiCad net classes to the --nets group "
            "(Default = kicad_default)."
        ),
    )
    route.add_argument(
        "--max-passes",
        "--autorouter-passes",
        dest="max_passes",
        type=int,
        default=None,
        metavar="N",
        help="FreeRouting -mp upper limit of auto-router passes.",
    )
    route.add_argument(
        "--post-route-passes",
        type=int,
        default=None,
        metavar="N",
        help="Ignored: FreeRouting 2.2.4 has no -pp. Kept for old commands.",
    )
    route.add_argument(
        "--fanout",
        action="store_true",
        default=False,
        help="Ignored: FreeRouting 2.2.4 has no -fo. Kept for old commands.",
    )
    route.add_argument(
        "--threads",
        type=int,
        default=None,
        metavar="N",
        help="FreeRouting -mt thread pool size for route optimization.",
    )
    route.add_argument(
        "--optimization-threshold",
        type=float,
        default=None,
        metavar="RATIO",
        help="FreeRouting -oit optimization improvement threshold.",
    )
    route.add_argument(
        "--board-update-strategy",
        choices=["greedy", "global", "hybrid"],
        default=None,
        help="FreeRouting -us board update strategy.",
    )
    route.add_argument(
        "--hybrid-ratio",
        type=float,
        default=None,
        metavar="RATIO",
        help=(
            "FreeRouting -hr hybrid ratio as a float "
            "(requires --board-update-strategy hybrid)."
        ),
    )
    route.add_argument(
        "--item-selection-strategy",
        choices=["sequential", "random", "prioritized"],
        default=None,
        help="FreeRouting -is item selection strategy.",
    )
    route.add_argument(
        "--ignore-net-class",
        action="append",
        default=[],
        dest="ignore_net_classes",
        metavar="CLASS",
        help=(
            "Exclude a net class from this route (repeatable or comma "
            "separated). Its copper stays fixed; passed to FreeRouting as "
            "one -inc list and enforced by the DSN rewrite."
        ),
    )
    route.add_argument(
        "--rules-file",
        default=None,
        help=(
            "FreeRouting -dr design rules file. Protected physical "
            "constraint; do not set without ask_user_question."
        ),
    )
    route.add_argument(
        "--save-intermediate",
        action="store_true",
        default=False,
        help="Ignored: FreeRouting 2.2.4 has no -im. Kept for old commands.",
    )
    route.add_argument(
        "--language",
        default=None,
        help="FreeRouting -l language code.",
    )
    route.add_argument(
        "--dialog-timeout",
        type=int,
        default=None,
        metavar="SEC",
        help="FreeRouting -dct dialog timeout in seconds.",
    )
    route.add_argument(
        "--disable-analytics",
        action="store_true",
        default=False,
        help="FreeRouting -da: disable analytics.",
    )
    route.add_argument(
        "--disable-logging",
        action="store_true",
        default=False,
        help="FreeRouting -dl: disable logging.",
    )
    route.add_argument(
        "--log-level",
        choices=[
            "ALL",
            "CONFIG",
            "FINE",
            "FINER",
            "FINEST",
            "INFO",
            "OFF",
            "SEVERE",
            "WARNING",
        ],
        default=None,
        help="FreeRouting -ll log level.",
    )
    route.add_argument(
        "--trace",
        action="store_true",
        default=False,
        help="Ignored: FreeRouting 2.2.4 has no -trace. Use --log-level.",
    )
    route.add_argument(
        "--experimental",
        action="store_true",
        default=False,
        help="Ignored: FreeRouting 2.2.4 has no -test. Kept for old commands.",
    )
    route.add_argument(
        "--extra-freerouting-arg",
        action="append",
        default=[],
        dest="extra_freerouting_args",
        metavar="ARG",
        help=(
            "Passthrough token appended after the headless/-de/-do "
            "skeleton. Repeatable. -dr/--rules-file extras are dropped."
        ),
    )
    route.add_argument(
        "--run-drc",
        action="store_true",
        default=False,
        help=(
            "After SES import, run kicad-cli pcb drc and include drc_summary "
            "with unconnected_items in the JSON result."
        ),
    )
    route.add_argument(
        "--refill-zones",
        action="store_true",
        default=False,
        help=(
            "After SES import, run kicad-cli pcb drc --refill-zones "
            "--save-board before optional post-route DRC."
        ),
    )
    route.add_argument(
        "--kicad-cli-path",
        default=None,
        help=(
            "Optional explicit kicad-cli path for --run-drc and "
            "--refill-zones."
        ),
    )
    route.add_argument(
        "--kicad-cli-timeout-sec",
        type=int,
        default=120,
        help="Timeout for optional kicad-cli post-route actions.",
    )

    lengths = subparsers.add_parser(
        "lengths",
        help="Report routed track length per net and the max skew.",
        description=(
            "Sum track/arc length per net with KiCad pcbnew. Use after "
            "routing a differential pair or matched bus to report skew "
            "against the target; FreeRouting cannot length-match."
        ),
    )
    lengths.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        required=True,
        help="Host platform for pcbnew path probing.",
    )
    lengths.add_argument(
        "--pcb", required=True, help="Path to the .kicad_pcb."
    )
    lengths.add_argument(
        "--project-dir",
        default=".",
        help="Project root used to resolve a relative --pcb.",
    )
    lengths.add_argument(
        "--nets",
        action="append",
        default=[],
        required=True,
        metavar="NET1,NET2",
        help="Nets to measure (comma separated, repeatable).",
    )
    lengths.add_argument(
        "--target-skew-mm",
        type=float,
        default=None,
        help="Optional skew budget; adds within_target to the result.",
    )

    diagnose = subparsers.add_parser(
        "diagnose",
        help="Check Java and pcbnew availability without modifying the board.",
    )
    diagnose.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        required=True,
        help="Host platform for pcbnew path probing.",
    )
    diagnose.add_argument(
        "--java-bin",
        default=os.environ.get("COPPERPILOT_JAVA", "java"),
        help="Java executable to probe.",
    )
    diagnose.add_argument(
        "--script-path",
        default=None,
        help=(
            "Path to this skill's main.py for recommended command output. "
            "Defaults to the invoked script path."
        ),
    )
    diagnose.add_argument(
        "--project-dir",
        default=".",
        help="Project root used when building recommended route command.",
    )
    diagnose.add_argument(
        "--pcb",
        default=None,
        help="Optional PCB path used when building recommended route command.",
    )
    return parser


def _resolve_route_paths(
    args: argparse.Namespace,
) -> Dict[str, Optional[Path]]:
    project_dir = Path(args.project_dir).resolve()
    return {
        "project_dir": project_dir,
        "pcb_path": resolve_project_path(args.pcb, project_dir),
        "output_pcb_path": resolve_project_path(args.output_pcb, project_dir),
        "dsn_path": resolve_project_path(args.dsn, project_dir),
        "ses_path": resolve_project_path(args.ses, project_dir),
        "jar_path": resolve_project_path(args.jar_path, project_dir),
        "cache_dir": resolve_project_path(args.cache_dir, project_dir),
        "rules_file": resolve_project_path(args.rules_file, project_dir),
    }


def _freerouting_options_from_args(
    args: argparse.Namespace,
    *,
    rules_file: Optional[Path],
) -> FreeRoutingOptions:
    return FreeRoutingOptions(
        headless=args.headless,
        max_passes=args.max_passes,
        threads=args.threads,
        optimization_threshold=args.optimization_threshold,
        board_update_strategy=args.board_update_strategy,
        hybrid_ratio=args.hybrid_ratio,
        item_selection_strategy=args.item_selection_strategy,
        ignore_net_classes=list(args.ignore_net_classes),
        rules_file=rules_file,
        language=args.language,
        dialog_timeout=args.dialog_timeout,
        disable_analytics=args.disable_analytics,
        disable_logging=args.disable_logging,
        log_level=args.log_level,
        extra_args=list(args.extra_freerouting_args),
    )


def legacy_flag_warnings(args: argparse.Namespace) -> List[str]:
    """Warn about accepted-but-ignored flags from older skill docs."""
    used = [
        label
        for dest, label in _LEGACY_ROUTE_FLAGS.items()
        if getattr(args, dest, None) not in (None, False)
    ]
    if not used:
        return []
    return [
        "Ignored "
        + ", ".join(used)
        + ": FreeRouting 2.2.4 does not support them. Use --max-passes, "
        "--timeout-sec, optimizer strategies, or a smaller --nets group."
    ]


def _attach_native_diagnostics(
    payload: Dict[str, Any],
    stdout_capture: io.StringIO,
    stderr_capture: io.StringIO,
) -> None:
    stdout_tail = tail_text(stdout_capture.getvalue())
    stderr_tail = tail_text(stderr_capture.getvalue())
    if stdout_tail:
        payload["native_stdout_tail"] = stdout_tail
    if stderr_tail:
        payload["native_stderr_tail"] = stderr_tail


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.command == "diagnose":
        script_path = args.script_path
        if script_path is None:
            script_path = str(Path(sys.argv[0]).resolve())
        with capture_native_streams() as (stdout_capture, stderr_capture):
            payload = diagnose_environment(
                platform=args.platform,
                java_bin=args.java_bin,
                script_path=script_path,
                pcb_path=args.pcb,
                project_dir=args.project_dir,
            )
        _attach_native_diagnostics(payload, stdout_capture, stderr_capture)
        _print_json(payload)
        return 0 if payload["status"] == "ok" else 2

    if args.command == "lengths":
        pcb = resolve_project_path(args.pcb, Path(args.project_dir).resolve())
        if pcb is None:
            _print_json({"status": "error", "error": "--pcb is required"})
            return 1
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        try:
            with capture_native_streams() as (stdout_capture, stderr_capture):
                payload = measure_net_lengths(
                    platform=args.platform,
                    pcb_path=pcb,
                    nets=args.nets,
                    target_skew_mm=args.target_skew_mm,
                )
        except Exception as exc:  # noqa: BLE001 - CLI boundary
            payload = {"status": "error", "error": str(exc)}
            _attach_native_diagnostics(payload, stdout_capture, stderr_capture)
            _print_json(payload)
            return 1
        _attach_native_diagnostics(payload, stdout_capture, stderr_capture)
        _print_json(payload)
        return 0

    if args.command == "route":
        paths = _resolve_route_paths(args)
        pcb_path = paths["pcb_path"]
        project_dir = paths["project_dir"]
        if pcb_path is None or project_dir is None:
            raise ValueError("--pcb and --project-dir are required for route")
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        try:
            with capture_native_streams() as (stdout_capture, stderr_capture):
                result = run_autoroute(
                    platform=args.platform,
                    pcb_path=pcb_path,
                    project_dir=project_dir,
                    output_pcb_path=paths["output_pcb_path"],
                    dsn_path=paths["dsn_path"],
                    ses_path=paths["ses_path"],
                    jar_path=paths["jar_path"],
                    freerouting_version=args.freerouting_version,
                    freerouting_url=args.freerouting_url,
                    java_bin=args.java_bin,
                    timeout_sec=args.timeout_sec,
                    keep_artifacts=args.keep_artifacts,
                    cache_dir=paths["cache_dir"],
                    freerouting_options=_freerouting_options_from_args(
                        args,
                        rules_file=paths["rules_file"],
                    ),
                    run_drc=args.run_drc,
                    refill_zones=args.refill_zones,
                    kicad_cli_path=args.kicad_cli_path,
                    kicad_cli_timeout_sec=args.kicad_cli_timeout_sec,
                    target_nets=args.nets,
                    target_classes=args.net_classes,
                )
        except FreeRoutingError as exc:
            summary = dict(exc.summary)
            telemetry = summary.get("freerouting_telemetry") or {}
            error_payload: Dict[str, Any] = {
                "status": "error",
                "error": str(exc),
                "commands": [summary],
                "freerouting_telemetry": telemetry,
                "next_actions": build_next_actions(
                    telemetry,
                    timed_out=bool(summary.get("timed_out")),
                ),
            }
            _attach_native_diagnostics(
                error_payload, stdout_capture, stderr_capture
            )
            _print_json(error_payload)
            return 1
        except Exception as exc:  # noqa: BLE001 - CLI boundary
            error_payload = {
                "status": "error",
                "error": str(exc),
                "next_actions": build_next_actions(),
            }
            _attach_native_diagnostics(
                error_payload, stdout_capture, stderr_capture
            )
            _print_json(error_payload)
            return 1

        payload = result.to_dict()
        payload["warnings"] = legacy_flag_warnings(args) + payload["warnings"]
        _attach_native_diagnostics(payload, stdout_capture, stderr_capture)
        _print_json(payload)
        return 0 if result.status == "routed" else 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
