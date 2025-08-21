FROM python:3.12

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.8.5 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

# Установка необходимых пакетов и добавление репозитория PostgreSQL
RUN apt-get update -o Acquire::http::No-Cache=True && apt-get upgrade -y \
    && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && apt-get update -o Acquire::http::No-Cache=True \
    && apt-get install -y postgresql-client-15

WORKDIR /code
COPY . /code

RUN pip install "poetry==$POETRY_VERSION" \
    && poetry --version

RUN poetry install

EXPOSE 8000