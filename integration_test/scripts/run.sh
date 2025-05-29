#!/bin/bash
set -e

cd $DIR
chmod +x $INTEGRATION_TEST_DIR/scripts/*.sh

git config --global --add safe.directory $DIR

until nc -z $DOKKU_HOST 22; do
  echo "Waiting for Dokku to be ready..."
  sleep 2
done

mkdir -p ~/.ssh
ssh-keyscan $DOKKU_HOST >> ~/.ssh/known_hosts

# Call SSH instead of "dokku" directly
SSH_COMMAND="ssh root@${DOKKU_HOST} -i $INTEGRATION_TEST_DIR/.ssh/id_rsa -o StrictHostKeyChecking=no"
export GIT_SSH_COMMAND="ssh -i $INTEGRATION_TEST_DIR/.ssh/id_rsa -o StrictHostKeyChecking=no"

mkdir -p /tmp/dokku-wrapper
cat <<EOF > /tmp/dokku-wrapper/dokku
#!/bin/bash
exec ${SSH_COMMAND} dokku "\$@"
EOF

chmod +x /tmp/dokku-wrapper/dokku
export PATH="/tmp/dokku-wrapper:$PATH"

# Configure environment variables
$INTEGRATION_TEST_DIR/scripts/configure-env.sh "$DIR"
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git add .
git commit -m "dsafa"

# Clean up Dokku
set +e
dokku apps:list | tail -n +2 | xargs -n1 dokku apps:destroy --force
dokku mysql:list | tail -n +2 | xargs -n1 dokku mysql:destroy
set -e
make dokku-uninstall

# Deploy the application
make dokku-install