#!/usr/bin/env python3
"""Runs every case in cases.json through scripts/check.py and checks the expected result.

A case expects "pass" (no blocks, no warns), or "block"/"warn" on its named vector.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check", ROOT / "linkedin-algorithm/scripts/check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

cases = json.loads((Path(__file__).parent / "cases.json").read_text())
failed = 0
for c in cases:
    text = c["text"].replace("LONGBODY", "One signal per account, one person who decides, one note. " * 40)
    a = c["args"]
    F = check.check(text, a.get("reader", ""), a.get("headline", ""), a.get("posted_today", ""))
    if c["expect"] == "pass":
        ok = not F
    else:
        ok = any(f["vector"] == c["vector"] and f["severity"] == c["expect"] for f in F)
    failed += not ok
    print(f"{'ok  ' if ok else 'FAIL'}  vector {c['vector']:<5} expect {c['expect']:<5}  {c['name']}")
    if not ok:
        for f in F:
            print(f"        got {f['severity']} on {f['vector']}: {f['detail']}")
print(f"\n{len(cases) - failed}/{len(cases)} passed")
sys.exit(1 if failed else 0)
