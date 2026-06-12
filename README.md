# loadsmith-lab-canonical-catalog

The **`catalog` origin** for [loadsmith-lab](../loadsmith-lab): test cases and
bundles for [Loadsmith](../loadsmith). This repo ships no code — just
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

## Bundles

| Bundle | Description |
|---|---|
| `parquet-destination` | Validates the parquet destination in single-file and chunked modes |
| `tls-spike` | Validates the rustls + rustls-rustcrypto TLS stack against real database servers |

## Using this repo

It's consumed by `loadsmith-lab` as an origin — register it once (local dev:
read live, no install):

```bash
loadsmith-lab origin local add catalog ../loadsmith-lab-canonical-catalog
loadsmith-lab run --local --select catalog/postgres-to-jsonl
loadsmith-lab bundle run --local --select catalog/parquet-destination
```

A case's `services[].image` references an image from the
[`loadsmith-lab-canonical-images`](../loadsmith-lab-canonical-images) repo as `images/<name>`.

## Writing a case or bundle

See the [loadsmith-lab docs](../loadsmith-lab/docs/src):
- [Writing Cases](../loadsmith-lab/docs/src/writing-cases)
- [Writing Bundles](../loadsmith-lab/docs/src/writing-bundles/bundle-yaml.md)
- [`case.yaml` schema](../loadsmith-lab/crates/loadsmith-lab-runner/src/case.rs)
- [`bundle.yaml` schema](../loadsmith-lab/docs/src/reference/bundle-yaml-schema.md)

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
