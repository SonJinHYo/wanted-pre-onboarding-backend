FROM python:3.9-alpine

# RUN ["apk", "update", "&&", "apk", "add", "--no-cache", "gcc", "libc-dev", "&&", "pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["apk", "update"]
RUN ["apk", "add", "--no-cache", "gcc","musl-dev", "libffi-dev","openssl-dev","mariadb-dev"]


WORKDIR /app

COPY requirements.txt .

RUN ["pip","install","-r","requirements.txt"]

COPY . .

ARG DEFAULT_PORT=8000

EXPOSE ${DEFAULT_PORT}

CMD ["python3","manage.py","runserver","0.0.0.0:8000","--settings=config.settings.local"]

