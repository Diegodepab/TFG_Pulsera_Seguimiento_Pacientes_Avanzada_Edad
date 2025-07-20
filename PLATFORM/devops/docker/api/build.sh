#!/bin/bash

export API_VERSION="$(cat version | sed -E -e 's/\s//g')"

docker-compose -f ../all/docker-compose.yml -f ../all/docker-compose-dev.yml build api

docker tag bracelet-api:latest pixelcrush/bracelet-api:latest
docker tag bracelet-api:latest pixelcrush/bracelet-api:${API_VERSION}

docker push pixelcrush/bracelet-api:latest
docker push pixelcrush/bracelet-api:${API_VERSION}
