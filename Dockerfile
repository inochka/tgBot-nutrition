FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/usr/src/app
WORKDIR $APP_HOME
ENV PYTHONPATH="${APP_HOME}:${APP_HOME}/app"

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
