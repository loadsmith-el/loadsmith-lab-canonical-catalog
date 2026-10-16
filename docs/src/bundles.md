# Bundles

A **bundle** is a sequence of existing cases wrapped with
setup / validate / cleanup hooks. The hooks run inside an image the bundle builds
from its own `Dockerfile`, so no host Python or other dependencies are required.

| Bundle | Description |
|---|---|
| `parquet-destination` | Validates the parquet destination in single-file and chunked modes |
| `postgres-types` | Validates the postgres source's type decoding value-by-value (Parquet checked with pyarrow) |
| `tls-spike` | Validates the rustls + rustls-rustcrypto TLS stack against real database servers (postgres + mysql + oracle) |

## Bundles never modify their cases

A bundle only **chains and wraps** existing cases — it never edits them. Each
case it sequences stays independently runnable via `run --select`. This keeps a
case a self-contained unit and the bundle a higher-level orchestration on top.

```text
bundles/<name>/
  bundle.yaml      the ordered list of cases + the hook references
  Dockerfile       builds the image the hook scripts run in
  scripts/         setup / validate / cleanup scripts
```

See [Writing a Case or Bundle](./writing.md) and the lab's
[Writing Bundles](https://loadsmith-el.github.io/loadsmith-lab/writing-bundles/bundle-yaml.html)
guide.
