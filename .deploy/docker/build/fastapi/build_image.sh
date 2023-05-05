#!/bin/bash

pushd ../../../../ || return
docker build -t demo_fastapi -f ./.deploy/docker/build/fastapi/Dockerfile .
popd || return