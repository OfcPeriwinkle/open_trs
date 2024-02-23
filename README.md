# Open TRS

Open TRS is a time reporting system for hobbies, projects, and life. At this time, Open TRS is a simple REST API built using Flask and SQLite.

The motivation behind this project is straightforward, provide a flexible foundation for practicing back-end development. Equally, this project's emphasis on providing a back-end API
leaves the door open for building clients of all shapes and sizes that utilize whatever front-end technologies someone is interested in learning.

If you want to build a client to utilize Open TRS, let me know and I'll be happy to work with you!

## Installation

To install the project, you need to have Python 3.10 installed (Python 3.6+ should work, but all development has been done in Python 3.10 and this project isn't using `tox` yet).

If you are new to Python, I reccomend using [`pyenv`](https://github.com/pyenv/pyenv) for installing specific versions of Python and the built-in `venv` module for creating
a virtual environment for installing Open TRS.

A fresh virtual enviornment can be created and activated with:

```sh
python -m venv .venv && source .venv/bin/activate
```

Then, you can install the project using pip:

```sh
pip install .
```

If you are planning on modifying Open TRS, use an in-place installation instead:

```sh
pip install -e .
```

## Running Tests

Open TRS uses `pytest` and `coverage` to run tests and produce coverage reports. Make sure these packages are installed in the current Python environment with:

```sh
pip install pytest coverage
```

To run the tests, you can use the following command in Open TRS' root directory:

```sh
coverage run -m pytest
```

This will run all the tests in the `tests` directory and generate a coverage report. To host a line-by-line coverage report, use:

```sh
coverage html && cd htmlcov && python -m http.server 8000
```

## Project Structure

The project is structured as follows:

- `open_trs`: This is the main package for the project. It contains the application logic and database models.
- `tests`: This directory contains all the unit tests for the project.
- `.github/workflows`: This directory contains the GitHub Actions workflow for running tests on push and pull request events.

## API Documentation

Once this project is a bit more mature, I'll build some docs for the API. Until then, please refer to the `tests/` directory to see example usage of the endpoints.

## Contributing

Contributions are welcome! Please make sure to write tests for any new features or changes in behavior.

## License

[Coffee-Ware](LICENSE)
