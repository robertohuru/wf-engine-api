#!/bin/sh

until cd /home/app
do
    echo "Waiting for server volume..."
done


until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done


gunicorn core.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4 --timeout 600