#!/bin/sh

set -e

echo "migrate"
python manage.py migrate

exec "$@"