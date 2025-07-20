#!/bin/bash

export PLATFORM_VERSION="$(cat version | sed -E -e 's/\s//g')"

docker-compose -f ../all/docker-compose.yml -f ../all/docker-compose-dev.yml build platform

docker tag bracelet-platform:latest pixelcrush/bracelet-platform:latest
docker tag bracelet-platform:latest pixelcrush/bracelet-platform:${PLATFORM_VERSION}

docker push pixelcrush/bracelet-platform:latest
docker push pixelcrush/bracelet-platform:${PLATFORM_VERSION}
