# Dokku API
This is the API server of the Dokku Dashboard project, built with [FastAPI](https://fastapi.tiangolo.com/) and [Paramiko](https://www.paramiko.org/).

## Getting Started (quick run)
The entire project has been built to run entirely on [Docker](https://www.docker.com/).

Create a `.env` from `.env.sample` and execute the command below to run the application:
```
$ make run
```

## Getting Started (development)
Install the dependencies for the project:
```
$ pip install poetry
$ poetry install --with dev
```

Now, you can run the server with:
```
$ poetry run python -m src
```

## Running Tests
The project has some tests to check if everything is working properly. To run the tests, execute the command below:
```
$ poetry run python -m unittest discover -s src.tests --verbose
```

## Coding Style
Run the commands below to properly format the project's code:
```
$ poetry run flake8 src
$ poetry run black src
```
