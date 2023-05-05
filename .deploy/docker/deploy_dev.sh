#!/bin/bash

set -a

sudo mkdir -p /demo/dav

source .env

#sudo docker stack deploy --compose-file docker-compose-dev.yml demo
#sudo docker stack deploy -c <(docker-compose -f docker-compose-dev.yml config) demo

rm -f docker-compose.yml
envsubst < "docker-compose-template.yml" > "docker-compose.yml"

sudo docker stack deploy --compose-file docker-compose.yml demo