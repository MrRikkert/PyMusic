# PyMusic

## Installing dependencies

Make sure you have pipenv installed and run:  
`pipenv install --dev`

this creates a new virtual environment and installs all needed dependencies and dev dependencies. Check the `Pipfile` in the root folder for required dependencies and python version.

To run most of the commands mentioned you need to have activated the virtual environment. To do this run:  
`pipenv shell`

## Running app

windows:  
`cd app`  
`uvicorn main:app --reload --loop asyncio`

linux:  
`uvicorn main:app --reload --loop uvloop`

## Docker

build the image:  
`docker build -t pymusic .`

create/run the container:  
`docker run -d --name pymusic -p 7000:80 pymusic`

to run an already created image:  
`docker start pymusic`

to update the current container:

- Build a new image:
  - `docker build -t pymusic .`
- remove the current container:
  - `docker rm pymusic`
- recreate the container:
  - `docker run -d --name pymusic -p 7000:80 pymusic`

## Tests

Tests are run using pytest. To run all tests use:  
`pytest`

To run the tests with coverage, use:  
`pytest --cov`

To also generate a coverage file for your IDE, use:  
`pytest --cov-report xml:coverage.xml --cov`

Some tests are skipped by default (like lastfm tests). to run these tests use:  
`pytest --run-optional-tests=lastfm`  
see the tox.ini for all optional markers

## Dev

### Linting

Linting is done with flake8 using these paramaters:

- `--max-line-length=88`
- `--ignore=E203`
- `--max-complexity=10`

These paramaters are defined in `tox.ini` so you only need to run the bare `flake8` command

## Formatter

Formatting is done using `black` with default settings
