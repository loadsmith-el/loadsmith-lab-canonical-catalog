# Using the Catalog

This repo is consumed by `loadsmith-lab` as an origin.

## Released catalog (default)

`catalog` is a **default remote origin**: on first run the lab registers it
(pointing at
`https://github.com/loadsmith-el/loadsmith-lab-canonical-catalog.git`) and clones
it the first time it's needed — there is nothing to register. Install what you
want to run, then run it:

```bash
# Install the whole catalog (or a single item: install catalog/postgres-to-jsonl)
loadsmith-lab install catalog

# Run a single case
loadsmith-lab run --select catalog/postgres-to-jsonl

# Run a bundle
loadsmith-lab bundle run --select catalog/parquet-destination
```

Running an item that isn't installed fails with a hint to run
`loadsmith-lab install <origin>/<name>`. To pick up new content, refresh the
clone **and** re-install — `origin remote update` only pulls the cached clone and
leaves already-installed copies untouched:

```bash
loadsmith-lab origin remote update catalog
loadsmith-lab install catalog
```

## Local dev override

For local development, register your checkout as a **local** origin — the lab
reads it live, with no install step. This replaces the default remote `catalog`
entry (the lab prints `note: replaced existing origin 'catalog'`):

```bash
# Register once (local dev: read live from the working tree)
loadsmith-lab origin local add catalog ../loadsmith-lab-canonical-catalog

# Run a single case
loadsmith-lab run --select catalog/postgres-to-jsonl

# Run a bundle
loadsmith-lab bundle run --select catalog/parquet-destination
```

To switch back to the released catalog:

```bash
loadsmith-lab origin local rm catalog
loadsmith-lab origin remote add catalog https://github.com/loadsmith-el/loadsmith-lab-canonical-catalog.git
```

## Images and run modes

A case's `services[].image` references an image from the
[`loadsmith-lab-canonical-images`](https://loadsmith-el.github.io/loadsmith-lab-canonical-images/)
repo as `images/<name>`; it is auto-built on first run.

For the run modes (building the core or a plugin from source via
`--loadsmith` / `--plugin`, picking a published image with `--tag`, and so on),
see the lab docs:

- [Running a Case](https://loadsmith-el.github.io/loadsmith-lab/getting-started/running-a-case.html)
- [Run Modes](https://loadsmith-el.github.io/loadsmith-lab/architecture/run-modes.html)
- [CLI Reference](https://loadsmith-el.github.io/loadsmith-lab/reference/cli.html)
