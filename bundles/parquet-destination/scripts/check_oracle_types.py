#!/usr/bin/env python3
"""Validate the oracle source's INTERVAL decoding (oracle-to-parquet-types).

Opens types.snappy.parquet: every interval column is the exact
struct<months: int32, days: int32, nanoseconds: int64> the parquet destination
writes for an Arrow Interval(MonthDayNano), with the values the case's query
computes from SEQ (keep the two in sync).
"""
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

STRUCT = pa.struct([
    pa.field("months", pa.int32(), nullable=False),
    pa.field("days", pa.int32(), nullable=False),
    pa.field("nanoseconds", pa.int64(), nullable=False),
])
NS = 1_000_000_000


def ds(total_ns):
    """A DAY TO SECOND value: whole days, the rest in nanoseconds (one sign)."""
    sign = -1 if total_ns < 0 else 1
    days, rest = divmod(abs(total_ns), 86_400 * NS)
    return {"months": 0, "days": sign * days, "nanoseconds": sign * rest}


def expected(seq):
    return {
        "YM": {"months": seq * 7 - 20, "days": 0, "nanoseconds": 0},
        "DS": ds(seq * 90061 * NS + 123_456_789),
        "DS_NEG": ds(-seq * 3_600_500_000_000),
        "DS_NULL": None,
    }


out = Path(sys.argv[1] if len(sys.argv) > 1 else "/output")
path = out / "types.snappy.parquet"
if not path.exists():
    print(f"FAIL: {path} not found")
    sys.exit(1)
table = pq.read_table(path)
errors = []
for name in ["YM", "DS", "DS_NEG", "DS_NULL"]:
    got = table.schema.field(name).type if name in table.column_names else None
    if got != STRUCT:
        errors.append(f"{name}: type {got}, want {STRUCT}")
if not errors:
    rows = table.to_pylist()
    if sorted(int(r["SEQ"]) for r in rows) != [1, 2, 3, 4, 5]:
        errors.append(f"SEQ: {[r['SEQ'] for r in rows]}")
    for r in rows:
        for name, want in expected(int(r["SEQ"])).items():
            if r[name] != want:
                errors.append(f"SEQ {r['SEQ']} {name}: got {r[name]}, want {want}")
for e in errors:
    print(f"FAIL: {e}")
print("OK" if not errors else f"FAILED ({len(errors)} problem(s))")
sys.exit(0 if not errors else 1)
