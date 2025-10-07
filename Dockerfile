FROM python:3.11

WORKDIR /app

RUN mkdir -p /app/.secrets

# Install poetry first
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only=main --no-cache

# Copy the rest of the application
COPY . /app

EXPOSE $API_PORT

CMD ["bash", "-c", "set -e && if [ -f \"${SSH_KEY_PATH}\" ]; then cp \"${SSH_KEY_PATH}\" /app/.secrets/id_rsa && chmod 600 /app/.secrets/id_rsa; fi && export SSH_KEY_PATH=/app/.secrets/id_rsa && python -m src"]
