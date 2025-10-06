FROM python:3.11

WORKDIR /app

RUN mkdir -p /app/.secrets

COPY . /app

RUN pip install poetry > /dev/null && \
    poetry install --no-root > /dev/null

EXPOSE $PORT

CMD ["bash", "-c", "set -e && if [ -f \"${SSH_KEY_PATH}\" ]; then cp \"${SSH_KEY_PATH}\" /app/.secrets/id_rsa && chmod 600 /app/.secrets/id_rsa; fi && export SSH_KEY_PATH=/app/.secrets/id_rsa && poetry run python -m src"]
