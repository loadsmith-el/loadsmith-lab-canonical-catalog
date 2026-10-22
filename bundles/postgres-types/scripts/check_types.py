#!/usr/bin/env python3
"""Validate the postgres source's type decoding (postgres-to-parquet-types).

Opens types.snappy.parquet and asserts, against the type_coverage fixture
(lab-postgres-15/03_type_coverage.sql — keep the two in sync):
  - the Arrow schema (e.g. timestamptz → timestamp[ms, tz=UTC], date[] → list<date32>);
  - the decoded values, row by row.
Dates/timestamps are compared as integers (days / ms since the Unix epoch) because
Python's datetime can't represent the BC values. Timestamps are millisecond
precision, so the fixture's microseconds are truncated. numeric(10,2) is an exact
decimal128(10, 2); the unconstrained c_numeric holds values no 38-digit decimal
fits (a 39-digit value, NaN in the array), so the case's query reads it ::text.
"""
import math
import sys
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def days(y, m, d):
    """Days since 1970-01-01 in the proleptic Gregorian calendar (year 0 = 1 BC)."""
    y -= m <= 2
    era = y // 400  # floor division (Hinnant's C version truncates and adjusts)
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def ms(y, mo, d, h=0, mi=0, s=0, milli=0):
    return ((days(y, mo, d) * 24 + h) * 60 + mi) * 60_000 + s * 1000 + milli


TS = pa.timestamp("ms")
TSZ = pa.timestamp("ms", tz="UTC")
SCHEMA = {
    "id": pa.int32(), "c_int2": pa.int32(), "c_int4": pa.int32(), "c_int8": pa.int64(),
    "c_float4": pa.float32(), "c_float8": pa.float64(),
    "c_numeric": pa.string(), "c_numeric_10_2": pa.decimal128(10, 2), "c_bool": pa.bool_(),
    "c_text": pa.string(), "c_varchar": pa.string(), "c_char": pa.string(),
    "c_date": pa.date32(), "c_timestamp": TS, "c_timestamptz": TSZ,
    "c_time": pa.string(), "c_timetz": pa.string(), "c_interval": pa.string(),
    "c_uuid": pa.string(), "c_json": pa.string(), "c_jsonb": pa.string(),
    "c_inet": pa.string(), "c_bytea": pa.binary(),
    "c_int4_arr": pa.list_(pa.int32()), "c_text_arr": pa.list_(pa.string()),
    "c_numeric_arr": pa.list_(pa.string()), "c_date_arr": pa.list_(pa.date32()),
    "c_timestamptz_arr": pa.list_(TSZ), "c_bytea_arr": pa.list_(pa.binary()),
}

NAN = object()  # sentinel: the value must be NaN
INF = float("inf")

# Expected values per row (temporal columns as epoch days / ms).
EXPECTED = {
    1: {
        "c_int2": 12, "c_int4": 123456, "c_int8": 9007199254740993,
        "c_float4": 1.5, "c_float8": 2.25,
        "c_numeric": "12345.6789", "c_numeric_10_2": Decimal("99.95"), "c_bool": True,
        "c_text": "hello", "c_varchar": "varchar", "c_char": "abc",
        "c_date": days(2024, 1, 15),
        "c_timestamp": ms(2024, 1, 15, 12, 30, 45, 123),
        "c_timestamptz": ms(2024, 1, 15, 12, 30, 45, 123),
        "c_time": "12:30:45", "c_timetz": "12:30:45+02", "c_interval": "1 day 02:03:04",
        "c_uuid": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "c_json": '{"k": "v"}', "c_jsonb": '{"k": "v"}', "c_inet": "192.168.0.1/24",
        "c_bytea": b"\xde\xad\xbe\xef",
        "c_int4_arr": [1, 2, None, 4], "c_text_arr": ["a", "b c", 'say "hi"'],
        "c_numeric_arr": ["1.5", None, "-2"],
        "c_date_arr": [days(2024, 1, 15), None, days(1999, 12, 31)],
        "c_timestamptz_arr": [ms(2024, 1, 15, 12, 30, 45), ms(2000, 1, 1)],
        "c_bytea_arr": [b"\xde\xad", b"\xbe\xef"],
    },
    2: {
        "c_int2": -12, "c_int4": -123456, "c_int8": -9007199254740993,
        "c_float4": -1.5, "c_float8": -2.25,
        "c_numeric": "-0.000001", "c_numeric_10_2": Decimal("-99.95"), "c_bool": False,
        "c_text": "", "c_varchar": "ção ✓", "c_char": "x  ",
        "c_date": 0,
        "c_timestamp": -1,  # 1969-12-31 23:59:59.999
        # '2024-06-30 23:59:59.999-03' → 2024-07-01 02:59:59.999 UTC
        "c_timestamptz": ms(2024, 7, 1, 2, 59, 59, 999),
        "c_time": "00:00:00", "c_timetz": "23:59:59-05:30", "c_interval": "-1 mons",
        "c_uuid": "00000000-0000-0000-0000-000000000000",
        "c_json": "[]", "c_jsonb": "[1, 2]", "c_inet": "::1",
        "c_bytea": b"",
        "c_int4_arr": [], "c_text_arr": [], "c_numeric_arr": [],
        "c_date_arr": [], "c_timestamptz_arr": [], "c_bytea_arr": [],
    },
    3: {
        "c_int2": 32767, "c_int4": 2147483647, "c_int8": 9223372036854775807,
        "c_float4": NAN, "c_float8": INF,
        "c_numeric": "123456789012345678901234567890.123456789",
        "c_numeric_10_2": Decimal("-12345678.99"), "c_bool": None,
        "c_text": "tab\tand\nnewline", "c_varchar": None, "c_char": None,
        "c_date": days(-43, 3, 15),  # 0044-03-15 BC
        "c_timestamp": ms(-43, 3, 15, 12),
        # rendered '0001-01-01 05:53:28+05:53:28' (LMT) in Asia/Kolkata
        "c_timestamptz": ms(1, 1, 1),
        "c_time": "24:00:00", "c_timetz": None, "c_interval": "1 year 2 mons 3 days",
        "c_uuid": None, "c_json": "null", "c_jsonb": '{"nested": {"a": [1, 2]}}',
        "c_inet": None,
        "c_bytea": b"\x00\xff",
        "c_int4_arr": [-2147483648], "c_text_arr": [None], "c_numeric_arr": ["NaN"],
        "c_date_arr": [days(-43, 3, 15)], "c_timestamptz_arr": [None], "c_bytea_arr": [None],
    },
    4: {name: None for name in SCHEMA if name != "id"},
}


def as_ints(col):
    """Temporal columns → epoch integers (dates: days, timestamps: ms)."""
    t = col.type
    if pa.types.is_list(t):
        inner = t.value_type
        if pa.types.is_date32(inner):
            return col.cast(pa.list_(pa.int32()))
        if pa.types.is_timestamp(inner):
            return col.cast(pa.list_(pa.int64()))
        return col
    if pa.types.is_date32(t):
        return col.cast(pa.int32())
    if pa.types.is_timestamp(t):
        return col.cast(pa.int64())
    return col


def same(got, want):
    if want is NAN:
        return isinstance(got, float) and math.isnan(got)
    return got == want


out = Path(sys.argv[1] if len(sys.argv) > 1 else "/output")
path = out / "types.snappy.parquet"
if not path.exists():
    print(f"FAIL: {path} not found (have: {[p.name for p in out.iterdir()]})")
    sys.exit(1)

table = pq.read_table(path)
errors = []

for name, want in SCHEMA.items():
    if name not in table.column_names:
        errors.append(f"missing column {name}")
    elif table.schema.field(name).type != want:
        errors.append(f"{name}: type {table.schema.field(name).type}, want {want}")

if table.num_rows != 4:
    errors.append(f"expected 4 rows, got {table.num_rows}")

if not errors:
    cols = {name: as_ints(table.column(name)).to_pylist() for name in SCHEMA}
    for i, row_id in enumerate(cols["id"]):
        for name, want in EXPECTED[row_id].items():
            got = cols[name][i]
            if not same(got, want):
                errors.append(f"row {row_id} {name}: got {got!r}, want {want!r}")

for e in errors:
    print(f"FAIL: {e}")
print("OK" if not errors else f"FAILED ({len(errors)} problem(s))")
sys.exit(0 if not errors else 1)
