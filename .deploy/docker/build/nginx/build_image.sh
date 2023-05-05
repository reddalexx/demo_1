#!/bin/bash

export DOLLAR='$'

set -a

source ../../.env

rm -f nginx.conf

envsubst < "nginx-template.conf" > "nginx.conf"

docker build -t demo_nginx .