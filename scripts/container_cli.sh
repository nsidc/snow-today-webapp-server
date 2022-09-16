#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(realpath "$THIS_DIR/..")"

cd $REPO_DIR
docker-compose run ingest "$@"
