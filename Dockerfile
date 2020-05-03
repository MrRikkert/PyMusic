FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install pipenv

COPY Pipfile.lock .
COPY Pipfile .

RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app
