#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(realpath "$THIS_DIR/..")"

cd $REPO_DIR
source VERSION.env
DOCKER_IMAGE="nsidc/snow-today-webapp-server-ingest:${SERVER_VERSION}"
if [[ "$(docker images -q "${DOCKER_IMAGE}" 2>/dev/null)" == "" ]]; then
    echo "Docker image ${DOCKER_IMAGE} not found. Did you deploy it?"
fi
# TODO: Specify --no-pull / --no-build so we only run the image
echo "$@"
# docker-compose run ingest "$@"
