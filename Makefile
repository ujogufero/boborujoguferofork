.PHONY: install lock sync dev shell format serve routes limiters deploy logs help noop

.DEFAULT_GOAL := help

HOST = 127.0.0.1
PORT = 5000

PYTHON ?= python
POETRY ?= poetry
FLYCTL ?= flyctl

install: ## poetry install
	$(POETRY) install

lock: ## poetry lock
	$(POETRY) lock

sync: ## poetry sync
	$(POETRY) sync

dev: ## poetry run flask run --host HOST --port PORT (default: 127.0.0.1:5000)
	$(POETRY) run flask run --host $(HOST) --port $(PORT)

shell: ## poetry run flask shell
	$(POETRY) run flask shell

format: ## poetry run black .
	$(POETRY) run black .

serve: ## poetry run gunicorn -b HOST:PORT app:app (default 127.0.0.1:5000)
	$(POETRY) run gunicorn -b $(HOST):$(PORT) app:app

routes: ## poetry run flask routes
	$(POETRY) run flask routes

limiters: ## poetry run flask limiter limits
	$(POETRY) run flask limiter limits

deploy: ## fly deploy
	$(FLYCTL) deploy

logs: ## fly logs
	$(FLYCTL) logs

help: ## make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

%: noop ## Avoid "nothing to be done" for any target that doesn't have a rule
	@:
