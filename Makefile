ifeq ($(filter help install,$(MAKECMDGOALS)),)
  include .env
endif

RED=\033[0;31m
YELLOW=\033[0;33m
GREEN=\033[0;32m
NC=\033[0m # No Color

TIMESTAMP     := $(shell date +%s)
SSH_DIR       ?= $(HOME)/.ssh

FORMATTED_API_NAME := $$(echo "$(API_NAME)" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

.PHONY: run
run:  ## Run the API locally
	@poetry run python -m src

.PHONY: install
install:  ## Install the API dependencies locally
	@command -v poetry >/dev/null 2>&1 || (echo "$(YELLOW)Installing Poetry...$(NC)" && pip install poetry)
	@poetry install --with dev --no-root

.PHONY: commit
commit:  ## Commit changes on local repository
	@poetry run cz commit

.PHONY: test
test:  ## Run unit tests
	@poetry run coverage run -m unittest discover -s src.tests --verbose && poetry run coverage report;

.PHONY: system-test
system-test:  ## Run system tests
	@{ \
		MASTER_KEY="abcd12345678-system-test"; \
		API_KEY="abc123-system-test"; \
		bash -l ./src/system_tests/build.sh dokku "$$MASTER_KEY" "$$API_KEY"; \
	}

.PHONY: lint
lint:  ## Run lint
	@poetry run flake8 src && poetry run black --check src

.PHONY: lint-fix
lint-fix:  ## Run lint fix
	@{ \
		poetry run isort src; \
		\
		poetry run black src; \
	}

.PHONY: dokku-install
dokku-install:  ## Install and run the API on Dokku.
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		echo "Creating Dokku app '$$FORMATTED_API_NAME'"; \
		dokku apps:create $$FORMATTED_API_NAME && \
		\
		make dokku-create-db && \
		\
		make dokku-deploy; \
	}

.PHONY: dokku-deploy
dokku-deploy:  ## Deploy the API to the Dokku (use dokku-install first).
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		REPO_NAME="dokku@$(SSH_HOSTNAME):$$FORMATTED_API_NAME"; \
		\
		make dokku-set-config;\
		\
		if git remote get-url dokku &> /dev/null; then \
		  git remote remove dokku; \
		fi; \
		git remote add dokku $$REPO_NAME && \
		\
		dokku buildpacks:clear $$FORMATTED_API_NAME && \
		dokku buildpacks:add $$FORMATTED_API_NAME https://github.com/heroku/heroku-buildpack-python.git && \
		\
		git push dokku; \
	}

.PHONY: dokku-create-db
dokku-create-db:
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql; \
		dokku mysql:create "$$FORMATTED_API_NAME-database"; \
		dokku mysql:link "$$FORMATTED_API_NAME-database" $$FORMATTED_API_NAME; \
	}

.PHONY: dokku-destroy-db
dokku-destroy-db:
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		dokku mysql:destroy $$FORMATTED_API_NAME-database --force; \
	}

.PHONY: set-config
dokku-set-config:
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		if [ -z "$(SSH_HOSTNAME)" ] || [ -z "$(SSH_KEY_PATH)" ]; then \
			echo "$(RED)ERROR: SSH_HOSTNAME, SSH_KEY_PATH, and FORMATTED_API_NAME are required.$(NC)"; \
			exit 1; \
		fi; \
		\
		echo "$(GREEN)Using SSH host: $(SSH_HOSTNAME)$(NC)"; \
		echo "$(GREEN)Reading RSA private key from: $(SSH_KEY_PATH)$(NC)"; \
		echo "$(GREEN)Using Dokku app: $$FORMATTED_API_NAME$(NC)"; \
		\
		if [ -z "$(API_KEY)" ]; then \
			echo "$(YELLOW)WARNING: No API_KEY in .env. Generating a new one...$(NC)"; \
			API_KEY=$$(curl -s https://www.uuidgenerator.net/api/version4); \
		else \
			API_KEY="$(API_KEY)"; \
		fi; \
		\
		dokku config:set $$FORMATTED_API_NAME \
			API_NAME='$(API_NAME)' \
			API_VERSION_NUMBER='$(API_VERSION_NUMBER)' \
			VOLUME_DIR='$(VOLUME_DIR)' \
			SSH_HOSTNAME='$(SSH_HOSTNAME)' \
			SSH_PORT='$(SSH_PORT)' \
			SSH_KEY_PATH="/$$FORMATTED_API_NAME/id_rsa" \
			API_KEY="$$API_KEY" \
			MASTER_KEY=$(MASTER_KEY) \
			AVAILABLE_DATABASES=$(AVAILABLE_DATABASES); \
		\
		mkdir -p "/$$FORMATTED_API_NAME"; \
		cp $(SSH_KEY_PATH) /$$FORMATTED_API_NAME/id_rsa; \
		chmod 644 /$$FORMATTED_API_NAME/id_rsa; \
		\
		if ! dokku storage:report $$FORMATTED_API_NAME | grep -q "/$$FORMATTED_API_NAME/:/$$FORMATTED_API_NAME/"; then \
			dokku storage:mount $$FORMATTED_API_NAME /$$FORMATTED_API_NAME/:/$$FORMATTED_API_NAME/; \
		fi; \
		\
		dokku nginx:set $$FORMATTED_API_NAME client-max-body-size $(CLIENT_MAX_BODY_SIZE); \
		dokku proxy:build-config $$FORMATTED_API_NAME; \
		\
		printf "$(GREEN)Using API_KEY=$$API_KEY$(NC)\n"; \
	}


.PHONY: dokku-uninstall
dokku-uninstall:  ## Stop and uninstall the API on Dokku
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		echo "Destroying Dokku app $$FORMATTED_API_NAME"; \
		dokku apps:destroy $$FORMATTED_API_NAME --force; \
		\
		make dokku-destroy-db; \
		\
		rm -rf "/$$FORMATTED_API_NAME"; \
	}

.PHONY: docker-run  
docker-run:  ## Run the entire project (API + Database locally) on Docker
	make docker-run-database
	make docker-run-api

.PHONY: docker-run-database
docker-run-database:  ## Run a MySQL database on Docker
	@docker compose up -d mysql

.PHONY: docker-run-api
docker-run-api:  ## Run the API on Docker
	@docker compose up dokku_api

.PHONY: docker-test
docker-test:  ## Run unit tests on Docker
	@docker compose up --exit-code-from unit-test unit-test

.PHONY: docker-lint
docker-lint:  ## Run lint on Docker
	@docker compose up --exit-code-from lint lint

.PHONY: docker-stop
docker-stop:  ## Stop the entire project on Docker
	docker compose down

.PHONY: generate-ssh-key
generate-ssh-key:  ## Generate SSH key and upload it to Dokku | Arg: key_name=<name>
	@{ \
		KEY_NAME=$${key_name}; \
		\
		if [ -z "$$KEY_NAME" ]; then \
			echo "$(RED)ERROR: Please, set the 'key_name' argument.$(NC)"; \
			exit 1; \
		fi; \
		\
		KEY_NAME="id_$(TIMESTAMP)_$$KEY_NAME"; \
		KEY_PATH=$(SSH_DIR)/$$KEY_NAME; \
		\
		echo "Generating SSH key named: $$KEY_NAME..."; \
		\
		if [ -f $$KEY_PATH ]; then \
			echo "SSH key $$KEY_PATH already exists. Skipping generation."; \
		else \
			ssh-keygen -t ed25519 -f $$KEY_PATH -N ""; \
			echo "SSH key generated at: $$KEY_PATH"; \
		fi; \
		\
		echo "Uploading public key to Dokku server..."; \
		cat $$KEY_PATH.pub | dokku ssh-keys:add $$KEY_NAME && \
		echo "$(GREEN)SSH key successfully added to Dokku as: $$KEY_PATH$(NC)"; \
	}

.PHONY: get-ip
get-ip:  ## Get the private IP address of the machine
	@{ \
		IP=$$(ip addr show | awk '/inet / && !/127.0.0.1/ { sub("/.*", "", $$2); print $$2; exit }'); \
		echo "Private IP address: $$IP"; \
	}

.PHONY: help
help:  ## List commands
	@echo ""; \
	echo "Available commands:"; \
	echo ""; \
	grep -E '^[a-zA-Z0-9_-]+:.*?## ' Makefile | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'; \
	echo ""