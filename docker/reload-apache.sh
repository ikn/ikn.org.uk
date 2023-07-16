#! /usr/bin/env bash

set -x -e

container_id="$(docker container ls --filter 'ancestor=ikn5812/ikn' --quiet)"
docker exec "$container_id" httpd -k graceful
