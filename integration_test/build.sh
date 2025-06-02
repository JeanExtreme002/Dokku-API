#!/bin/bash
set -e

# Run Dokku container
docker compose up -d dokku

# Set up SSH key
mkdir -p .ssh
KEY_PATH=".ssh/id_rsa"

if [ ! -f "$KEY_PATH" ]; then
  datetime=$(date +%Y%m%d_%H%M%S)
  ssh-keygen -t rsa -b 4096 -m PEM -C "integration_test" -f "${KEY_PATH}_$datetime" -N ""
  mv "${KEY_PATH}_$datetime" "$KEY_PATH"
  mv "${KEY_PATH}_$datetime.pub" "${KEY_PATH}.pub"
else
  echo "SSH key already exists at $KEY_PATH, skipping generation."
fi

KEY_CONTENT=$(cat "${KEY_PATH}.pub")

set +e
docker exec dokku bash -c "echo \"$KEY_CONTENT\" | dokku ssh-keys:add admin-$datetime"
docker exec dokku bash -c "echo \"$KEY_CONTENT\" >> /root/.ssh/authorized_keys"

# Run test
set -e
DOKKU_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dokku)
DOKKU_HOST="$DOKKU_HOST" docker compose up integration_test --build
