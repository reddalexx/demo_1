#!/bin/bash

sudo mkdir -p /deploy
cd /deploy

source ./install_docker.sh

git clone https://github.com/reddalexx/demo_1.git

pushd demo_1/./deploy/docker/build/main || exit
source ./build_image.sh
popd || exit

pushd demo_1/./deploy/docker/build/fastapi || exit
source ./build_image.sh
popd || exit

pushd demo_1/./deploy/docker/build/nginx || exit
source ./build_image.sh
popd || exit
