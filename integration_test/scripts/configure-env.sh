#!/bin/bash
set -e

DIR="$1"
cd "$DIR"

ENV_SAMPLE_PATH="$DIR/.env.sample"
ENV_PATH="/$DIR/.env"
cp "$ENV_SAMPLE_PATH" "$ENV_PATH"

# Setup SSH
MASTER_KEY="abc12345678"
API_KEY="abc123"
SSH_HOSTNAME="dokku"
RSA_KEY_FILE="$DIR/integration_test/.ssh/id_rsa.pub"

sed -i "s|^MASTER_KEY=.*|MASTER_KEY=\"$MASTER_KEY\"|" "$ENV_PATH"
sed -i "s|^API_KEY=.*|API_KEY=\"$API_KEY\"|" "$ENV_PATH"
sed -i "s|^SSH_HOSTNAME=.*|SSH_HOSTNAME=$SSH_HOSTNAME|" "$ENV_PATH"
sed -i "s|^RSA_KEY_FILE=.*|RSA_KEY_FILE=$RSA_KEY_FILE|" "$ENV_PATH"
