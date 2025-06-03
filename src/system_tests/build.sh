#!/bin/bash
set -e

CONTAINER_NAME="$1"
MASTER_KEY="$2"
API_KEY="$3"

DOKKU_API_HOST="0.0.0.0"
DOKKU_API_PORT=5000

echo "Setting up SSH key..."
mkdir -p .ssh
KEY_PATH=".ssh/id_rsa"

if [ ! -f "$KEY_PATH" ]; then
  echo "Generating SSH key at $KEY_PATH..."
  datetime=$(date +%Y%m%d_%H%M%S)
  ssh-keygen -t rsa -b 4096 -m PEM -C "system_test" -f "${KEY_PATH}_$datetime" -N ""
  mv "${KEY_PATH}_$datetime" "$KEY_PATH"
  mv "${KEY_PATH}_$datetime.pub" "${KEY_PATH}.pub"
else
  echo "SSH key already exists at $KEY_PATH, skipping generation."
fi

echo "Building Dokku container..."

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}$"; then
  echo "Stopping old Dokku container..."
  docker stop "$CONTAINER_NAME" && docker rm "$CONTAINER_NAME"
fi

docker compose up -d "$CONTAINER_NAME"

echo "Getting Dokku container IP address..."
DOKKU_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_NAME")

echo "Dokku container is running at $DOKKU_HOST!"

echo "Adding SSH key to Dokku..."
KEY_CONTENT=$(cat "${KEY_PATH}.pub")

set +e
docker exec "$CONTAINER_NAME" bash -c "echo \"$KEY_CONTENT\" >> /root/.ssh/authorized_keys"
docker exec "$CONTAINER_NAME" bash -c "echo \"$KEY_CONTENT\" | dokku ssh-keys:add key-\"$datetime\""
docker exec "$CONTAINER_NAME" bash -c "dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql;"
set -e

until nc -z $DOKKU_HOST 22; do
	echo "Waiting for SSH Server to be ready..."
done

echo "Configuring environment variables..."
cp .env.sample .env

sed -i "s|^MASTER_KEY=.*|MASTER_KEY=\"$MASTER_KEY\"|" .env
sed -i "s|^API_KEY=.*|API_KEY=\"$API_KEY\"|" .env
sed -i "s|^SSH_HOSTNAME=.*|SSH_HOSTNAME=$DOKKU_HOST|" .env
sed -i "s|^SSH_KEY_PATH=.*|SSH_KEY_PATH=$KEY_PATH|" .env
sed -i "s|^DB_HOST=.*|DB_HOST=localhost|" .env
sed -i "s|^HOST=.*|HOST=$DOKKU_API_HOST|" .env
sed -i "s|^PORT=.*|PORT=$DOKKU_API_PORT|" .env

echo "MASTER_KEY: $MASTER_KEY"
echo "API_KEY: $API_KEY"

echo "Setting up Dokku-API database..."
make docker-run-database

echo "Setting up Dokku-API..."
make run &
PID=$!

until nc -z $DOKKU_API_HOST $DOKKU_API_PORT; do
  echo "Waiting for Dokku-API to be ready..."
  sleep 3
done

echo "Started API process with PID: $PID"

poetry run python -m src.system_tests http://$DOKKU_API_HOST:$DOKKU_API_PORT $MASTER_KEY $API_KEY;
