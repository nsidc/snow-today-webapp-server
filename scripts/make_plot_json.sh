#!/bin/bash
# Create JSON files from input plot CSVs.
#
# This script is a WIP. To use it, copy it into the root of the server directory.
# It should contain $input_dir.
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input_dir="$THIS_DIR/snow_today_2.0_testing/linePlotsToDate"
output_dir="$THIS_DIR/plots"

mkdir -p $output_dir

for inputfile in $input_dir/*.txt; do
    outputfile="${output_dir}/$(basename $inputfile .txt).json";
    echo $inputfile $outputfile

    # 1) `awk`: Strip trailers from source files (everything after a blank
    #    line) so they can be read as CSV.
    # 2) `sed`: Generalize headers (remove variable strings).
    # 3) `python`: Convert the CSV to JSON.
    cat $inputfile \
        | awk '/^$/{exit}1' - \
        | sed -e '1s/_(albedo|RF|scd|sca)//g' - \
        | python csv_cols_to_json.py
done
