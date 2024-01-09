#!/bin/sh

until cd /home/app
do
    echo "Waiting for server volume..."
done

# run a worker
celery -A core worker --loglevel=info --concurrency 1 -E
