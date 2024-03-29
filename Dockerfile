FROM python:3.9.7-slim
RUN apt-get -y update && apt-get -y install git

RUN mkdir /app
WORKDIR /app
RUN mkdir "/.logs"

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

EXPOSE 8080
ENV DB_PROVIDER="postgres"
ENV DB_POSTGRES_USER="postgres"
ENV DB_POSTGRES_PASSWORD="postgres"
ENV DB_POSTGRES_HOST="0.0.0.0"
ENV DB_POSTGRES_DATABASE="pymusic"
ENV DB_POSTGRES_PORT=1234
ENV ALBUM_ART_PATH="C:\\art"
ENV IMG_URL="https://myhost:5555/img/"
ENV MUSIC_PATH="C:\\music\\"
ENV LIBRARY_BASE_PATH="/app/music"
ENV LASTFM_KEY=""
ENV LASTFM_SECRET=""

ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1

CMD sh start.sh
