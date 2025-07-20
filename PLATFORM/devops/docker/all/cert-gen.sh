#!/bin/bash

if [ -f .env ]
then
    # Load variables from .env file
    export $(cat .env | sed 's/#.*//g' | xargs)

    docker run --rm \
    -p 80:80 -p 443:443 \
    --name letsencrypt \
    -v "$(pwd)/certs:/etc/letsencrypt" \
    certbot/certbot certonly -n \
    -m "Diegodepablo" \
    -d "${HTTPS_PLATFORM_DOMAIN}" \
    --standalone --agree-tos
fi
