#!/bin/bash

export DOLLAR='$'

set -a

source ../../.env

rm -f nginx.conf

if [ "${USE_HTTPS}" = true ] ; then
    envsubst < "nginx-https-template.conf" > "nginx.conf"
else
    envsubst < "nginx-http-template.conf" > "nginx.conf"
fi

rm -f routes.conf

envsubst < "nginx-routes-template.conf" > "routes.conf"

docker build -t demo_nginx .