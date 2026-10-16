# Cases

A **case** is a single Loadsmith pipeline run against one or more services, with
a readiness probe and an `expect` block asserting the outcome.

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

## Two distinct purposes

- **Smoke / content cases** (e.g. `postgres-to-jsonl`) validate real
  content and type round-trips on the 100k-row canonical dataset, with an
  `output:` block asserting what was written.
- **Volume / throughput cases** (e.g. `postgres-to-null-15M`) inflate row counts
  to measure pure read/pump throughput. They write to the `null` destination and
  assert only `rows_read` / `rows_written` — never an `output:` block (a
  multi-million-row file would be gigabytes). See
  [Writing a Case or Bundle](./writing.md) for why this rule is strict.
