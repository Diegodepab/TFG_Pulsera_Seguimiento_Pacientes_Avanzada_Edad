#!/bin/bash

if [ -f .env ]
then
    # Load variables from .env file
    export $(cat .env | sed 's/#.*//g' | xargs)

    docker run --rm \
    --name letsencrypt \
    -v "$(pwd)/certs:/etc/letsencrypt" \
    -v "$(pwd)/certs/webroot:/webroot" \
    certbot/certbot renew \
    --webroot --webroot-path /webroot --agree-tos

    docker exec bracelet-pro_nginx_1 nginx -s reload
fi
