# Layout & Manifest

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

## The manifest is authoritative

`loadsmith-lab.toml` maps each case and bundle to a description, under `[cases]`
and `[bundles]`. The lab reads the **manifest**, not the filesystem — so
`loadsmith-lab list`, `bundle list`, and `origin show catalog` all reflect what's
declared there.

When you add content, add **both**:

1. the content directory (`cases/<name>/` or `bundles/<name>/`), and
2. an entry under `[cases]` / `[bundles]` in `loadsmith-lab.toml`.

Keep the [Cases](./cases.md) and [Bundles](./bundles.md) tables (and the repo
`README.md`) in sync when you add or rename content.

## How a case references an image

A case's `services[].image` is an `<origin>/<name>` reference — for example
`images/lab-postgres-15` — resolved against
[`loadsmith-lab-canonical-images`](https://loadsmith-el.github.io/loadsmith-lab-canonical-images/).
If a case needs a new image, it's added **there**, not here.
