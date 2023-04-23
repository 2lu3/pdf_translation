#!/bin/bash
set -xe


if [ $1 = "develop" ]; then
    SETTINGS="config.settings.development"
elif [ $1 = "production" ]; then
    SETTINGS="config.settings.production"
else
    exit 1
fi


poetry run python3 manage.py makemigrations --noinput --settings=${SETTINGS}
poetry run python3 manage.py migrate --noinput --settings=${SETTINGS}
poetry run python3 manage.py createcustomsuperuser --username ${DJANGO_USERNAME} --password ${DJANGO_PASSWORD} --noinput --database default --email ${DJANGO_EMAIL} --settings=${SETTINGS}
#poetry run python3 manage.py collectstatic --noinput

if [ $1 = "develop" ]; then
    poetry run python3 manage.py runserver 0.0.0.0:8000 --settings=${SETTINGS}
elif [ $1 = "production" ]; then
    # gunicornを起動させる時はプロジェクト名を指定します
    # 今回はdjangopjにします
    poetry run gunicorn djangopj.wsgi:application --bind 0.0.0.0:8000 --settings=${SETTINGS}
else
    exit 1
fi
