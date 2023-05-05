#!/bin/bash

pushd ../../../../ || return
docker build -t demo_main_app -f ./.deploy/docker/build/main/Dockerfile .
popd || return