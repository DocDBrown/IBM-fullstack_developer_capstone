#!/bin/sh

set -e

echo "Making migrations and migrating the database."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files."
python manage.py collectstatic --noinput

exec "$@"
