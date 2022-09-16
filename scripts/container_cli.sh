#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(realpath "$THIS_DIR/..")"

cd $REPO_DIR
# TODO: Source VERSION file
# TODO: Specify --no-pull / --no-build so we only run the image
docker-compose run ingest "$@"
