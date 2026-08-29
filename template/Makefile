.PHONY: setup hooks board dev dev-down dev-logs db-reset check verify gen lint typecheck test

setup: hooks ## first time on a machine
	@echo ">> setup complete"

hooks: ## install the git hooks (refuses a push to the default branch)
	git config core.hooksPath .githooks
	@echo ">> hooks installed. Override deliberately: ALLOW_PUSH_DEFAULT=1"

board: ## the progress board in a browser
	python tools/board.py

check: ## the fast gate. Seconds, no toolchains. Run before every push
	@python tools/no_placeholders.py
	@python tools/dep_check.py
	@python tools/ownership_check.py
	@python tools/track.py check
	@echo ">> fast gate passed. `make verify` also runs lint, types and tests."

verify: check lint typecheck test ## everything CI runs

dev: ## start the local stack
	@test -f .env || (cp .env.example .env 2>/dev/null && echo ">> created .env") || true
	docker compose up -d

dev-down: ## stop the local stack, keep the data
	docker compose down

db-reset: ## wipe and restart. Destroys local data only
	docker compose down -v
	@$(MAKE) dev

# A language runs only when source of that language exists. A bare directory is
# not code, and CI must not fail on a toolchain nothing needs yet.
has = $(shell find $(1) -name '$(2)' -not -path '*/node_modules/*' 2>/dev/null | head -1)

lint: ## all linters. a new warning is a failure
	@echo ">> add your linters here, guarded by $(call has,dir,pattern)"

typecheck: ## strict mode everywhere
	@echo ">> add your typecheckers here"

test: ## every test, every language
	@echo ">> add your test runners here"

gen: ## regenerate anything generated, from its source
	@echo ">> add your generator here"
