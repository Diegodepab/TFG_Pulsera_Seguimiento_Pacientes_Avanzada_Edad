#!/bin/bash

export NGINX_VERSION="$(cat version | sed -E -e 's/\s//g')"

docker-compose -f ../all/docker-compose.yml -f ../all/docker-compose-dev.yml build nginx

docker tag bracelet-nginx:latest pixelcrush/bracelet-nginx:latest
docker tag bracelet-nginx:latest pixelcrush/bracelet-nginx:${NGINX_VERSION}

docker push pixelcrush/bracelet-nginx:latest
docker push pixelcrush/bracelet-nginx:${NGINX_VERSION}
