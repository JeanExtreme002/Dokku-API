ifeq ($(filter help install,$(MAKECMDGOALS)),)
  include .env
endif

RED=\033[0;31m
YELLOW=\033[0;33m
GREEN=\033[0;32m
NC=\033[0m # No Color

TIMESTAMP     := $(shell date +%s)
SSH_DIR       ?= $(HOME)/.ssh

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
	@{ \
		echo "$(GREEN)Running tests...$(NC)"; \
		PYTHONPATH=. poetry run python -m coverage run -m unittest discover -s src/tests -p "test_*.py" -t . --verbose; \
		echo "$(GREEN)Generating coverage report...$(NC)"; \
		poetry run coverage report; \
	}

.PHONY: system-test
system-test:  ## Run system tests
	@{ \
		MASTER_KEY="abcd12345678-system-test"; \
		API_KEY="abc123-system-test"; \
		bash -l ./src/system_tests/build.sh dokku "$$MASTER_KEY" "$$API_KEY"; \
	}

.PHONY: build
build:  ## Build the package for PyPI distribution
	@echo "$(GREEN)Building package for PyPI...$(NC)"
	@poetry build
	@echo "$(GREEN)Package built successfully!$(NC)"
	@echo "$(YELLOW)Built files:$(NC)"
	@ls -la dist/

.PHONY: check-package
check-package:  ## Check package integrity using twine
	@echo "$(GREEN)Checking package integrity...$(NC)"
	@if [ ! -d "dist/" ] || [ -z "$$(ls -A dist/)" ]; then \
		echo "$(YELLOW)No dist/ folder found or it's empty. Building first...$(NC)"; \
		make build; \
	fi
	@poetry run twine check dist/*
	@echo "$(GREEN)Package check completed!$(NC)"

.PHONY: publish
publish:  ## Publish package to PyPI using twine
	@echo "$(GREEN)Publishing to PyPI using twine...$(NC)"
	@if [ ! -d "dist/" ] || [ -z "$$(ls -A dist/)" ]; then \
		echo "$(YELLOW)No dist/ folder found or it's empty. Building first...$(NC)"; \
		make build; \
	fi
	@echo "$(YELLOW)You'll need your PyPI API token.$(NC)"
	@echo "$(YELLOW)Get it from: https://pypi.org/manage/account/token/$(NC)"
	@read -p "Enter your PyPI token: " token; \
	TWINE_USERNAME=__token__ TWINE_PASSWORD=$$token poetry run twine upload dist/*
	@echo "$(GREEN)Package published to PyPI!$(NC)"
	@echo "$(YELLOW)Install with: pip install dokku-api$(NC)"

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
docker-test:
	@docker compose up --exit-code-from unit-test unit-test

.PHONY: docker-lint
docker-lint:
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

.PHONY: get-env-path
get-env-path:  ## Get the absolute path of the .env file
	@{ \
		if [ -f ".env" ]; then \
			realpath .env; \
		else \
			echo "$(RED)ERROR: .env file not found in current directory$(NC)"; \
			exit 1; \
		fi; \
	}

.PHONY: help
help:  ## List commands
	@echo ""; \
	echo "$(GREEN)Dokku API - Available Commands$(NC)"; \
	echo ""; \
	echo "$(YELLOW)Docker Deployment:$(NC)"; \
	grep -E '^(docker-run|docker-run-database|docker-run-api|docker-stop):.*?## ' Makefile | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'; \
	echo ""; \
	echo "$(YELLOW)Development:$(NC)"; \
	grep -E '^(run|install|test|system-test|lint|lint-fix|commit|build|check-package|publish):.*?## ' Makefile | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'; \
	echo ""; \
	echo "$(YELLOW)Utilities:$(NC)"; \
	grep -E '^(generate-ssh-key|get-ip|get-env-path):.*?## ' Makefile | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'; \
	echo ""; \