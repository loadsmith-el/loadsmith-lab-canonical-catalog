#!/usr/bin/env bash
# Regenerate the PEM wallet (ewallet.pem) this case mounts at /wallet.
#
# The oracledb thin driver trusts the webpki roots plus every certificate in
# `<wallet_dir>/ewallet.pem`, so the "wallet" is just the lab CA in PEM — no
# orapki, no cwallet.sso. It holds only the public lab CA (no private key), so
# it is safe to commit. Re-run this only if the lab CA changes.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ca="${1:-$here/../../../../loadsmith-lab-canonical-images/images/lab-oracle/tls/ca.crt}"
[ -f "$ca" ] || { echo "lab CA not found: $ca" >&2; exit 1; }

install -m 0644 "$ca" "$here/ewallet.pem"
echo "wrote $here/ewallet.pem"
