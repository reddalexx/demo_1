#!/usr/bin/env bash

pushd ../

source .env

echo "=== Stopping docker service ==="

sudo service docker stop

# Run the following commands if apache2 blocks port 80
# sudo update-rc.d apache2 disable
# sudo service apache2 stop

sudo mkdir -p ${VOLUME_NGINX_CERT}

sudo certbot certonly --standalone --preferred-challenges http -d ${HOST} --config-dir ./.certs --agree-tos --email "${SUPPORT_EMAIL}" --non-interactive --deploy-hook "touch certificate_change_occured"
sudo cp ./.certs/live/${HOST}/fullchain.pem ${VOLUME_NGINX_CERT}/certificate.pem
sudo cp ./.certs/live/${HOST}/privkey.pem ${VOLUME_NGINX_CERT}/certificate.key
sudo rm -r ./.certs

echo "=== Starting docker service ==="

sudo service docker start

popd