#!/usr/bin/env python3
"""Print compact FreeRouting JSON summary without multi-MB drc_summary dump."""

import json
import sys
from pathlib import Path


def main():
    p = Path(sys.argv[1])
    s = p.read_text().lstrip()
    d, _ = json.JSONDecoder().raw_decode(s)
    ng = d.get("net_group") or {}
    ntc = ng.get("non_target_copper") or {}
    out = {
        "status": d.get("status"),
        "error": d.get("error"),
        "segments_before": d.get("segment_count_before"),
        "segments_after": d.get("segment_count_after"),
        "freerouting_telemetry": d.get("freerouting_telemetry"),
        "decision": ng.get("decision"),
        "reasons": ng.get("reasons"),
        "non_target_copper_status": ntc.get("status"),
        "changed_nets_keys": list((ntc.get("changed_nets") or {}).keys()),
        "target_items_added": ntc.get("target_items_added"),
        "drc_delta": ng.get("drc_delta"),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
