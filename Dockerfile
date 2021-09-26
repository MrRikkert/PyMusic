FROM python:3.9.7-slim

RUN mkdir /app
WORKDIR /app

RUN pip install pipenv

COPY Pipfile.lock .
COPY Pipfile .

RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 8080
ENV DB_PROVIDER="postgres"
ENV DB_POSTGRES_USER="postgres"
ENV DB_POSTGRES_PASSWORD="postgres"
ENV DB_POSTGRES_PASSWORD="0.0.0.0"
ENV DB_POSTGRES_DATABASE="pymusic"
ENV DB_POSTGRES_PORT=1234
ENV ALBUM_ART_PATH=C:\art
ENV IMG_URL="https://myhost:5555/img/"
ENV MUSIC_PATH="C:\\music\\"
ENV LASTFM_KEY=""
ENV LASTFM_SECRET=""

CMD ["pipenv", "run", "gunicorn", "--workers=1", "--threads=1", "-b 0.0.0.0:8080", "server:server"]
