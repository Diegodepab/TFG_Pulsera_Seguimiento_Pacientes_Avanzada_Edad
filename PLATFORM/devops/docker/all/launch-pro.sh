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
Launch bracelet production environment

    -h      display this help and exit
    -a      launch in foreground, attached mode
    
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

export ATTACH_MODE="0"
export COMPOSE_PROJECT_NAME="bracelet-pro"

while getopts "h?a" opt; do
    case "$opt" in
        h|\?)
            show_help
            exit 0
            ;;
        a)  ATTACH_MODE="1"
            ;;
    esac
done

# Simply start env
$compose_cmd \
 -f docker-compose.yml \
 up \
 $([[ "$ATTACH_MODE" == "1" ]] && echo "" || echo "-d")
