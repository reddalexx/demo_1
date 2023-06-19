#!/bin/bash

set -e

ROLE=$1
echo "ROLE: ${DOLLAR}{ROLE}"

if [[ "${DOLLAR}{ROLE}" == "daphne" ]]; then

  echo ">>> Start django migrations..."
  python manage.py migrate --noinput

  echo ">>> Set default site..."
  python manage.py set_default_site --name ar_demo --domain ${HOST}

  echo ">>> Install initial data from fixtures..."
  python manage.py loaddata demo/data/fixtures/*.json

  echo ">>> Create default superuser"
  python manage.py create_superuser --username ${ADMIN_USERNAME} --email ${ADMIN_EMAIL} --password ${ADMIN_PASSWORD}

  echo ">>> Collect django static files..."
  python manage.py collectstatic --noinput

  echo ">>> Run daphne server..."
  exec daphne -b 0.0.0.0 -p ${DAPHNE_PORT} -t 60 --application-close-timeout 60 demo.asgi:application

else
  echo "Unknown service/role/argument ${DOLLAR}{ROLE}"

fi
