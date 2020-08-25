#!/bin/sh

python manage.py makemigrations

# Setup null primary keys 
python manage.py migrate players 0001
python manage.py migrate --fake players 0002
python manage.py migrate