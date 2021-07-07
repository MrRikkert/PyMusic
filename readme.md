# PyMusic

## Installing dependencies

Make sure you have pipenv installed and run:
`pipenv install --dev`

this creates a new virtual environment and installs all needed dependencies and dev dependencies. Check the `Pipfile` in the root folder for required dependencies and python version.

To run most of the commands mentioned you need to have activated the virtual environment. To do this run:
`pipenv shell`

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

To run the LastFM tests you need to copy the `.env.template` file and remove the `.template` extension.
You then need to fill the `LASTFM_KEY` and `LASTFM_SECRET` with your own API keys. You can get a LastFM API key
[here](https://www.last.fm/api/account/create)

## Dev

### Linting

Linting is done with flake8 using these paramaters:

- `--max-line-length=88`
- `--ignore=E203`
- `--max-complexity=10`

These paramaters are defined in `tox.ini` so you only need to run the bare `flake8` command

### Formatter

Formatting is done using `black` with default settings

### SASS

For automatic SASS compilation I use the [compile hero](https://github.com/Wscats/compile-hero/blob/master/README.md) VS Code extension

## Dash

### Bootstrap

You need to include your own [bootstrap (4.6)](https://getbootstrap.com/docs/4.6/getting-started/download/) SASS files in the assets folder and the theme to use (DARKLY as default). You need to mimick the below file strcuture

```text
assets/
├── bootstrap/
│   ├── scss/                   // Bootstrap scss folder
│   │   └── ...
│   └── [theme]/                // Theme folder
│       ├── _bootswatch.scss
│       └── _variables.scss
│
└── style.scss
```

See [Dash Bootstrap themes](https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/) for more info
