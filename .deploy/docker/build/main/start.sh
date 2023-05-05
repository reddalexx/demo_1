#!/bin/bash

set -e

ROLE=$1
echo "ROLE: ${ROLE}"

if [[ "${ROLE}" == "daphne" ]]; then

  echo ">>> Start django migrations..."
  python manage.py migrate --noinput

  echo ">>> Install initial data from fixtures..."
  python manage.py loaddata demo/data/fixtures/*.json

  echo ">>> Collect django static files..."
  python manage.py collectstatic --noinput

  echo ">>> Run daphne server..."
  exec daphne -b 0.0.0.0 -p 3355 -t 60 --application-close-timeout 60 demo.asgi:application

elif [[ "${ROLE}" == "jupyter" ]]; then

  echo ">>> Install jupyter requirements..."
  pip install jupyter

  echo ">>> Install fastapi requirements..."
#  pip install -r apps/hotels/

  jupyter notebook --port=8888 --no-browser --ip=0.0.0.0

fi
