#!/bin/sh

# # [local]
# python3 manage.py makemigrations --settings=config.settings.local
# python3 manage.py migrate --settings=config.settings.local
# python3 manage.py runserver 0.0.0.0:8000 --settings=config.settings.local

# product
python3 manage.py makemigrations --settings=config.settings.prod
python3 manage.py migrate --settings=config.settings.prod
gunicorn -c gunicorn_conf.py config.wsgi:application
