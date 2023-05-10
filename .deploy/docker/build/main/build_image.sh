#!/bin/bash

set -a

source ../../.env

rm -f start.sh

envsubst < "start-template.sh" > "start.sh"

pushd ../../../../ || return
#docker volume rm demo_django_app || true
docker build -t demo_main_app -f ./.deploy/docker/build/main/Dockerfile .
popd || return