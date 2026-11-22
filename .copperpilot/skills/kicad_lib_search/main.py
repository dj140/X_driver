#!/usr/bin/env python3
"""KiCad library search skill installed by CopperPilot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Sequence

Platform = Literal["win", "mac", "linux"]


def default_symbol_dir(platform: Platform) -> Path:
    env = os.environ.get("KICAD10_SYMBOL_DIR")
    if env:
        return Path(env)
    if platform == "mac":
        return Path(
            "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
        )
    if platform == "win":
        return Path(r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
    return Path("/usr/share/kicad/symbols")


def default_footprint_dir(platform: Platform) -> Path:
    env = os.environ.get("KICAD10_FOOTPRINT_DIR")
    if env:
        return Path(env)
    if platform == "mac":
        return Path(
            "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
        )
    if platform == "win":
        return Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
    return Path("/usr/share/kicad/footprints")


def default_model_dir(platform: Platform) -> Path:
    env = os.environ.get("KICAD10_3DMODEL_DIR")
    if env:
        return Path(env)
    if platform == "mac":
        return Path(
            "/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels"
        )
    if platform == "win":
        return Path(r"C:\Program Files\KiCad\10.0\share\kicad\3dmodels")
    return Path("/usr/share/kicad/3dmodels")


def _dedupe_paths(paths: Iterable[Path]) -> List[Path]:
    seen: set[str] = set()
    out: List[Path] = []
    for raw in paths:
        resolved = raw.expanduser()
        key = str(resolved.resolve()) if resolved.exists() else str(resolved)
        if key in seen:
            continue
        seen.add(key)
        out.append(resolved)
    return out


def project_local_symbol_paths(project_dir: Path) -> List[Path]:
    root = project_dir.resolve()
    paths: List[Path] = []
    for path in sorted(root.glob("*.kicad_sym")):
        paths.append(path)
    return paths


def project_local_footprint_dirs(project_dir: Path) -> List[Path]:
    root = project_dir.resolve()
    return sorted(root.glob("*.pretty"))


def project_local_model_dirs(project_dir: Path) -> List[Path]:
    root = project_dir.resolve()
    model_root = root / "libs" / "3dmodels"
    if model_root.is_dir():
        return [model_root]
    return []


def resolve_symbol_roots(
    platform: Platform,
    *,
    project_dir: Path,
    include_project_local: bool,
    extra_dirs: Optional[Sequence[str]] = None,
) -> tuple[List[Path], List[str]]:
    """Return symbol file paths and warning strings."""
    warnings: List[str] = []
    paths: List[Path] = []

    stock = default_symbol_dir(platform)
    if stock.is_dir():
        paths.extend(sorted(stock.glob("*.kicad_sym")))
    else:
        warnings.append(f"Stock symbol directory not found: {stock}")

    if extra_dirs:
        for raw in extra_dirs:
            candidate = Path(raw).expanduser()
            if candidate.is_file() and candidate.suffix == ".kicad_sym":
                paths.append(candidate)
            elif candidate.is_dir():
                paths.extend(sorted(candidate.rglob("*.kicad_sym")))
            else:
                warnings.append(f"Symbol path not found: {candidate}")

    if include_project_local:
        paths.extend(project_local_symbol_paths(project_dir))

    return _dedupe_paths(paths), warnings


def resolve_footprint_roots(
    platform: Platform,
    *,
    project_dir: Path,
    include_project_local: bool,
    extra_dirs: Optional[Sequence[str]] = None,
    prefer_extra_dirs: bool = True,
) -> tuple[List[Path], List[str]]:
    """Resolve footprint library roots.

    When ``prefer_extra_dirs`` is True (default), explicit and project-local
    roots are searched before stock libraries so deterministic fixtures and
    project overrides win over mismatched stock versions.
    """
    warnings: List[str] = []
    extra: List[Path] = []
    project_local: List[Path] = []
    stock_dirs: List[Path] = []

    stock = default_footprint_dir(platform)
    if stock.is_dir():
        stock_dirs.extend(sorted(stock.glob("*.pretty")))
    else:
        warnings.append(f"Stock footprint directory not found: {stock}")

    if extra_dirs:
        for raw in extra_dirs:
            candidate = Path(raw).expanduser()
            if candidate.suffix == ".pretty" and candidate.is_dir():
                extra.append(candidate)
            elif candidate.is_dir():
                extra.extend(sorted(candidate.rglob("*.pretty")))
            else:
                warnings.append(f"Footprint path not found: {candidate}")

    if include_project_local:
        project_local.extend(project_local_footprint_dirs(project_dir))

    if prefer_extra_dirs:
        dirs = extra + project_local + stock_dirs
    else:
        dirs = stock_dirs + extra + project_local

    return _dedupe_paths(dirs), warnings


def resolve_model_roots(
    platform: Platform,
    *,
    project_dir: Path,
    include_project_local: bool,
    extra_dirs: Optional[Sequence[str]] = None,
) -> tuple[List[Path], List[str]]:
    warnings: List[str] = []
    roots: List[Path] = []

    if extra_dirs:
        for raw in extra_dirs:
            candidate = Path(raw).expanduser()
            if candidate.is_dir():
                roots.append(candidate)
            else:
                warnings.append(f"3D model path not found: {candidate}")

    if include_project_local:
        roots.extend(project_local_model_dirs(project_dir))

    # Explicit and project-local roots are intent-bearing and must not be
    # crowded out by a large stock library before max_results is reached.
    stock = default_model_dir(platform)
    if stock.is_dir():
        roots.append(stock)
    else:
        warnings.append(f"Stock 3D model directory not found: {stock}")

    return _dedupe_paths(roots), warnings

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence


SearchKind = Literal["symbol", "footprint", "model", "all"]
MODEL_EXTENSIONS = {".step", ".stp", ".wrl", ".stl"}


@dataclass
class SearchResult:
    kind: str
    library: str
    name: str
    path: str
    score: float
    identifier: str
    description: str = ""
    keywords: str = ""
    tags: str = ""
    model_path: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "kind": self.kind,
            "library": self.library,
            "name": self.name,
            "path": self.path,
            "score": self.score,
            "identifier": self.identifier,
        }
        if self.description:
            payload["description"] = self.description
        if self.keywords:
            payload["keywords"] = self.keywords
        if self.tags:
            payload["tags"] = self.tags
        if self.model_path:
            payload["model_path"] = self.model_path
        if self.extra:
            payload.update(self.extra)
        if self.kind == "footprint":
            payload["library_path"] = self.path
            payload["footprint_id"] = self.name
        elif self.kind == "symbol":
            payload["library_path"] = self.path
            payload["symbol_id"] = self.name
        return payload


def _split_query_words(query: str) -> List[str]:
    words: List[str] = []
    for space_sep in query.lower().split():
        for pipe_sep in space_sep.split("|"):
            for col_sep in pipe_sep.split(":"):
                token = col_sep.strip()
                if token:
                    words.append(token)
    return words


def _calculate_name_score(
    name: str,
    query_lower: str,
    query_words: Sequence[str],
    *,
    short_name_bonus: int = 2,
) -> float:
    score = 0.0
    name_lower = name.lower()

    if query_lower == name_lower:
        score += 20.0

    name_matched = False
    for word in query_words:
        if word == name_lower:
            score += 25.0
            name_matched = True
            break

    if len(name_lower) <= short_name_bonus:
        for word in query_words:
            if word == name_lower:
                score += 15.0
                break

    if not name_matched and query_words and query_words[0] == name_lower:
        score += 10.0
        name_matched = True

    if not name_matched and query_lower in name_lower:
        score += 10.0

    return score


def _read_limited_text(path: Path, max_bytes: int) -> str:
    size = path.stat().st_size
    if size <= max_bytes:
        return path.read_text(encoding="utf-8", errors="replace")
    with path.open("rb") as handle:
        data = handle.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def _extract_property(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def _timed_out(start: float, timeout_ms: Optional[int]) -> bool:
    if timeout_ms is None:
        return False
    return (time.perf_counter() - start) * 1000.0 >= timeout_ms


_SYMBOL_HEADER_RE = re.compile(r'\(symbol\s+"((?:[^"\\]|\\.)*)"')
_PIN_RE = re.compile(r"\(pin\s")
_EXTENDS_RE = re.compile(r'\(extends\s+"((?:[^"\\]|\\.)*)"')


def _unit_suffix(name: str, base: str) -> Optional[tuple[int, int]]:
    """Return (unit, body_style) when ``name`` is ``<base>_<unit>_<style>``."""
    prefix = base + "_"
    if not name.startswith(prefix):
        return None
    parts = name[len(prefix) :].split("_")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1])


def iter_top_level_symbol_spans(
    content: str,
) -> List[tuple[str, int, int, int]]:
    """Return ``(name, start, end, unit_count)`` for top-level symbols.

    KiCad names unit/body-style sub-symbols ``<parent>_<unit>_<style>``
    (e.g. ``LM358_1_1``), so a header with that shape directly after its
    parent is a nested unit block, not a separate library symbol. A
    symbol's span runs to the next top-level header, so it includes its
    unit blocks (pins and graphics). Library-qualified names such as
    ``Device:R`` (schematic ``lib_symbols``) nest as ``R_0_1``.
    """
    spans: List[List[Any]] = []
    base = None
    for match in _SYMBOL_HEADER_RE.finditer(content):
        name = match.group(1)
        if base is not None:
            suffix = _unit_suffix(name, base)
            if suffix is not None:
                spans[-1][3] = max(spans[-1][3], suffix[0])
                continue
        spans.append([name, match.start(), len(content), 1])
        base = name.split(":")[-1]
    for idx in range(len(spans) - 1):
        spans[idx][2] = spans[idx + 1][1]
    return [(n, s, e, u) for n, s, e, u in spans]


def _symbol_extra(
    symbol_block: str,
    symbol_name: str,
    fp_filters: str,
    counts_of: Callable[[str], tuple[int, int]],
) -> Dict[str, Any]:
    extra: Dict[str, Any] = {}
    if fp_filters:
        extra["footprint_filters"] = fp_filters
    pin_count, unit_count = counts_of(symbol_name)
    extends = _EXTENDS_RE.search(symbol_block, 0, 2000)
    if extends:
        # Derived symbols carry only properties; pins and units come
        # from the parent in the same file.
        parent = extends.group(1)
        extra["extends"] = parent
        pin_count, unit_count = counts_of(parent)
    extra["pin_count"] = pin_count
    if unit_count > 1:
        extra["unit_count"] = unit_count
    return extra


def search_symbols_in_files(
    query: str,
    symbol_files: Sequence[Path],
    *,
    max_results: int = 20,
    timeout_ms: Optional[int] = 30000,
    max_file_bytes: int = 32_000_000,
) -> List[SearchResult]:
    query_lower = query.lower()
    query_words = _split_query_words(query)
    start = time.perf_counter()
    scored: List[tuple[SearchResult, float]] = []

    for symbol_file in symbol_files:
        if _timed_out(start, timeout_ms):
            break
        try:
            content = _read_limited_text(symbol_file, max_file_bytes)
        except OSError:
            continue

        lib_name = symbol_file.stem
        content_lower = content.lower()
        if query_words and not all(
            word in content_lower for word in query_words
        ):
            continue

        spans = iter_top_level_symbol_spans(content)
        span_by_name = {name: (lo, hi, u) for name, lo, hi, u in spans}

        def counts_of(name: str) -> tuple[int, int]:
            """Return (pin_count, unit_count) for a symbol in this file."""
            bounds = span_by_name.get(name)
            if bounds is None:
                return 0, 1
            pins = len(_PIN_RE.findall(content, bounds[0], bounds[1]))
            return pins, bounds[2]

        for symbol_name, block_start, block_end, _units in spans:
            if _timed_out(start, timeout_ms):
                break
            symbol_block = content[block_start:block_end]
            # KiCad 6+ writes (property "Description" "..."): the optional
            # quote lets the key's closing quote precede the value.
            description = _extract_property(
                symbol_block, r'(?:ki_description|Description)"?\s+"([^"]*)"'
            )
            keywords = _extract_property(
                symbol_block, r'ki_keywords"?\s+"([^"]*)"'
            )
            fp_filters = _extract_property(
                symbol_block,
                r'(?:ki_fp_filters|kifpfilters)"?\s+"([^"]*)"',
            )
            haystack = " ".join(
                [symbol_name, lib_name, description, keywords, fp_filters]
            ).lower()

            score = _calculate_name_score(
                symbol_name, query_lower, query_words, short_name_bonus=2
            )
            if description and query_lower in description.lower():
                score += 3.0
            if keywords and query_lower in keywords.lower():
                score += 2.0
            if fp_filters and query_lower in fp_filters.lower():
                score += 2.0
            for word in query_words:
                if word in haystack:
                    score += 1.0

            if score <= 0:
                continue

            result = SearchResult(
                kind="symbol",
                library=lib_name,
                name=symbol_name,
                path=str(symbol_file),
                score=score,
                identifier=f"{lib_name}:{symbol_name}",
                description=description,
                keywords=keywords,
                extra=_symbol_extra(
                    symbol_block,
                    symbol_name,
                    fp_filters,
                    counts_of,
                ),
            )
            scored.append((result, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [item[0] for item in scored[:max_results]]


def search_footprints_in_dirs(
    query: str,
    footprint_dirs: Sequence[Path],
    *,
    max_results: int = 20,
    timeout_ms: Optional[int] = 30000,
    max_file_bytes: int = 500_000,
) -> List[SearchResult]:
    query_lower = query.lower()
    query_words = _split_query_words(query)
    start = time.perf_counter()
    scored: List[tuple[SearchResult, float]] = []

    for lib_dir in footprint_dirs:
        if _timed_out(start, timeout_ms):
            break
        lib_name = lib_dir.name.replace(".pretty", "")
        try:
            filenames = [
                path
                for path in lib_dir.iterdir()
                if path.suffix == ".kicad_mod"
            ]
        except OSError:
            continue

        filenames_text = " ".join(path.name for path in filenames).lower()
        if query_words and not any(
            word in filenames_text for word in query_words
        ):
            header_match = False
        else:
            header_match = True

        for file_path in filenames:
            if _timed_out(start, timeout_ms):
                break
            footprint_name = file_path.stem
            filename_lower = footprint_name.lower()
            filename_match_count = sum(
                1 for word in query_words if word in filename_lower
            )

            try:
                if filename_match_count >= len(query_words):
                    content = _read_limited_text(file_path, max_file_bytes)
                elif filename_match_count > 0 or header_match:
                    content = _read_limited_text(file_path, max_file_bytes)
                    header = content[:400].lower()
                    if query_words and not any(
                        word in header for word in query_words
                    ):
                        continue
                else:
                    continue
            except OSError:
                continue

            description = _extract_property(content, r'\(descr\s+"([^"]*)"')
            tags = _extract_property(content, r'\(tags\s+"([^"]*)"')
            models = " ".join(re.findall(r'\(model\s+"([^"]*)"', content))
            pads = " ".join(
                re.findall(r'\(pad\s+"?([^"\s)]+)"?', content)[:20]
            )
            haystack = " ".join(
                [
                    footprint_name,
                    lib_name,
                    description,
                    tags,
                    models,
                    pads,
                ]
            ).lower()

            score = _calculate_name_score(
                footprint_name, query_lower, query_words, short_name_bonus=4
            )
            if description and query_lower in description.lower():
                score += 3.0
            if tags and query_lower in tags.lower():
                score += 2.0
            for word in query_words:
                if word in haystack:
                    score += 1.0

            if score <= 0:
                continue

            model_path = models.split()[0] if models else ""
            result = SearchResult(
                kind="footprint",
                library=lib_name,
                name=footprint_name,
                path=str(file_path),
                score=score,
                identifier=f"{lib_name}:{footprint_name}",
                description=description,
                tags=tags,
                model_path=model_path,
            )
            scored.append((result, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [item[0] for item in scored[:max_results]]


def search_models_in_roots(
    query: str,
    model_roots: Sequence[Path],
    *,
    max_results: int = 20,
    timeout_ms: Optional[int] = 30000,
) -> List[SearchResult]:
    query_lower = query.lower()
    query_words = _split_query_words(query)
    start = time.perf_counter()
    scored: List[tuple[SearchResult, float]] = []

    for root in model_roots:
        if _timed_out(start, timeout_ms):
            break
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if _timed_out(start, timeout_ms):
                break
            if not path.is_file():
                continue
            if path.suffix.lower() not in MODEL_EXTENSIONS:
                continue
            try:
                rel_path = path.relative_to(root)
                rel_text = str(rel_path)
            except ValueError:
                rel_text = path.name
            haystack = rel_text.lower()
            if query_words and not any(
                word in haystack for word in query_words
            ):
                continue

            library = path.parent.name
            if library.endswith(".3dshapes"):
                library = library[: -len(".3dshapes")]

            score = _calculate_name_score(
                path.stem, query_lower, query_words, short_name_bonus=6
            )
            for word in query_words:
                if word in haystack:
                    score += 1.0

            if score <= 0:
                continue

            identifier = f"${{KIPRJMOD}}/libs/3dmodels/{rel_text}"
            if "libs/3dmodels" not in str(root):
                identifier = f"${{KICAD10_3DMODEL_DIR}}/{rel_text}"

            result = SearchResult(
                kind="model",
                library=library,
                name=path.name,
                path=str(path),
                score=score,
                identifier=identifier,
                model_path=str(path),
            )
            scored.append((result, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return [item[0] for item in scored[:max_results]]


def build_summary(
    query: str,
    kind: str,
    results: Sequence[SearchResult],
) -> str:
    if not results:
        return f"No {kind} matches found for '{query}'."
    top = results[:3]
    parts = [f"{item.identifier}" for item in top]
    suffix = ""
    if len(results) > 3:
        suffix = f" (+{len(results) - 3} more)"
    return (
        f"Found {len(results)} {kind} result(s) for '{query}': "
        + ", ".join(parts)
        + suffix
    )


def run_search(
    *,
    kind: SearchKind,
    query: str,
    platform: Platform,
    project_dir: str = ".",
    include_project_local: bool = True,
    symbol_dirs: Optional[Sequence[str]] = None,
    footprint_dirs: Optional[Sequence[str]] = None,
    model_dirs: Optional[Sequence[str]] = None,
    max_results: int = 20,
    timeout_ms: int = 30000,
    max_file_bytes: int = 32_000_000,
) -> Dict[str, Any]:
    start = time.perf_counter()
    project_path = Path(project_dir).expanduser().resolve()
    warnings: List[str] = []
    searched_roots: Dict[str, List[str]] = {
        "symbols": [],
        "footprints": [],
        "models": [],
    }
    all_results: List[SearchResult] = []

    per_kind = max_results if kind != "all" else max(5, max_results // 3 or 5)

    if kind in {"symbol", "all"}:
        symbol_files, symbol_warnings = resolve_symbol_roots(
            platform,
            project_dir=project_path,
            include_project_local=include_project_local,
            extra_dirs=symbol_dirs,
        )
        warnings.extend(symbol_warnings)
        searched_roots["symbols"] = [str(path) for path in symbol_files[:50]]
        symbol_results = search_symbols_in_files(
            query,
            symbol_files,
            max_results=per_kind if kind == "symbol" else per_kind,
            timeout_ms=timeout_ms,
            max_file_bytes=max_file_bytes,
        )
        all_results.extend(symbol_results)

    if kind in {"footprint", "all"}:
        footprint_lib_dirs, footprint_warnings = resolve_footprint_roots(
            platform,
            project_dir=project_path,
            include_project_local=include_project_local,
            extra_dirs=footprint_dirs,
        )
        warnings.extend(footprint_warnings)
        searched_roots["footprints"] = [
            str(path) for path in footprint_lib_dirs[:50]
        ]
        footprint_results = search_footprints_in_dirs(
            query,
            footprint_lib_dirs,
            max_results=per_kind if kind == "footprint" else per_kind,
            timeout_ms=timeout_ms,
            max_file_bytes=min(max_file_bytes, 500_000),
        )
        all_results.extend(footprint_results)

    if kind in {"model", "all"}:
        model_roots, model_warnings = resolve_model_roots(
            platform,
            project_dir=project_path,
            include_project_local=include_project_local,
            extra_dirs=model_dirs,
        )
        warnings.extend(model_warnings)
        searched_roots["models"] = [str(path) for path in model_roots[:50]]
        model_results = search_models_in_roots(
            query,
            model_roots,
            max_results=per_kind if kind == "model" else per_kind,
            timeout_ms=timeout_ms,
        )
        all_results.extend(model_results)

    if kind == "all":
        all_results.sort(key=lambda item: item.score, reverse=True)
        all_results = all_results[:max_results]

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    result_dicts = [item.to_dict() for item in all_results]
    summary_kind = kind if kind != "all" else "library"
    return {
        "summary": build_summary(query, summary_kind, all_results),
        "query": query,
        "kind": kind,
        "platform": platform,
        "project_dir": str(project_path),
        "searched_roots": searched_roots,
        "results": result_dicts,
        "warnings": warnings,
        "elapsed_ms": elapsed_ms,
    }

import difflib
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


DEFAULT_INFO_MAX_FILE_BYTES = 64_000_000
DEFAULT_MAX_PINS = 200
DEFAULT_MAX_PADS = 300

SYMBOL_COORDINATES = (
    "mm relative to the symbol origin, library Y axis (up positive). "
    "Pin x,y is the wire connection point; orientation (0/90/180/270) "
    "points from that point toward the body; side is where the pin sits. "
    "For a symbol placed at sheet (X, Y) with no rotation or mirror, the "
    "pin's wire point is (X + x, Y - y): schematic y = -library y. "
    "Pins omit style when it is 'line' and hidden when false."
)
FOOTPRINT_COORDINATES = (
    "mm relative to the footprint origin, PCB Y axis (down positive), "
    "footprint unrotated. Pad rotation is in degrees. For a footprint "
    "placed at (X, Y) with rotation 0 on the front side, a pad is at "
    "(X + x, Y + y)."
)

_SEXPR_TOKEN_RE = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
_SEXPR_ESCAPES = {"n": "\n", "t": "\t", "r": "\r"}
_PIN_SIDES = {0: "left", 90: "bottom", 180: "right", 270: "top"}
_STRUCTURED_SYMBOL_PROPERTIES = {
    "Reference": "reference",
    "Value": "value",
    "Footprint": "footprint",
    "Datasheet": "datasheet",
    "Description": "description",
    "ki_description": "description",
    "ki_keywords": "keywords",
    "ki_fp_filters": "fp_filters",
}
_GRAPHIC_TAGS = {"rectangle", "polyline", "circle", "arc", "bezier"}
_FP_SHAPE_TAGS = {
    "fp_line",
    "fp_rect",
    "fp_poly",
    "fp_arc",
    "fp_circle",
    "fp_curve",
}
_EXTENT_LAYERS = ("F.CrtYd", "B.CrtYd", "F.Fab", "B.Fab", "F.SilkS", "B.SilkS")


class LibInfoError(Exception):
    """A lookup failure reported to the caller as JSON."""

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message)
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"success": False, "error": str(self)}
        payload.update(self.details)
        return payload


# --------------------------------------------------------------------------
# S-expression helpers
# --------------------------------------------------------------------------


def _unquote(token: str) -> str:
    body = token[1:-1]
    if "\\" not in body:
        return body
    return re.sub(
        r"\\(.)",
        lambda m: _SEXPR_ESCAPES.get(m.group(1), m.group(1)),
        body,
    )


def parse_sexpr(text: str) -> List[Any]:
    """Parse the first complete s-expression in ``text`` into lists.

    Quoted and bare atoms both become ``str``.
    """
    stack: List[List[Any]] = []
    for match in _SEXPR_TOKEN_RE.finditer(text):
        token = match.group()
        if token == "(":
            node: List[Any] = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError("unbalanced ')' in s-expression")
            done = stack.pop()
            if not stack:
                return done
        elif stack:
            stack[-1].append(_unquote(token) if token[0] == '"' else token)
    raise ValueError("unterminated s-expression")


def sexpr_block_end(text: str, start: int) -> int:
    """Return the index just past the s-expression opening at ``start``."""
    depth = 0
    for match in _SEXPR_TOKEN_RE.finditer(text, start):
        token = match.group()
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
            if depth == 0:
                return match.end()
    return len(text)


def _children(node: List[Any], tag: str) -> List[List[Any]]:
    return [
        child
        for child in node
        if isinstance(child, list) and child and child[0] == tag
    ]


def _child(node: List[Any], tag: str) -> Optional[List[Any]]:
    for child in node:
        if isinstance(child, list) and child and child[0] == tag:
            return child
    return None


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float) -> float:
    rounded = round(value, 4)
    return 0.0 if rounded == 0 else rounded


def _xy(node: Optional[List[Any]]) -> Optional[Tuple[float, float]]:
    if node is None or len(node) < 3:
        return None
    return _num(node[1]), _num(node[2])


def _flag(node: List[Any], tag: str) -> Optional[bool]:
    """Read ``(tag yes|no)`` / ``(tag)`` / bare ``tag``; None if absent."""
    for child in node[1:]:
        if child == tag:
            return True
        if isinstance(child, list) and child and child[0] == tag:
            if len(child) == 1:
                return True
            return child[1] not in ("no", "false")
    return None


def _scalars(node: Optional[List[Any]]) -> List[str]:
    if node is None:
        return []
    return [item for item in node[1:] if isinstance(item, str)]


class _BBox:
    def __init__(self) -> None:
        self.min_x = math.inf
        self.min_y = math.inf
        self.max_x = -math.inf
        self.max_y = -math.inf

    def add(self, x: float, y: float) -> None:
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

    def add_circle(self, cx: float, cy: float, radius: float) -> None:
        self.add(cx - radius, cy - radius)
        self.add(cx + radius, cy + radius)

    def empty(self) -> bool:
        return self.min_x == math.inf

    def to_dict(self) -> Optional[Dict[str, float]]:
        if self.empty():
            return None
        return {
            "min_x": _round(self.min_x),
            "min_y": _round(self.min_y),
            "max_x": _round(self.max_x),
            "max_y": _round(self.max_y),
            "width": _round(self.max_x - self.min_x),
            "height": _round(self.max_y - self.min_y),
        }


def _arc_extent_points(
    start: Tuple[float, float],
    mid: Tuple[float, float],
    end: Tuple[float, float],
) -> List[Tuple[float, float]]:
    """Points bounding a three-point arc (endpoints plus axis crossings)."""
    points = [start, mid, end]
    (ax, ay), (bx, by), (cx, cy) = start, mid, end
    det = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(det) < 1e-12:
        return points
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / det
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / det
    radius = math.hypot(ax - ux, ay - uy)
    tau = 2.0 * math.pi

    def angle(px: float, py: float) -> float:
        return math.atan2(py - uy, px - ux) % tau

    a_start, a_mid, a_end = angle(ax, ay), angle(bx, by), angle(cx, cy)
    sweep_end = (a_end - a_start) % tau
    counter_clockwise = (a_mid - a_start) % tau <= sweep_end
    for k in range(4):
        theta = k * math.pi / 2.0
        if counter_clockwise:
            inside = (theta - a_start) % tau <= sweep_end
        else:
            inside = (theta - a_end) % tau <= (a_start - a_end) % tau
        if inside:
            points.append(
                (ux + radius * math.cos(theta), uy + radius * math.sin(theta))
            )
    return points


def _add_shape_to_bbox(node: List[Any], bbox: _BBox) -> None:
    """Grow ``bbox`` by a symbol graphic or footprint shape node."""
    tag = node[0]
    start = _xy(_child(node, "start"))
    end = _xy(_child(node, "end"))
    if tag in ("circle", "fp_circle"):
        center = _xy(_child(node, "center"))
        radius_node = _child(node, "radius")
        if center is None:
            return
        if radius_node is not None:
            radius = _num(radius_node[1] if len(radius_node) > 1 else 0)
        elif end is not None:
            radius = math.hypot(end[0] - center[0], end[1] - center[1])
        else:
            return
        bbox.add_circle(center[0], center[1], radius)
        return
    if tag in ("arc", "fp_arc"):
        mid = _xy(_child(node, "mid"))
        if start is not None and mid is not None and end is not None:
            for x, y in _arc_extent_points(start, mid, end):
                bbox.add(x, y)
            return
    for point in (start, end):
        if point is not None:
            bbox.add(point[0], point[1])
    pts = _child(node, "pts")
    if pts is not None:
        for item in pts[1:]:
            if not isinstance(item, list) or not item:
                continue
            if item[0] == "xy":
                point = _xy(item)
                if point is not None:
                    bbox.add(point[0], point[1])
            elif item[0] == "arc":
                _add_shape_to_bbox(item, bbox)


def _close_names(name: str, candidates: Sequence[str], limit: int = 10):
    lowered = name.lower()
    close = difflib.get_close_matches(name, candidates, n=limit, cutoff=0.6)
    for candidate in candidates:
        if len(close) >= limit:
            break
        if candidate in close:
            continue
        candidate_lower = candidate.lower()
        if lowered in candidate_lower or candidate_lower in lowered:
            close.append(candidate)
    return close[:limit]


def _read_library_file(path: Path, max_file_bytes: int) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise LibInfoError(f"Cannot read {path}: {exc}") from exc
    if size > max_file_bytes:
        raise LibInfoError(
            f"{path} is {size} bytes, above --max-file-bytes "
            f"{max_file_bytes}."
        )
    return path.read_text(encoding="utf-8", errors="replace")


def _split_identifier(identifier: str, kind: str) -> Tuple[str, str]:
    lib, sep, name = identifier.partition(":")
    if not sep or not lib or not name:
        raise LibInfoError(
            f"{kind} id must look like 'Library:Name', got {identifier!r}."
        )
    return lib, name


# --------------------------------------------------------------------------
# Symbols
# --------------------------------------------------------------------------


def _find_symbol_node(text: str, name: str) -> Optional[List[Any]]:
    pattern = re.compile(r'\(symbol\s+"' + re.escape(name) + r'"')
    match = pattern.search(text)
    if match is None:
        return None
    end = sexpr_block_end(text, match.start())
    return parse_sexpr(text[match.start() : end])


def _symbol_properties(node: List[Any]) -> Dict[str, str]:
    props: Dict[str, str] = {}
    for prop in _children(node, "property"):
        if len(prop) >= 3 and isinstance(prop[1], str):
            props[prop[1]] = prop[2] if isinstance(prop[2], str) else ""
    return props


def _pin_payload(
    pin: List[Any],
    unit: int,
    body_style: int,
) -> Dict[str, Any]:
    at = _child(pin, "at") or ["at", "0", "0", "0"]
    orientation = int(round(_num(at[3] if len(at) > 3 else 0))) % 360
    name_node = _child(pin, "name")
    number_node = _child(pin, "number")
    length_node = _child(pin, "length")
    payload: Dict[str, Any] = {
        "number": (
            number_node[1] if number_node and len(number_node) > 1 else ""
        ),
        "name": name_node[1] if name_node and len(name_node) > 1 else "",
        "type": pin[1] if len(pin) > 1 and isinstance(pin[1], str) else "",
        "style": pin[2] if len(pin) > 2 and isinstance(pin[2], str) else "",
        "unit": unit,
        "body_style": body_style,
        "x": _round(_num(at[1] if len(at) > 1 else 0)),
        "y": _round(_num(at[2] if len(at) > 2 else 0)),
        "orientation": orientation,
        "side": _PIN_SIDES.get(orientation, "other"),
        "length": _round(
            _num(length_node[1] if length_node and len(length_node) > 1 else 0)
        ),
        "hidden": bool(_flag(pin, "hide")),
    }
    alternates = [
        alt[1]
        for alt in _children(pin, "alternate")
        if len(alt) > 1 and isinstance(alt[1], str)
    ]
    if alternates:
        payload["alternates"] = alternates
    # Keep big parts small: the common defaults are left out (see
    # SYMBOL_COORDINATES).
    if payload["style"] == "line":
        del payload["style"]
    if not payload["hidden"]:
        del payload["hidden"]
    return payload


def _collect_symbol_body(
    node: List[Any],
) -> Tuple[List[Dict[str, Any]], Dict[int, str], set, Dict[int, _BBox]]:
    """Pins, unit names, body styles and per-unit bbox of a symbol.

    Unit 0 holds graphics and pins shared by every unit.
    """
    base = str(node[1]).split(":")[-1]
    pins: List[Dict[str, Any]] = []
    unit_names: Dict[int, str] = {}
    body_styles: set = set()
    boxes: Dict[int, _BBox] = {}

    def visit(owner: List[Any], unit: int, style: int) -> None:
        bbox = boxes.setdefault(unit, _BBox())
        for child in owner:
            if not isinstance(child, list) or not child:
                continue
            tag = child[0]
            if tag == "pin":
                payload = _pin_payload(child, unit, style)
                pins.append(payload)
                theta = math.radians(payload["orientation"])
                bbox.add(payload["x"], payload["y"])
                bbox.add(
                    payload["x"] + payload["length"] * math.cos(theta),
                    payload["y"] + payload["length"] * math.sin(theta),
                )
            elif tag in _GRAPHIC_TAGS:
                _add_shape_to_bbox(child, bbox)

    visit(node, 0, 0)
    for sub in _children(node, "symbol"):
        suffix = _unit_suffix(str(sub[1]) if len(sub) > 1 else "", base)
        unit, style = suffix if suffix is not None else (0, 0)
        if style:
            body_styles.add(style)
        unit_name = _child(sub, "unit_name")
        if unit_name is not None and len(unit_name) > 1:
            unit_names[unit] = unit_name[1]
        visit(sub, unit, style)
    return pins, unit_names, body_styles, boxes


def _merged_bbox(boxes: Sequence[Optional[_BBox]]) -> _BBox:
    merged = _BBox()
    for box in boxes:
        if box is not None and not box.empty():
            merged.add(box.min_x, box.min_y)
            merged.add(box.max_x, box.max_y)
    return merged


def _symbol_names(text: str) -> List[str]:
    return [name for name, _s, _e, _u in iter_top_level_symbol_spans(text)]


def symbol_info(
    library_path: str,
    symbol: str,
    *,
    unit: Optional[int] = None,
    pins: Optional[Sequence[str]] = None,
    max_pins: int = DEFAULT_MAX_PINS,
    max_file_bytes: int = DEFAULT_INFO_MAX_FILE_BYTES,
) -> Dict[str, Any]:
    """Describe one symbol: properties, resolved ``extends``, units, pins."""
    path = Path(library_path).expanduser()
    if not path.is_file():
        raise LibInfoError(f"Symbol library not found: {path}")
    text = _read_library_file(path, max_file_bytes)

    name = symbol
    node = _find_symbol_node(text, name)
    if node is None and ":" in name:
        name = name.split(":", 1)[1]
        node = _find_symbol_node(text, name)
    if node is None:
        raise LibInfoError(
            f"Symbol {symbol!r} not found in {path}.",
            library_path=str(path),
            close_matches=_close_names(name, _symbol_names(text)),
        )

    chain = [node]
    seen = {name}
    while True:
        extends = _child(chain[-1], "extends")
        if extends is None or len(extends) < 2:
            break
        parent_name = extends[1]
        if parent_name in seen or len(chain) > 8:
            raise LibInfoError(f"Circular extends chain at {parent_name!r}.")
        seen.add(parent_name)
        parent = _find_symbol_node(text, parent_name)
        if parent is None:
            raise LibInfoError(
                f"{name!r} extends {parent_name!r}, which is not in {path}.",
                library_path=str(path),
            )
        chain.append(parent)

    # Derived symbols override properties; the root owns pins/graphics.
    properties: Dict[str, str] = {}
    for ancestor in reversed(chain):
        properties.update(_symbol_properties(ancestor))
    body_owner = chain[-1]
    all_pins, unit_names, body_styles, boxes = _collect_symbol_body(body_owner)

    def inherited(tag: str) -> Optional[List[Any]]:
        for ancestor in chain:
            found = _child(ancestor, tag)
            if found is not None:
                return found
        return None

    payload: Dict[str, Any] = {
        "success": True,
        "kind": "symbol",
        "library": path.stem,
        "library_path": str(path),
        "name": name,
        "symbol_id": name,
        "identifier": f"{path.stem}:{name}",
    }
    if len(chain) > 1:
        payload["extends_parent"] = str(chain[1][1])
        payload["extends_chain"] = [str(item[1]) for item in chain[1:]]
    other: Dict[str, str] = {}
    for key, value in properties.items():
        field_name = _STRUCTURED_SYMBOL_PROPERTIES.get(key)
        if field_name:
            payload.setdefault(field_name, value)
        else:
            other[key] = value
    if other:
        payload["other_properties"] = other

    unit_count = max([pin["unit"] for pin in all_pins] + [1])
    pin_names = inherited("pin_names")
    pin_numbers = inherited("pin_numbers")
    payload.update(
        {
            "power": inherited("power") is not None,
            "in_bom": _flag(chain[0], "in_bom") is not False,
            "on_board": _flag(chain[0], "on_board") is not False,
            "unit_count": unit_count,
            "body_styles": sorted(body_styles or {1}),
            "has_demorgan": 2 in body_styles,
            "pin_names_hidden": bool(pin_names and _flag(pin_names, "hide")),
            "pin_numbers_hidden": bool(
                pin_numbers and _flag(pin_numbers, "hide")
            ),
            "pin_count": len(all_pins),
            "bbox": _merged_bbox(list(boxes.values())).to_dict(),
            "coordinates": SYMBOL_COORDINATES,
            "y_axis": "library (up positive); schematic y = -y",
        }
    )
    if pin_names is not None:
        offset = _child(pin_names, "offset")
        if offset is not None and len(offset) > 1:
            payload["pin_name_offset"] = _round(_num(offset[1]))
    if unit_count > 1:
        units = []
        for number in range(1, unit_count + 1):
            entry: Dict[str, Any] = {
                "unit": number,
                "pin_count": sum(1 for p in all_pins if p["unit"] == number),
                "bbox": _merged_bbox(
                    [boxes.get(0), boxes.get(number)]
                ).to_dict(),
            }
            if number in unit_names:
                entry["name"] = unit_names[number]
            units.append(entry)
        payload["units"] = units
        payload["common_pin_count"] = sum(
            1 for p in all_pins if p["unit"] == 0
        )

    selected = all_pins
    if unit is not None:
        selected = [p for p in selected if p["unit"] in (0, unit)]
    if pins:
        wanted = {item.lower() for item in pins}
        selected = [
            p
            for p in selected
            if p["number"].lower() in wanted or p["name"].lower() in wanted
        ]
    if 2 not in body_styles:
        for pin in selected:
            pin.pop("body_style", None)

    if len(selected) > max_pins:
        payload["pins_truncated"] = True
        payload["note"] = (
            f"{len(selected)} pins; showing {max_pins}. Narrow with --unit "
            "or --pin, or raise --max-pins."
        )
    elif not selected and (unit is not None or pins):
        payload["note"] = "No pins matched --unit/--pin."
    shown = selected[:max_pins]
    by_name: Dict[str, List[str]] = {}
    for pin in shown:
        by_name.setdefault(pin["name"], []).append(pin["number"])
    payload["pins"] = shown
    payload["pins_by_name"] = by_name
    return payload


def resolve_symbol_library(
    library: str,
    *,
    platform: Platform,
    project_dir: str = ".",
    include_project_local: bool = True,
    symbol_dirs: Optional[Sequence[str]] = None,
) -> Path:
    """Find ``<library>.kicad_sym`` in the roots ``search`` uses."""
    files, _warnings = resolve_symbol_roots(
        platform,
        project_dir=Path(project_dir).expanduser().resolve(),
        include_project_local=include_project_local,
        extra_dirs=symbol_dirs,
    )
    matches = [path for path in files if path.stem == library]
    if matches:
        stock = default_symbol_dir(platform)
        # Explicit and project-local libraries win over stock ones.
        non_stock = [path for path in matches if path.parent != stock]
        return (non_stock or matches)[0]
    raise LibInfoError(
        f"Symbol library {library!r} not found.",
        close_matches=_close_names(
            library, sorted({path.stem for path in files})
        ),
    )


# --------------------------------------------------------------------------
# Footprints
# --------------------------------------------------------------------------


def _pad_payload(pad: List[Any]) -> Tuple[Dict[str, Any], List[float]]:
    at = _child(pad, "at") or ["at", "0", "0"]
    size = _child(pad, "size")
    x = _num(at[1] if len(at) > 1 else 0)
    y = _num(at[2] if len(at) > 2 else 0)
    rotation = _num(at[3] if len(at) > 3 else 0)
    width = _num(size[1]) if size and len(size) > 1 else 0.0
    height = _num(size[2]) if size and len(size) > 2 else width
    payload: Dict[str, Any] = {
        "number": pad[1] if len(pad) > 1 and isinstance(pad[1], str) else "",
        "type": pad[2] if len(pad) > 2 and isinstance(pad[2], str) else "",
        "shape": pad[3] if len(pad) > 3 and isinstance(pad[3], str) else "",
        "x": _round(x),
        "y": _round(y),
        "rotation": _round(rotation),
        "size": [_round(width), _round(height)],
    }
    drill = _child(pad, "drill")
    if drill is not None:
        values = [item for item in drill[1:] if isinstance(item, str)]
        oval = bool(values) and values[0] == "oval"
        numbers = [_round(_num(v)) for v in values if v != "oval"]
        if oval:
            payload["drill"] = {
                "shape": "oval",
                "size": numbers[:2] if len(numbers) > 1 else numbers * 2,
            }
        elif numbers:
            payload["drill"] = numbers[0]
        offset = _xy(_child(drill, "offset"))
        if offset is not None and any(offset):
            payload["drill_offset"] = [_round(offset[0]), _round(offset[1])]
    payload["layers"] = _scalars(_child(pad, "layers"))
    for tag in ("pinfunction", "pintype"):
        node = _child(pad, tag)
        if node is not None and len(node) > 1:
            payload[tag] = node[1]

    # Rotated rectangle corners for the pad envelope.
    theta = math.radians(rotation)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    corners: List[float] = []
    for dx, dy in (
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    ):
        corners.extend(
            (x + dx * cos_t + dy * sin_t, y - dx * sin_t + dy * cos_t)
        )
    return payload, corners


def footprint_info(
    footprint_path: str,
    *,
    max_pads: int = DEFAULT_MAX_PADS,
    max_file_bytes: int = DEFAULT_INFO_MAX_FILE_BYTES,
) -> Dict[str, Any]:
    """Describe one ``.kicad_mod``: pads, courtyard, attributes, models."""
    path = Path(footprint_path).expanduser()
    if not path.is_file():
        raise LibInfoError(f"Footprint file not found: {path}")
    text = _read_library_file(path, max_file_bytes)
    try:
        node = parse_sexpr(text)
    except ValueError as exc:
        raise LibInfoError(f"Cannot parse {path}: {exc}") from exc
    if not node or node[0] not in ("footprint", "module"):
        raise LibInfoError(f"{path} is not a KiCad footprint file.")

    name = str(node[1]) if len(node) > 1 else path.stem
    library = path.parent.name
    if library.endswith(".pretty"):
        library = library[: -len(".pretty")]
    attrs = _scalars(_child(node, "attr"))
    descr = _child(node, "descr")
    tags = _child(node, "tags")
    layer = _child(node, "layer")

    pads: List[Dict[str, Any]] = []
    pad_bbox = _BBox()
    for pad in _children(node, "pad"):
        pad_entry, corners = _pad_payload(pad)
        pads.append(pad_entry)
        for idx in range(0, len(corners), 2):
            pad_bbox.add(corners[idx], corners[idx + 1])

    extents: Dict[str, _BBox] = {}
    for shape in node[1:]:
        if not isinstance(shape, list) or not shape:
            continue
        if shape[0] not in _FP_SHAPE_TAGS:
            continue
        layer_node = _child(shape, "layer")
        if layer_node is None or len(layer_node) < 2:
            continue
        layer_name = layer_node[1]
        if layer_name not in _EXTENT_LAYERS:
            continue
        _add_shape_to_bbox(shape, extents.setdefault(layer_name, _BBox()))

    models = []
    for model in _children(node, "model"):
        entry: Dict[str, Any] = {"path": model[1] if len(model) > 1 else ""}
        for tag in ("offset", "scale", "rotate"):
            holder = _child(model, tag)
            xyz = _child(holder, "xyz") if holder is not None else None
            if xyz is not None:
                entry[tag] = [_round(_num(v)) for v in xyz[1:4]]
        if _flag(model, "hide"):
            entry["hidden"] = True
        models.append(entry)

    pad_numbers: List[str] = []
    for pad_entry in pads:
        number = pad_entry["number"]
        if number and number not in pad_numbers:
            pad_numbers.append(number)
    pad_type = "other"
    if "smd" in attrs:
        pad_type = "smd"
    elif "through_hole" in attrs:
        pad_type = "through_hole"

    courtyard = {
        layer_name: extents[layer_name].to_dict()
        for layer_name in ("F.CrtYd", "B.CrtYd")
        if layer_name in extents
    }
    payload: Dict[str, Any] = {
        "success": True,
        "kind": "footprint",
        "library": library,
        "name": name,
        "footprint_id": name,
        "identifier": f"{library}:{name}",
        "path": str(path),
        "library_path": str(path),
        "description": descr[1] if descr and len(descr) > 1 else "",
        "tags": tags[1] if tags and len(tags) > 1 else "",
        "layer": layer[1] if layer and len(layer) > 1 else "",
        "attributes": attrs,
        "mount": pad_type,
        "pad_count": len(pads),
        "pad_numbers": pad_numbers,
        "courtyard": courtyard or None,
        "extents": {
            layer_name: extents[layer_name].to_dict()
            for layer_name in _EXTENT_LAYERS
            if layer_name in extents and "CrtYd" not in layer_name
        },
        "pad_bbox": pad_bbox.to_dict(),
        "models": models,
        "coordinates": FOOTPRINT_COORDINATES,
    }
    if len(pads) > max_pads:
        payload["pads_truncated"] = True
        payload["note"] = (
            f"{len(pads)} pads; showing {max_pads}. Raise --max-pads."
        )
    payload["pads"] = pads[:max_pads]
    return payload


def resolve_footprint_file(
    footprint_id: Optional[str] = None,
    *,
    library_path: Optional[str] = None,
    footprint: Optional[str] = None,
    platform: Platform = "linux",
    project_dir: str = ".",
    include_project_local: bool = True,
    footprint_dirs: Optional[Sequence[str]] = None,
) -> Path:
    """Resolve a ``.kicad_mod`` from a path, a ``.pretty`` + name, or an id."""
    library = ""
    if footprint_id:
        library, footprint = _split_identifier(footprint_id, "Footprint")
    if not library_path and not library:
        raise LibInfoError("Pass --library-path or --footprint-id Lib:Name.")
    if library_path:
        candidate = Path(library_path).expanduser()
        if candidate.suffix == ".kicad_mod":
            return candidate
        lib_dirs = [candidate]
    else:
        lib_dirs_all, _warnings = resolve_footprint_roots(
            platform,
            project_dir=Path(project_dir).expanduser().resolve(),
            include_project_local=include_project_local,
            extra_dirs=footprint_dirs,
        )
        lib_dirs = [p for p in lib_dirs_all if p.name == f"{library}.pretty"]
        if not lib_dirs:
            raise LibInfoError(
                f"Footprint library {library!r} not found under "
                f"{default_footprint_dir(platform)} or the extra/project "
                "footprint dirs.",
                close_matches=_close_names(
                    library,
                    sorted({p.name[: -len(".pretty")] for p in lib_dirs_all}),
                ),
            )
    if not footprint:
        raise LibInfoError("Pass --footprint NAME or --footprint-id Lib:Name.")
    if footprint.endswith(".kicad_mod"):
        footprint = footprint[: -len(".kicad_mod")]
    if ":" in footprint:
        footprint = footprint.split(":", 1)[1]
    for lib_dir in lib_dirs:
        candidate = lib_dir / f"{footprint}.kicad_mod"
        if candidate.is_file():
            return candidate
    names: List[str] = []
    for lib_dir in lib_dirs:
        try:
            names.extend(
                p.stem for p in lib_dir.iterdir() if p.suffix == ".kicad_mod"
            )
        except OSError:
            continue
    raise LibInfoError(
        f"Footprint {footprint!r} not found in "
        + ", ".join(str(p) for p in lib_dirs),
        close_matches=_close_names(footprint, sorted(names)),
    )

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Sequence



def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search KiCad symbol, footprint, and 3D model libraries."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser(
        "search", help="Search installed and project-local KiCad libraries."
    )
    search.add_argument(
        "--kind",
        choices=["symbol", "footprint", "model", "all"],
        default="all",
        help="Library kind to search.",
    )
    search.add_argument("--query", required=True, help="Search query.")
    search.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        required=True,
        help="Host platform for default KiCad install paths.",
    )
    search.add_argument(
        "--project-dir",
        default=".",
        help="Project root used for project-local libraries.",
    )
    search.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of results to return.",
    )
    search.add_argument(
        "--timeout-ms",
        type=int,
        default=30000,
        help="Soft timeout budget in milliseconds.",
    )
    search.add_argument(
        "--max-file-bytes",
        type=int,
        default=32_000_000,
        help="Maximum bytes to read from a single library file.",
    )
    search.add_argument(
        "--symbol-dir",
        action="append",
        default=[],
        help="Extra symbol file or directory to search.",
    )
    search.add_argument(
        "--footprint-dir",
        action="append",
        default=[],
        help="Extra footprint .pretty directory to search.",
    )
    search.add_argument(
        "--model-dir",
        action="append",
        default=[],
        help="Extra 3D model root directory to search.",
    )
    search.add_argument(
        "--no-project-local",
        action="store_true",
        help="Skip project-local symbol, footprint, and model libraries.",
    )

    symbol = subparsers.add_parser(
        "symbol-info",
        help=(
            "Pins (number, name, type, position, orientation), units, "
            "extends and properties of one symbol."
        ),
    )
    symbol_target = symbol.add_mutually_exclusive_group(required=True)
    symbol_target.add_argument(
        "--library-path",
        help="Path to the .kicad_sym file (search result library_path).",
    )
    symbol_target.add_argument(
        "--symbol-id",
        help="Library:Name, resolved against the same dirs as search.",
    )
    symbol.add_argument(
        "--symbol",
        help="Symbol name inside --library-path (search result symbol_id).",
    )
    symbol.add_argument(
        "--unit",
        type=int,
        help="Only pins of this unit (plus pins common to all units).",
    )
    symbol.add_argument(
        "--pin",
        action="append",
        default=[],
        help="Only this pin number or name (repeatable).",
    )
    symbol.add_argument(
        "--max-pins",
        type=int,
        default=DEFAULT_MAX_PINS,
        help="Maximum pins to list.",
    )
    _add_info_root_args(symbol, "--symbol-dir", "Extra symbol file or dir.")

    footprint = subparsers.add_parser(
        "footprint-info",
        help=("Pads, courtyard, attributes and 3D models of one footprint."),
    )
    footprint_target = footprint.add_mutually_exclusive_group(required=True)
    footprint_target.add_argument(
        "--library-path",
        help=(
            "A .pretty dir (with --footprint) or a .kicad_mod file "
            "(search result library_path)."
        ),
    )
    footprint_target.add_argument(
        "--footprint-id",
        help="Library:Name, resolved against the same dirs as search.",
    )
    footprint.add_argument(
        "--footprint",
        help="Footprint name inside the .pretty dir.",
    )
    footprint.add_argument(
        "--max-pads",
        type=int,
        default=DEFAULT_MAX_PADS,
        help="Maximum pads to list.",
    )
    _add_info_root_args(
        footprint, "--footprint-dir", "Extra footprint .pretty dir or root."
    )

    selftest = subparsers.add_parser(
        "selftest",
        help="Validate standalone script imports, parser wiring, and defaults.",
    )
    selftest.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        required=True,
        help="Host platform for default KiCad install paths.",
    )
    selftest.add_argument(
        "--project-dir",
        default=".",
        help="Project root used for project-local library resolution checks.",
    )
    return parser


def _add_info_root_args(
    parser: argparse.ArgumentParser, extra_flag: str, extra_help: str
) -> None:
    parser.add_argument(
        "--platform",
        choices=["win", "mac", "linux"],
        default=_host_platform(),
        help="Host platform for default KiCad install paths.",
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project root used for project-local libraries.",
    )
    parser.add_argument(
        extra_flag, action="append", default=[], help=extra_help
    )
    parser.add_argument(
        "--no-project-local",
        action="store_true",
        help="Skip project-local libraries when resolving ids.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_INFO_MAX_FILE_BYTES,
        help="Refuse library files larger than this.",
    )


def _host_platform() -> str:
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def _run_symbol_info(args: argparse.Namespace) -> Dict[str, Any]:
    if args.symbol_id:
        library, _sep, name = args.symbol_id.partition(":")
        if not library or not name:
            raise LibInfoError(
                "--symbol-id must look like 'Library:Name', got "
                f"{args.symbol_id!r}."
            )
        library_path = str(
            resolve_symbol_library(
                library,
                platform=args.platform,
                project_dir=args.project_dir,
                include_project_local=not args.no_project_local,
                symbol_dirs=_non_empty(args.symbol_dir),
            )
        )
    else:
        library_path = args.library_path
        name = args.symbol
        if not name:
            raise LibInfoError("Pass --symbol NAME with --library-path.")
    return symbol_info(
        library_path,
        name,
        unit=args.unit,
        pins=_non_empty(args.pin),
        max_pins=args.max_pins,
        max_file_bytes=args.max_file_bytes,
    )


def _run_footprint_info(args: argparse.Namespace) -> Dict[str, Any]:
    path = resolve_footprint_file(
        args.footprint_id,
        library_path=args.library_path,
        footprint=args.footprint,
        platform=args.platform,
        project_dir=args.project_dir,
        include_project_local=not args.no_project_local,
        footprint_dirs=_non_empty(args.footprint_dir),
    )
    return footprint_info(
        str(path),
        max_pads=args.max_pads,
        max_file_bytes=args.max_file_bytes,
    )


def format_info_json(payload: Dict[str, Any]) -> str:
    """Pretty JSON with one line per pin/pad row and per map entry."""
    lines = ["{"]
    items = list(payload.items())
    for index, (key, value) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        label = json.dumps(key)
        if (
            isinstance(value, list)
            and value
            and all(isinstance(item, dict) for item in value)
        ):
            rows = ",\n".join("    " + json.dumps(item) for item in value)
            lines.append(f"  {label}: [\n{rows}\n  ]{comma}")
        elif isinstance(value, dict) and value:
            rows = ",\n".join(
                f"    {json.dumps(k)}: {json.dumps(v)}"
                for k, v in value.items()
            )
            lines.append(f"  {label}: {{\n{rows}\n  }}{comma}")
        else:
            lines.append(f"  {label}: {json.dumps(value)}{comma}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def run_selftest(platform: Platform, project_dir: str) -> dict:
    payload = run_search(
        kind="symbol",
        query="__copperpilot_selftest__",
        platform=platform,
        project_dir=project_dir,
        include_project_local=False,
        symbol_dirs=[],
        footprint_dirs=[],
        model_dirs=[],
        max_results=1,
        timeout_ms=1000,
        max_file_bytes=1024,
    )
    return {
        "success": True,
        "platform": platform,
        "project_dir": project_dir,
        "defaults": {
            "symbol_dir": str(default_symbol_dir(platform)),
            "footprint_dir": str(default_footprint_dir(platform)),
            "model_dir": str(default_model_dir(platform)),
        },
        "search_ok": isinstance(payload, dict)
        and payload.get("kind") == "symbol",
        "info_ok": _selftest_info(),
    }


def _selftest_info() -> bool:
    probe = parse_sexpr(
        '(symbol "P" (symbol "P_1_1" (pin input line (at 1 2 90) '
        '(length 2.54) (name "A") (number "1"))))'
    )
    pins = _collect_symbol_body(probe)[0]
    return len(pins) == 1 and pins[0]["orientation"] == 90


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "selftest":
        payload = run_selftest(args.platform, args.project_dir)
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if payload.get("success") and payload.get("info_ok") else 1

    if args.command in ("symbol-info", "footprint-info"):
        runner = (
            _run_symbol_info
            if args.command == "symbol-info"
            else _run_footprint_info
        )
        try:
            payload = runner(args)
        except LibInfoError as exc:
            payload = exc.to_dict()
        except (OSError, ValueError) as exc:
            payload = {"success": False, "error": str(exc)}
        sys.stdout.write(format_info_json(payload))
        return 0 if payload.get("success") else 1

    if args.command != "search":
        parser.error(f"Unsupported command: {args.command}")
        return 2

    payload = run_search(
        kind=args.kind,
        query=args.query,
        platform=args.platform,
        project_dir=args.project_dir,
        include_project_local=not args.no_project_local,
        symbol_dirs=_non_empty(args.symbol_dir),
        footprint_dirs=_non_empty(args.footprint_dir),
        model_dirs=_non_empty(args.model_dir),
        max_results=args.max_results,
        timeout_ms=args.timeout_ms,
        max_file_bytes=args.max_file_bytes,
    )
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _non_empty(values: List[str]) -> Optional[List[str]]:
    cleaned = [value for value in values if value]
    return cleaned or None


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
