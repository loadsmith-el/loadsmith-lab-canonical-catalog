# loadsmith-lab-canonical-catalog

> 📖 **Full documentation:** <https://loadsmith-el.github.io/loadsmith-lab-canonical-catalog/>

The **`catalog` origin** for [loadsmith-lab](https://github.com/loadsmith-el/loadsmith-lab): test cases and
bundles for [Loadsmith](https://github.com/loadsmith-el/loadsmith). This repo ships no code — just
declarative YAML (and the small Dockerfiles bundles need for their hook
scripts).

## Layout

```text
loadsmith-lab.toml      manifest: name → description, per category
cases/<name>/
  case.yaml              services + readiness + the `expect` block
  pipeline.yaml          the Loadsmith pipeline under test
bundles/<name>/
  bundle.yaml            a sequence of cases + optional setup/validate/cleanup hooks
  Dockerfile             builds the image the hooks run in (always required)
  scripts/               setup/validate/cleanup scripts (optional)
```

Hooks are optional per entry. A bundle with no hooks (e.g. `tls-spike`) still
needs a `Dockerfile` — a one-line `FROM debian:12-slim` stub is enough, because
the lab always builds the hook image.

Add an entry under `[cases]` or `[bundles]` in `loadsmith-lab.toml` whenever you
add content — that manifest is what `loadsmith-lab list`/`bundle list` and
`origin show catalog` read.

## Cases

| Case | Description |
|---|---|
| `postgres-to-jsonl` | Reads 100k rows from PostgreSQL and writes them to JSONL (content/type smoke test) |
| `postgres-to-jsonl-tls-require` | Reads 100k rows from Postgres over TLS (`mode: require`) — rustls handshake validation |
| `postgres-to-null-5M` | Reads 5M rows into the null sink — pure read/pump throughput |
| `postgres-to-null-15M` | Reads 15M rows into the null sink — pure read/pump throughput |
| `postgres-to-parquet-single` | Reads 100k rows and writes a single Parquet file |
| `postgres-to-parquet-chunked` | Reads 100k rows and writes multiple chunked Parquet files |
| `postgres-to-parquet-localcopy` | Chunked Parquet to a staging dir, delivered via the local-copy sink |
| `postgres-to-parquet-localcopy-resume` | Crashes the sink mid-delivery and asserts the core respawns it and delivers every chunk |
| `postgres-to-parquet-types` | Type coverage: `timestamptz` (non-UTC session), BC dates, NaN, `numeric`, arrays, an all-NULL row → Parquet (values asserted by the `postgres-types` bundle) |
| `postgres-to-postgres-types` | Round-trips the `type_coverage` scalar columns Postgres→Postgres (append COPY, non-UTC sessions on both sides) |
| `mysql-to-jsonl` | Reads 100k rows from MySQL and writes them to JSONL (content/type smoke test) |
| `mysql-to-jsonl-native` | Reads 100k rows from MySQL via the legacy `mysql_native_password` auth plugin — auth-mode coverage |
| `mysql-to-jsonl-tls-require` | Reads 100k rows from MySQL over TLS (`mode: require`) — rustls handshake validation |
| `mysql-to-mysql` | Loads 100k rows into MySQL (`append` mode) — destination smoke test |
| `mysql-to-mysql-staged-merge` | Loads 100k rows into MySQL via `merge` (ON DUPLICATE KEY upsert by `id`) |
| `oracle-to-jsonl` | Reads 100k wide rows (34 cols) from Oracle and writes them to JSONL (content/type smoke test) |
| `oracle-to-jsonl-tls` | Reads 100k rows from Oracle over TCPS — `tls.mode: verify-full`, chain + hostname verified against the lab CA (`root_cert`) |
| `oracle-to-jsonl-incremental` | Incremental watermark read (cursor `event_sequence > 50000`) — reads the upper 50k |
| `oracle-to-oracle` | Loads 100k rows into Oracle (`append` array INSERT) — destination smoke test |
| `oracle-to-oracle-staged-merge` | Loads 100k rows into Oracle via `merge` (staging GTT + one set-based `MERGE` by `id`) |
| `oracle-to-oracle-lob` | Round-trips RAW/BLOB/CLOB columns Oracle→Oracle — binary/LOB type coverage |
| `oracle-to-oracle-nls` | Loads with a comma-decimal `NLS_LANG` — regression guard only (the thin driver ignores `NLS_LANG`) |
| `sharepoint-file-to-jsonl` | Downloads a CSV from a mock Microsoft Graph, normalizes columns, writes JSONL (file-mode smoke test) |
| `sharepoint-list-to-jsonl` | Reads a paginated SharePoint List from a mock Microsoft Graph and writes JSONL (list-mode + pagination smoke test) |
| `file-csv-to-jsonl` | Parser stage: the `file` raw source (recursive glob, non-matching files skipped) + the `csv` parser (inferred schema, empty cells as nulls) → JSONL |
| `csv-to-postgres` | Parser stage: `;`-separated windows-1252 CSVs with declared columns → Postgres `type_coverage_sink` (append COPY with a column list) |
| `csv-malformed-error` | Parser stage: a ragged CSV row fails the run (exit 1); the error names the file and line |
| `csv-schema-mismatch-error` | Parser stage: a later file whose inferred schema differs fails with `SCHEMA_MISMATCH` (exit 1) |
| `file-excel-to-jsonl` | Parser stage: the `file` raw source + the `excel` parser (named sheet, `skip_rows`) → JSONL |

## Bundles

| Bundle | Description |
|---|---|
| `parquet-destination` | Validates the parquet destination in single-file and chunked modes |
| `postgres-types` | Validates the postgres source's type decoding value-by-value (Parquet checked with pyarrow) |
| `tls-spike` | Validates the rustls + rustls-rustcrypto TLS stack against real database servers (postgres + mysql + oracle) |

## Using this repo

It's consumed by `loadsmith-lab` as an origin.

### Released catalog (default)

`catalog` is a **default remote origin**: on first run the lab registers it
(pointing at this repo's GitHub URL) and clones it the first time it's needed —
no registration step. Install what you want to run, then run it:

```bash
loadsmith-lab install catalog                    # or: install catalog/postgres-to-jsonl
loadsmith-lab run --select catalog/postgres-to-jsonl
loadsmith-lab bundle run --select catalog/parquet-destination
```

Running an item that isn't installed fails with a hint to `loadsmith-lab install` it.
To pick up new content, refresh the clone **and** re-install — `update` only pulls
the cached clone and leaves installed copies untouched:

```bash
loadsmith-lab origin remote update catalog
loadsmith-lab install catalog
```

### Local dev override

To work on this repo, register your checkout as a **local** origin — read live,
no install. This replaces the default remote `catalog` entry (the lab prints
`note: replaced existing origin 'catalog'`):

```bash
loadsmith-lab origin local add catalog ../loadsmith-lab-canonical-catalog
loadsmith-lab run --select catalog/postgres-to-jsonl
loadsmith-lab bundle run --select catalog/parquet-destination
```

To switch back to the released catalog:

```bash
loadsmith-lab origin local rm catalog
loadsmith-lab origin remote add catalog https://github.com/loadsmith-el/loadsmith-lab-canonical-catalog.git
```

A case's `services[].image` references an image from the
[`loadsmith-lab-canonical-images`](https://github.com/loadsmith-el/loadsmith-lab-canonical-images) repo as `images/<name>`.

## Writing a case or bundle

See the [loadsmith-lab docs](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src):
- [Writing Cases](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/writing-cases/case-yaml.md)
- [Writing Bundles](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/writing-bundles/bundle-yaml.md)
- [`case.yaml` schema](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/reference/case-yaml-schema.md)
- [`bundle.yaml` schema](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/reference/bundle-yaml-schema.md)

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
