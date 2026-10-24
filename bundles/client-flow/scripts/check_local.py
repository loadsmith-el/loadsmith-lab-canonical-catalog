#!/usr/bin/env python3
"""Validate what the local-copy sink delivered (bundle client-flow).

The cases deliver to <output>/delivered. For the case in
$LOADSMITH_LAB_CASE_NAME this checks:
  - every file is <YYYY-MM-DD>/<run id>/events.<n>.snappy.parquet (the
    default `key`), with no temp file left behind;
  - the number of distinct run prefixes (a resumed run adds none);
  - every id of the source is there, and how many times rows were read
    twice: exactly (`dups`), or only reported (`dups: None`, a partitioned
    load resumed after a failure re-reads its partitions in progress).
"""
import os
import re
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

CASES = {
    "postgres-to-parquet-localcopy-runs": {"id": "id", "runs": 2, "unique": 100_010, "dups": 0},
    "postgres-to-parquet-localcopy-resume-run": {"id": "id", "runs": 1, "unique": 100_000, "dups": 1},
    "postgres-to-parquet-localcopy-partitioned-resume": {"id": "id", "runs": 1, "unique": 100_000, "dups": None},
    "postgres-to-parquet-localcopy-partitioned-restart": {"id": "id", "runs": 1, "unique": 100_000, "dups": 0},
    "oracle-to-parquet-localcopy-partitioned-resume": {"id": "ID", "runs": 1, "unique": 100_000, "dups": None},
}

case = os.environ.get("LOADSMITH_LAB_CASE_NAME", "").split("/")[-1]
if case not in CASES:
    print(f"FAIL: no expectations for case {case!r}")
    sys.exit(1)
want = CASES[case]
out = Path(sys.argv[1] if len(sys.argv) > 1 else "/output")
root = out / "delivered"
errors = []

files = sorted(p for p in root.rglob("*") if p.is_file()) if root.exists() else []
name_re = re.compile(r"(\d{4}-\d{2}-\d{2})/(\d+-\d+)/events\.\d{8}\.snappy\.parquet")
runs = set()
tables = []
for p in files:
    rel = p.relative_to(root).as_posix()
    m = name_re.fullmatch(rel)
    if not m:
        errors.append(f"unexpected file {rel!r}")
        continue
    runs.add(m.group(2))
    tables.append(pq.read_table(p, columns=[want["id"]]))
print(f"{len(files)} file(s) under delivered/, {len(runs)} run prefix(es)")

if not tables:
    errors.append("no Parquet files delivered")
if len(runs) != want["runs"]:
    errors.append(f"expected {want['runs']} run prefix(es), got {len(runs)}: {sorted(runs)}")
if tables:
    ids = pa.concat_tables(tables).column(want["id"]).to_pylist()
    unique = len(set(ids))
    dups = len(ids) - unique
    print(f"{len(ids)} rows, {unique} unique ids, {dups} read twice")
    if unique != want["unique"]:
        errors.append(f"expected {want['unique']} unique ids, got {unique}")
    if want["dups"] is not None and dups != want["dups"]:
        errors.append(f"expected {want['dups']} id(s) read twice, got {dups}")

for e in errors:
    print(f"FAIL: {e}")
print("OK" if not errors else f"FAILED ({len(errors)} problem(s))")
sys.exit(0 if not errors else 1)
