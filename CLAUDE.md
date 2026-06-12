# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository. It is **operating instructions only** — for what this
repo is and how a case/bundle is structured, read [README.md](README.md) and
the [loadsmith-lab docs](../loadsmith-lab/docs/src), or the source itself.
Don't guess at "why" — go read it.

## Conventions

- **English only.** All artifacts committed to this repo — YAML, scripts,
  commit messages, identifiers — must be in English, even when the user writes
  in Portuguese.
- **This repo is content only.** It's the `catalog` origin for
  [loadsmith-lab](../loadsmith-lab) — no engine code lives here. The engine
  (resolution, runner, CLI) lives in `../loadsmith-lab`; if a change requires
  touching the runner or `case.rs`/`bundle.rs` schema, that's a
  `loadsmith-lab` change, not a catalog change.
- **Update the manifest.** Adding a case or bundle means adding both the
  content directory *and* an entry under `[cases]`/`[bundles]` in
  [`loadsmith-lab.toml`](loadsmith-lab.toml) — `loadsmith-lab list` and
  `origin show catalog` read from the manifest, not the filesystem.
- **Keep README.md in sync** with the case/bundle tables when you add or
  rename content.

## Hard rules — read before adding a case

- **Volume/scale cases (anything that inflates row counts via `CROSS JOIN` /
  `generate_series`) MUST use `destination.type: "null"`** (quoted — `null` is
  a YAML keyword), and assert only `rows_read`/`rows_written` in `expect` — no
  `output:` block. A multi-million-row JSONL is gigabytes, and the output dir
  defaults to the system temp dir (often a tmpfs that can't hold it). Name
  them `<service>-to-null-<N>` (e.g. `postgres-to-null-15M`). The 100k smoke
  case (`postgres-to-jsonl`) is the one that validates real content/type
  round-trips — don't conflate the two purposes.
- **Postgres-protocol services need a query-level readiness probe**, not just
  `tcp:` — the service accepts connections while still loading the 100k-row
  seed, so a TCP-only check races. Mirror the `postgres:` probe block in
  `cases/postgres-to-jsonl/case.yaml`.
- **A case's `services[].image` is an `<origin>/<name>` reference** (e.g.
  `images/lab-postgres-15`), resolved against
  [`loadsmith-lab-canonical-images`](../loadsmith-lab-canonical-images). If a case needs a new
  image, add it there — not here.
- **Bundles never modify the cases they sequence** — a bundle only chains and
  wraps existing cases (which stay runnable standalone via `run --select`) with
  setup/validate/cleanup hooks. Hook scripts run inside the bundle's own
  `Dockerfile`-built image — no host Python/deps required.

## Verifying a change

This repo has no build step. Verify a case or bundle by running it through the
`loadsmith-lab` engine (sibling repo, registered as a local origin):

```bash
cd ../loadsmith-lab
./target/debug/loadsmith-lab origin local add catalog ../loadsmith-lab-canonical-catalog   # once
./target/debug/loadsmith-lab run --local --select catalog/<name>
./target/debug/loadsmith-lab bundle run --local --select catalog/<bundle-name>
```
