#!/usr/bin/env python3
"""Validate what the s3 sink delivered (bundle client-flow).

The lab-s3 simulator keeps objects as plain files at <output>/s3/<bucket>/<key>
(the case mounts it with `output_mount`). For the case in
$LOADSMITH_LAB_CASE_NAME this checks:
  - every key is <prefix>/<YYYY-MM-DD>/<run id>/<file>.parquet;
  - the number of distinct run prefixes (one per run of the case);
  - total rows and unique ids (nothing lost, nothing duplicated);
  - the numeric columns' Arrow types: integers and exact decimals, never
    strings (Oracle NUMBER(p,s) / Postgres DECIMAL(p,s) must stay numbers).
"""
import os
import re
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

DEC = pa.decimal128
# Per source dialect: column → expected Arrow type.
TYPES = {
    "postgres": {
        "event_sequence": pa.int64(), "reading_int": pa.int32(), "reading_bigint": pa.int64(),
        "reading_decimal": DEC(18, 6), "reading_double": pa.float64(), "status_code": pa.int32(),
        "latitude": DEC(9, 6), "longitude": DEC(9, 6), "altitude_km": DEC(12, 3),
        "battery_percent": DEC(5, 2), "reading_bool": pa.bool_(), "is_anomaly": pa.bool_(),
    },
    "oracle": {
        # NUMBER(19) is past int64's 18 guaranteed digits: an exact decimal.
        "EVENT_SEQUENCE": DEC(19, 0), "READING_INT": pa.int64(), "READING_BIGINT": DEC(19, 0),
        "READING_DECIMAL": DEC(18, 6), "READING_DOUBLE": pa.float64(), "STATUS_CODE": pa.int32(),
        "LATITUDE": DEC(9, 6), "LONGITUDE": DEC(9, 6), "ALTITUDE_KM": DEC(12, 3),
        "BATTERY_PERCENT": DEC(5, 2), "READING_BOOL": pa.int32(), "IS_ANOMALY": pa.int32(),
    },
}

CASES = {
    "postgres-to-s3-parquet": {"prefix": "raw/events", "dialect": "postgres", "runs": 1, "rows": 100_000},
    "postgres-to-s3-parquet-incremental": {
        "prefix": "raw/postgres-events", "dialect": "postgres", "runs": 2, "rows": 100_010,
    },
    "oracle-to-s3-parquet-incremental": {
        "prefix": "raw/oracle-events", "dialect": "oracle", "runs": 2, "rows": 100_010,
    },
}

case = os.environ.get("LOADSMITH_LAB_CASE_NAME", "").split("/")[-1]
if case not in CASES:
    print(f"FAIL: no expectations for case {case!r}")
    sys.exit(1)
want = CASES[case]
out = Path(sys.argv[1] if len(sys.argv) > 1 else "/output")
root = out / "s3" / "lake"
errors = []

objects = sorted(p for p in root.rglob("*") if p.is_file()) if root.exists() else []
key_re = re.compile(re.escape(want["prefix"]) + r"/(\d{4}-\d{2}-\d{2})/(\d+-\d+)/[^/]+\.parquet")
runs = set()
tables = []
for p in objects:
    key = p.relative_to(root).as_posix()
    m = key_re.fullmatch(key)
    if not m:
        errors.append(f"unexpected object key {key!r}")
        continue
    runs.add(m.group(2))
    tables.append(pq.read_table(p))
print(f"{len(objects)} object(s) under s3://lake/{want['prefix']}/, {len(runs)} run prefix(es)")

if not tables:
    errors.append("no Parquet objects delivered")
if len(runs) != want["runs"]:
    errors.append(f"expected {want['runs']} run prefix(es), got {len(runs)}: {sorted(runs)}")

if tables:
    table = pa.concat_tables(tables)
    id_col = "ID" if want["dialect"] == "oracle" else "id"
    ids = table.column(id_col).to_pylist()
    if len(ids) != want["rows"]:
        errors.append(f"expected {want['rows']} rows, got {len(ids)}")
    if len(set(ids)) != len(ids):
        errors.append(f"{len(ids) - len(set(ids))} duplicated id(s)")
    for name, typ in TYPES[want["dialect"]].items():
        if name not in table.column_names:
            errors.append(f"missing column {name}")
        elif table.schema.field(name).type != typ:
            errors.append(f"{name}: type {table.schema.field(name).type}, want {typ}")

for e in errors:
    print(f"FAIL: {e}")
print("OK" if not errors else f"FAILED ({len(errors)} problem(s))")
sys.exit(0 if not errors else 1)
