# Dokku API
This is the API server of the Dokku Dashboard project, built with [FastAPI](https://fastapi.tiangolo.com/) and [Paramiko](https://www.paramiko.org/).

## Getting Started (quick run)
The entire project has been built to run entirely on [Dokku](https://dokku.com/) or [Docker](https://www.docker.com/).

Create a `.env` from `.env.sample`, set the variables, and execute the command below to run the application:
```
$ make dokku-install
```
Now, open the API on your browser at [http://dokku-api.yourdomain](http://dokku-api.yourdomain) — if you did not change the default settings.

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
```

## Coding Style
Run the commands below to properly format the project's code:
```
$ make lint
$ make lint-fix
```
