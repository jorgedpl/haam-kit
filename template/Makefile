# Command contract shared by agents, CI and humans.
# Agents and CI only ever call these targets, so each project fills them in once.
# TODO(setup): replace each `@echo TODO ...; exit 1` with the real command for your stack.
# Examples are given in comments for Node, Python and PHP/Laravel.

.PHONY: setup hooks dev test lint typecheck build check audit secrets e2e smoke deploy

setup:  ## Install dependencies
	@echo "TODO(setup): make setup"; exit 1
#   Node:    npm ci
#   Python:  pip install -r requirements.txt -r requirements-dev.txt
#   Laravel: composer install && npm ci

hooks:  ## Turn on the secret scan before every commit (keeps your own git hooks working). Run once per clone.
	python3 tools/haam/haam.py hooks --apply

dev:  ## Run the app locally (used for UAT)
	@echo "TODO(setup): make dev"; exit 1
#   Node:    npm run dev
#   Python:  python manage.py runserver   /   uvicorn app.main:app --reload
#   Laravel: php artisan serve

test:  ## Unit tests
	@echo "TODO(setup): make test"; exit 1
#   Node:    npm test
#   Python:  pytest -q
#   Laravel: php artisan test

lint:  ## Lint and format check
	@echo "TODO(setup): make lint"; exit 1
#   Node:    npm run lint
#   Python:  ruff check . && ruff format --check .
#   Laravel: ./vendor/bin/pint --test

typecheck:  ## Type checks (make it a no-op if your stack has none)
	@echo "TODO(setup): make typecheck"; exit 1
#   Node:    npx tsc --noEmit
#   Python:  mypy .
#   Laravel: ./vendor/bin/phpstan analyse

build:  ## Production build
	@echo "TODO(setup): make build"; exit 1
#   Node:    npm run build

check: lint typecheck test build  ## Everything CI runs. Must pass before any PR.

audit:  ## Dependency vulnerability audit (fails on high/critical)
	@echo "TODO(setup): make audit"; exit 1
#   Node:    npm audit --audit-level=high
#   Python:  pip-audit
#   Laravel: composer audit

secrets:  ## Scan uncommitted changes for secrets (same check as the pre-commit hook)
	@bash scripts/scan-secrets.sh

e2e:  ## End-to-end / browser tests (optional)
	@echo "No e2e tests configured yet"

smoke:  ## Post-deploy smoke test. Usage: SMOKE_URL=https://... make smoke
	@test -n "$(SMOKE_URL)" || (echo "SMOKE_URL not set"; exit 1)
	@curl -fsS -o /dev/null -w "%{http_code} $(SMOKE_URL)\n" "$(SMOKE_URL)"
#   TODO(setup): add a health endpoint check, e.g. curl -fsS "$(SMOKE_URL)/health"

deploy:  ## Production deploy. Only ever run by deploy.yml in GitHub Actions.
	@test "$(CI)" = "true" || (echo "Refusing to deploy outside CI"; exit 1)
	@echo "TODO(setup): make deploy"; exit 1
