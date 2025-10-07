# Dokku API
This is a RESTful API for managing applications and resources on Dokku, built with [FastAPI](https://fastapi.tiangolo.com/).

[![CI](https://github.com/JeanExtreme002/Dokku-API/actions/workflows/ci.yml/badge.svg)](https://github.com/JeanExtreme002/Dokku-API/actions/workflows/ci.yml)
[![Pypi](https://img.shields.io/pypi/v/dokku-api)](https://pypi.org/project/dokku-api/)
[![License](https://img.shields.io/pypi/l/Dokku-API)](https://pypi.org/project/Dokku-API/)
[![Platforms](https://img.shields.io/badge/platforms-Dokku%20%7C%20Linux-8A2BE2)](https://pypi.org/project/dokku-api/)
[![Python Version](https://img.shields.io/badge/python->=3.11-blue)](https://pypi.org/project/dokku-api/)

### Installing Dokku API from PyPI:
```
$ pip install dokku-api
$ dokku-api help
```

## Getting Started (quick run)
The entire project has been built to run entirely on [Dokku](https://dokku.com/) or [Docker](https://www.docker.com/).

Create a `.env` from `.env.sample`, configure the variables, and execute one of the commands below to run the application:
```
# For installing and running the API as a Dokku application.
$ make dokku-install

# For installing and running the API on Docker.
$ make docker-run
```
Now, open the API on your browser at [http://dokku-api.yourdomain](http://dokku-api.yourdomain) — if you did not change the default settings.

Access [/docs](http://dokku-api.yourdomain/docs) for more information about the API.

## Getting Started (development)
Install the dependencies for the project:
```
$ pip install poetry
$ make install
```

Now, you can run the server with:
```
$ make run
```

Run `make help` to learn about more commands. 

## Running Tests
The project has some tests to check if everything is working properly. To run the tests, execute the command below:
```
$ make test
$ make system-test
```

## Coding Style
Run the commands below to properly format the project's code:
```
$ make lint
$ make lint-fix
```
