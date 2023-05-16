#!/bin/bash

set -a

source .env

# setup WEBDAV root
sudo mkdir -p "${VOLUME_WEBDAV}"

# setup NGINX files
sudo mkdir -p "${VOLUME_NGINX_CONF}"
sudo mkdir -p "${VOLUME_NGINX_INCL}"
sudo mkdir -p "${VOLUME_NGINX_HEAD}"
sudo mkdir -p "${VOLUME_NGINX_CERT}"

pushd ./build/nginx || exit
envsubst < "nginx.template.conf" > "${VOLUME_NGINX_CONF}/nginx.conf"
envsubst < "routes.template.conf" > "${VOLUME_NGINX_INCL}/routes.conf"
envsubst < "proxy-headers.template.conf" > "${VOLUME_NGINX_HEAD}/proxy.conf"
envsubst < "ws-headers.template.conf" > "${VOLUME_NGINX_HEAD}/ws.conf"
if [ "${USE_HTTPS}" = true ]; then
  envsubst < "nginx_ssl.template.conf" > "${VOLUME_NGINX_INCL}/ssl.conf"
fi
popd || exit

# setup docker compose file
envsubst < "docker-compose-template.yml" > "docker-compose.yml"

sudo docker stack deploy --compose-file docker-compose.yml demo

rm -f docker-compose.yml