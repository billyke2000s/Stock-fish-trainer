#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
assets=app/src/main/assets
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
fetch() {
    local name=$1 version=$2 digest=$3
    curl --retry 3 -fsSL "https://registry.npmjs.org/$name/-/$name-$version.tgz" -o "$temp/package.tgz"
    echo "$digest  $temp/package.tgz" | sha256sum -c -
    tar xOf "$temp/package.tgz" "package/$name" > "$assets/$name"
}
fetch chess.js 0.10.3 c7b7e163abc8cbafd735550c9f9af260a67dbeebf28f51684749cfb9772b20b9
fetch stockfish.js 10.0.2 ed612bf4755ab64c3f95311673156d70d18d089929b1de25136e017383497f94
