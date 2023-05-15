#!/bin/bash

set -a

source .env

# setup WEBDAV root
sudo mkdir -p "${VOLUME_WEBDAV}"

# setup NGINX files
sudo mkdir -p "${VOLUME_NGINX_CONF}"
sudo mkdir -p "${VOLUME_NGINX_INCL}"
sudo mkdir -p "${VOLUME_NGINX_CERT}"

pushd ./build/nginx || exit
envsubst < "routes-template.conf" > "${VOLUME_NGINX_INCL}/routes.conf"
[ "${USE_HTTPS}" = true ] && PROTOCOL_SUFFIX='s'
envsubst < "http${PROTOCOL_SUFFIX}-template.conf" > "${VOLUME_NGINX_CONF}/nginx.conf"
popd || exit

# setup docker compose file
envsubst < "docker-compose-template.yml" > "docker-compose.yml"

sudo docker stack deploy --compose-file docker-compose.yml demo

rm -f docker-compose.yml