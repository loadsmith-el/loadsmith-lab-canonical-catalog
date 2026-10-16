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
  bundle.yaml            a sequence of cases + setup/validate/cleanup hooks
  Dockerfile             builds the image the hooks run in
  scripts/               setup/validate/cleanup scripts
```

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
| `postgres-to-postgres-types` | Round-trips the `type_coverage` scalar columns Postgres→Postgres (atomic COPY, non-UTC sessions on both sides) |
| `mysql-to-jsonl` | Reads 100k rows from MySQL and writes them to JSONL (content/type smoke test) |
| `mysql-to-jsonl-native` | Reads 100k rows from MySQL via the legacy `mysql_native_password` auth plugin — auth-mode coverage |
| `mysql-to-jsonl-tls-require` | Reads 100k rows from MySQL over TLS (`mode: require`) — rustls handshake validation |
| `mysql-to-mysql` | Loads 100k rows into MySQL (`atomic` mode) — destination smoke test |
| `mysql-to-mysql-staged-merge` | Loads 100k rows into MySQL via `staged_merge` (ON DUPLICATE KEY upsert by `id`) |
| `oracle-to-jsonl` | Reads 100k wide rows (34 cols) from Oracle and writes them to JSONL (content/type smoke test) |
| `oracle-to-jsonl-tls` | Reads 100k rows from Oracle over TCPS — `tls.mode: verify-full`, chain + hostname verified against the lab CA (`root_cert`) |
| `oracle-to-jsonl-incremental` | Incremental watermark read (cursor `event_sequence > 50000`) — reads the upper 50k |
| `oracle-to-oracle` | Loads 100k rows into Oracle (`atomic` array INSERT) — destination smoke test |
| `oracle-to-oracle-staged-merge` | Loads 100k rows into Oracle via `staged_merge` (staging GTT + one set-based `MERGE` by `id`) |
| `oracle-to-oracle-lob` | Round-trips RAW/BLOB/CLOB columns Oracle→Oracle — binary/LOB type coverage |
| `oracle-to-oracle-nls` | Loads with a comma-decimal `NLS_LANG` — regression guard only (the thin driver ignores `NLS_LANG`) |
| `sharepoint-file-to-jsonl` | Downloads a CSV from a mock Microsoft Graph, normalizes columns, writes JSONL (file-mode smoke test) |
| `sharepoint-list-to-jsonl` | Reads a paginated SharePoint List from a mock Microsoft Graph and writes JSONL (list-mode + pagination smoke test) |

## Bundles

| Bundle | Description |
|---|---|
| `parquet-destination` | Validates the parquet destination in single-file and chunked modes |
| `postgres-types` | Validates the postgres source's type decoding value-by-value (Parquet checked with pyarrow) |
| `tls-spike` | Validates the rustls + rustls-rustcrypto TLS stack against real database servers (postgres + mysql + oracle) |

## Using this repo

It's consumed by `loadsmith-lab` as an origin — register it once (local dev:
read live, no install):

```bash
loadsmith-lab origin local add catalog ../loadsmith-lab-canonical-catalog
loadsmith-lab run --select catalog/postgres-to-jsonl
loadsmith-lab bundle run --select catalog/parquet-destination
```

A case's `services[].image` references an image from the
[`loadsmith-lab-canonical-images`](https://github.com/loadsmith-el/loadsmith-lab-canonical-images) repo as `images/<name>`.

## Writing a case or bundle

See the [loadsmith-lab docs](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src):
- [Writing Cases](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/writing-cases)
- [Writing Bundles](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/writing-bundles/bundle-yaml.md)
- [`case.yaml` schema](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/reference/case-yaml-schema.md)
- [`bundle.yaml` schema](https://github.com/loadsmith-el/loadsmith-lab/blob/main/docs/src/reference/bundle-yaml-schema.md)

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
