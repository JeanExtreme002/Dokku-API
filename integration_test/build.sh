#!/bin/bash
set -e

# Run Dokku container
docker compose up -d dokku

# Set up SSH key
mkdir -p .ssh
datetime=$(date +%Y%m%d_%H%M%S)

ssh-keygen -t rsa -b 4096 -m PEM -C "integration_test" -f ".ssh/id_rsa_$datetime" -N ""
mv .ssh/id_rsa_$datetime .ssh/id_rsa
mv .ssh/id_rsa_$datetime.pub .ssh/id_rsa.pub

KEY_CONTENT=$(cat .ssh/id_rsa.pub)

set +e
docker exec dokku bash -c "echo \"$KEY_CONTENT\" | dokku ssh-keys:add admin-$datetime"
docker exec dokku bash -c "echo \"$KEY_CONTENT\" >> /root/.ssh/authorized_keys"

# Run test
set -e
docker compose up integration_test --build
