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
sudo mkdir -p "${VOLUME_NGINX_LOGS}"
sudo mkdir -p "${VOLUME_CLICKHOUSE}"
sudo mkdir -p "${VOLUME_NGINX_CLICKHOUSE}"
sudo mkdir -p "${VOLUME_GRAFANA}"

pushd ./build/nginx || exit
cp nginx.template.conf "${VOLUME_NGINX}/nginx.conf"
envsubst < "server.template.conf" > "${VOLUME_NGINX_CONF}/server.conf"
envsubst < "routes.template.conf" > "${VOLUME_NGINX_INCL}/routes.conf"
envsubst < "proxy-headers.template.conf" > "${VOLUME_NGINX_HEAD}/proxy.conf"
envsubst < "ws-headers.template.conf" > "${VOLUME_NGINX_HEAD}/ws.conf"
if [ "${USE_HTTPS}" = true ]; then
  envsubst < "server_ssl.template.conf" > "${VOLUME_NGINX_INCL}/ssl.conf"
fi
popd || exit

# setup docker compose file
envsubst < "docker-compose-template.yml" > "docker-compose.yml"

# setup clickhouse
pushd ./build/clickhouse || exit
envsubst < "init-defaults.template.sh" > "${VOLUME_CLICKHOUSE}/init-defaults.sh"
popd || exit

# setup nginx-clickhouse
pushd ./build/clickhouse-nginx || exit
envsubst < "config.template.yml" > "${VOLUME_NGINX_CLICKHOUSE}/config.yml"
popd || exit

# setup grafana
pushd ./build/grafana || exit
envsubst < "clickhouse-datasource.template.yaml" > "${VOLUME_GRAFANA}/clickhouse-datasource.yaml"
envsubst < "nginx_dashboard.template.json" > "${VOLUME_GRAFANA}/nginx_dashboard.json"
cp default-dashboard.template.yaml "${VOLUME_GRAFANA}/default-dashboard.yaml"
popd || exit

sudo docker stack deploy --compose-file docker-compose.yml demo

rm -f docker-compose.yml