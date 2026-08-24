#!/usr/bin/env bash
set -euo pipefail

mkdir -p dist

echo "Build output" > dist/build.txt

echo "tarball=build.txt" >> "$GITHUB_OUTPUT"