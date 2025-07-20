#!/bin/bash

## Try to infer docker host ip.
# if PYCHARM_HOST is manually set
HOST="${PYCHARM_HOST}"

# this should work on Mac and Linux
if [ -z "${HOST}" ]; then
    HOST=`getent hosts host.docker.internal | awk '{ print $1 }'`
fi

# else get host ip
if [ -z "${HOST}" ] || [ "${HOST}" = "::1" ]; then
    HOST=`/sbin/ip route | awk '/default/ { print $3 }'`
fi

# This is needed to be able to debug with Pycharm
if [ "${HOST}" ]; then
    if [ "${PYDEV_HOSTNAME}" != "" ]; then
        echo "${HOST}	${PYDEV_HOSTNAME}" >> /etc/hosts
    fi
fi

unset PYCHARM_HOST

exec uvicorn --reload --reload-dir /code --reload-dir /bracelet-lib --host 0.0.0.0 --port 8000 --log-level info "main:app"
