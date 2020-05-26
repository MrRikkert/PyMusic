FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

RUN pip install pipenv

COPY Pipfile.lock .
COPY Pipfile .

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pipenv install --system --deploy --ignore-pipfile
RUN apt-get autoremove -y gcc

ENV JWT_SECRET_KEY=
ENV JWT_ALGORITHM=
ENV PASS_ALGORITHM=
ENV LASTFM_KEY=
ENV LASTFM_SECRET=
ENV DB_PROVIDER=
ENV DB_SQLITE_FILENAME=
ENV DB_SQLITE_CREATE_DB=
ENV DB_POSTGRES_USER=
ENV DB_POSTGRES_PASSWORD=
ENV DB_POSTGRES_HOST=
ENV DB_POSTGRES_DATABASE=

COPY . /app
