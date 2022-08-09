#!/bin/bash
# Create symbolic links pointing to COGs matching given YYYYMMDD.
#
# This script is a WIP. To use it, copy it into the root of the server
# directory.
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COGS_DIR="$THIS_DIR/cogs"

if [ -z "${1-}" ]; then
    echo "Expected YYYYMMDD date as first positional argument."
    exit 1
fi
input_date="$1"

set +e
date "+%Y%m%d" -d "$input_date" > /dev/null 2>&1
date_is_valid=$?
set -e
if [[ "$date_is_valid" != "0" ]]; then
    echo "Expected YYYYMMDD date; got '${input_date}'."
    exit 1
fi

matches=$(ls $COGS_DIR/*${input_date}*.tif)
n_matches=$(echo "$matches" | wc -w)
if [[ "$n_matches" != "9" ]]; then
    echo "Expected 9 matching GeoTIFFs. Got ${n_matches}:"
    for match in $matches; do
        echo "  - $match"
    done
    exit 1
fi

cd $COGS_DIR;
for match in $matches; do
    file_name=$(basename $match)
    symlink_name=$(echo "${file_name}" | awk -F"${input_date}_" '{print $2}')

    ln -sf "${file_name}" "${symlink_name}"
    echo "Created symlink: $symlink_name -> $file_name"
done
