# Introduction

This repository is the **`catalog` origin** for
[loadsmith-lab](https://loadsmith-el.github.io/loadsmith-lab/): the test cases
and bundles that validate [Loadsmith](https://loadsmith-el.github.io/loadsmith/).

It ships **no code** — only declarative YAML (plus the small Dockerfiles that
bundles need for their hook scripts). The engine that resolves, runs, and reports
on this content lives in
[`loadsmith-lab`](https://loadsmith-el.github.io/loadsmith-lab/); this repo is
content only.

## The origin model

`loadsmith-lab` reads content from **origins**. This repo is the `catalog`
origin; its sibling
[`loadsmith-lab-canonical-images`](https://loadsmith-el.github.io/loadsmith-lab-canonical-images/)
is the `images` origin. A case here references an image there as
`images/<name>`, and the lab resolves both.

```text
loadsmith-lab-canonical-catalog  ◄── you are here   the catalog origin (cases + bundles)
loadsmith-lab-canonical-images                       the images origin (service Dockerfiles)
loadsmith-lab                                         the engine (resolve, run, report)
loadsmith                                             the tool under test
```

## Where to go next

- [Layout & Manifest](./layout.md) — the directory shape and the
  `loadsmith-lab.toml` manifest.
- [Cases](./cases.md) — what each case validates.
- [Bundles](./bundles.md) — the sequenced, hook-wrapped scenarios.
- [Using the Catalog](./using.md) — the default origin, local overrides and running.
- [Writing a Case or Bundle](./writing.md) — the rules and where the schemas
  live.
