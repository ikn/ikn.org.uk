#! /usr/bin/env bash

set -x -e

docker container ls -q | xargs -r docker container stop
docker container prune -f
docker compose --file "$(dirname "$0")/docker-compose.yaml" \
    --env-file "$ENV_FILE" \
    up --detach --pull="$PULL_POLICY"
docker image prune -af
