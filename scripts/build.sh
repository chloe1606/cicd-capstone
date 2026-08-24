#!/usr/bin/env bash
set -euo pipefail

TARBALL="my-app-$(date +%Y%m%d).tar.gz"

echo "tarball=$TARBALL" >> "$GITHUB_OUTPUT"