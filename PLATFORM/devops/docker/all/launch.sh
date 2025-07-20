#!/bin/bash
# Script to launch bracelet API environment
# if any variable is unset exits with error
set -u

# exists at first non 0 exit code
set -e

# Usage info
show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-v]...
Launch bracelet development environment

    -h      display this help and exit
    -r      rebuild containers, if set containers will be rebuilt before launch
    -c      clean environment, if set a new empty datastore will be created for PostgreSQL
    -d      launch in background, detached mode

EOF
}

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

command -v docker >/dev/null 2>&1 || { echo >&2 "You need the docker binary in the path"; exit 1; }
compose_cmd="docker compose"
if command -v docker-compose > /dev/null; then
    compose_cmd="docker-compose"
fi

# Create env file for Docker Compose.
if [ ! -e .env  ]; then
  cp env.template .env
fi

export CLEAN_ENV="0"
export DETACH_MODE="0"
export REBUILD_CONTAINERS="0"
export COMPOSE_PROJECT_NAME="bracelet"
export NGINX_VERSION="$(cat ../nginx/version | sed -E -e 's/\s//g')"
export API_VERSION="$(cat ../api/version | sed -E -e 's/\s//g')"
export PLATFORM_VERSION="$(cat ../platform/version | sed -E -e 's/\s//g')"

while getopts "h?cdr" opt; do
    case "$opt" in
        h|\?)
            show_help
            exit 0
            ;;
        c)  CLEAN_ENV="1"
            ;;
        d)  DETACH_MODE="1"
            ;;
        r)  REBUILD_CONTAINERS="1"
            ;;
    esac
done

if [ "${CLEAN_ENV}" = "1" ]; then
  # Remove existing network and data volumes related to this compose
  $compose_cmd -f docker-compose.yml -f docker-compose-dev.yml down -v --remove-orphans
fi

$compose_cmd \
 -f docker-compose.yml \
 -f docker-compose-dev.yml \
 up \
 $([[ "$REBUILD_CONTAINERS" == "1" ]] && echo "--force-recreate --build") \
 $([[ "$DETACH_MODE" == "1" ]] && echo "-d")
