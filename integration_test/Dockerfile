FROM debian:bookworm

RUN apt-get update && \
    apt-get install -y netcat-openbsd make git openssh-client curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .