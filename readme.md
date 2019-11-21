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

## Tests

Tests are run using pytest. To run all tests use:  
`pytest`

To run the tests with coverage, use:  
`pytest --cov`

To also generate a coverage file for your IDE, use:  
`pytest --cov-report xml:coverage.xml --cov`

## Linting

Linting is done with flake8 using these paramaters:

- `--max-line-length=120`
- `--ignore=E203`
- `--max-complexity 10`

full command:  
`flake8 --max-line-length=120 --ignore=E203 --max-complexity 10`
