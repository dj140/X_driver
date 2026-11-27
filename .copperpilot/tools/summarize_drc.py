#!/usr/bin/env python3
import sys, json
from collections import Counter

d = json.load(open(sys.argv[1]))
c = Counter((v["severity"], v["type"]) for v in d["violations"])
errs = sum(v for (s, _), v in c.items() if s == "error")
warns = sum(v for (s, _), v in c.items() if s == "warning")
label = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
print(f"{label}: errors={errs}, warnings={warns}, total={len(d['violations'])}, unconnected={len(d['unconnected_items'])}")
for (s, t), cnt in sorted(c.items()):
    print(f"  {s:8s} {t:28s}: {cnt}")
