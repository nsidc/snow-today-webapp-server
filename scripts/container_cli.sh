#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(realpath "$THIS_DIR/..")"

cd $REPO_DIR
# TODO: Conditionally source VERSION.latest.env if not in prod? Look at $ENVIRONMENT?
source VERSION.env
DOCKER_IMAGE="nsidc/snow-today-webapp-server-ingest:${SERVER_VERSION}"
if [[ "$(docker images -q "${DOCKER_IMAGE}" 2>/dev/null)" == "" ]]; then
    echo "Docker image ${DOCKER_IMAGE} not found. Did you deploy it?"
fi
echo "$@"
# docker-compose run ingest "$@"
