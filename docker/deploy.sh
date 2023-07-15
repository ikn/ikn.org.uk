#! /usr/bin/env bash

set -x -e

docker container ls -q | xargs -r docker container stop
docker container prune -f
docker compose --file - up --detach < "$(dirname "$0")/docker-compose.yaml"
docker image prune -af
