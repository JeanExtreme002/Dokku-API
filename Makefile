include .env

RED=\033[0;31m
YELLOW=\033[0;33m
GREEN=\033[0;32m
NC=\033[0m # No Color

TIMESTAMP     := $(shell date +%s)
SSH_DIR       ?= $(HOME)/.ssh

FORMATTED_API_NAME := $$(echo "$(API_NAME)" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

.PHONY:
run:  ## Run the API locally
	@poetry run python -m src

.PHONY:
install:  ## Install the API dependencies locally
	@pip install poetry && poetry install --with dev --no-root

.PHONY: test
test:  ## Run unit tests
	@poetry run coverage run -m unittest discover -s src.tests --verbose && poetry run coverage report;

.PHONY: lint
lint:  ## Run lint
	@poetry run flake8 src && poetry run yapf -r --diff src > /dev/null

.PHONY: lint-fix
lint-fix:  ## Run lint fix
	@{ \
		poetry run isort src; \
		\
		EXIT_CODE=$$(poetry run flake8 src > /dev/null 2>&1; echo $$?); \
		\
		if [ "$$EXIT_CODE" -ne 0 ]; then \
		  poetry run black src --quiet; \
		fi; \
		\
		poetry run yapf -r -i src; \
	}

.PHONY: dokku-install
dokku-install:  ## Install and run the API on Dokku.
	@{ \
		FORMATTED_API_NAME=$(FORMATTED_API_NAME); \
		\
		echo "Creating Dokku app $$FORMATTED_API_NAME"; \
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
		if [ -z "$(SSH_HOSTNAME)" ] || [ -z "$(RSA_KEY_FILE)" ]; then \
			echo "$(RED)ERROR: SSH_HOSTNAME, RSA_KEY_FILE, and FORMATTED_API_NAME are required.$(NC)"; \
			exit 1; \
		fi; \
		\
		echo "$(GREEN)Using SSH host: $(SSH_HOSTNAME)$(NC)"; \
		echo "$(GREEN)Reading RSA private key from: $(RSA_KEY_FILE)$(NC)"; \
		echo "$(GREEN)Using Dokku app: $$FORMATTED_API_NAME$(NC)"; \
		\
		SSH_KEY_PATH="/$$FORMATTED_API_NAME/id_rsa"; \
		RSA_KEY_PASSPHRASE=$$(sed ':a;N;$$!ba;s/\n/\\n/g' $(RSA_KEY_FILE)); \
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
			SSH_HOSTNAME='$(SSH_HOSTNAME)' \
			SSH_PORT='$(SSH_PORT)' \
			SSH_KEY_PATH="$$SSH_KEY_PATH" \
			SSH_KEY_PASSPHRASE="$$RSA_KEY_PASSPHRASE" \
			API_KEY="$$API_KEY" \
			MASTER_KEY=$(MASTER_KEY); \
		\
		mkdir -p "/$$FORMATTED_API_NAME"; \
		cp $(RSA_KEY_FILE) /$$FORMATTED_API_NAME/id_rsa; \
		chmod 644 /$$FORMATTED_API_NAME/id_rsa; \
		\
		if ! dokku storage:report $$FORMATTED_API_NAME | grep -q "/$$FORMATTED_API_NAME/:/$$FORMATTED_API_NAME/"; then \
			dokku storage:mount $$FORMATTED_API_NAME /$$FORMATTED_API_NAME/:/$$FORMATTED_API_NAME/; \
		fi; \
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