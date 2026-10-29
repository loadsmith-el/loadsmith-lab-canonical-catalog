#!/usr/bin/env python3
"""Validate oracle-to-jsonl-clob: every CLOB is the query's 4000 x's, 4000 y's
and lob_roundtrip's own text (empty for its NULL row) — whole, not cut at 4000
bytes."""
import json
import sys
from pathlib import Path

TAILS = {
    1: "the quick brown fox jumps over the lazy dog",
    2: "lorem ipsum dolor sit amet, consectetur adipiscing elit",
    3: "",
}
out = Path(sys.argv[1] if len(sys.argv) > 1 else "/output")
rows = [json.loads(line) for line in (out / "lob.jsonl").read_text().splitlines() if line]
errors = []
if sorted(int(r["ID"]) for r in rows) != [1, 2, 3]:
    errors.append(f"ids: {[r['ID'] for r in rows]}")
for r in rows:
    want = "x" * 4000 + "y" * 4000 + TAILS[int(r["ID"])]
    got = r["CLOB_DATA"]
    if got != want:
        errors.append(f"id {r['ID']}: {len(got or '')} chars, want {len(want)}")
for e in errors:
    print(f"FAIL: {e}")
print("OK" if not errors else f"FAILED ({len(errors)} problem(s))")
sys.exit(0 if not errors else 1)
