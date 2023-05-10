#!/bin/bash

set -a

source ../../.env

envsubst < "start-template.sh" > "start.sh"

pushd ../../../../ || return
docker build -t demo_main_app -f ./.deploy/docker/build/main/Dockerfile .
popd || return

rm -f start.sh
