#!/usr/bin/env bash
# Regenerate the lab CA copy (ca.crt) this case mounts at /tls.
#
# The pipeline passes it inline as `tls.root_cert`. It holds only the public
# lab CA (no private key), so it is safe to commit. Re-run this only if the lab CA changes.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ca="${1:-$here/../../../../loadsmith-lab-canonical-images/images/lab-oracle/tls/ca.crt}"
[ -f "$ca" ] || { echo "lab CA not found: $ca" >&2; exit 1; }

install -m 0644 "$ca" "$here/ca.crt"
echo "wrote $here/ca.crt"
