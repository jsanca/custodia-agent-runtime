.PHONY: server-install server-test server-lint server-typecheck server-check docker-up docker-down

server-install:
	cd server && uv sync

server-test:
	cd server && uv run pytest

server-lint:
	cd server && uv run ruff check .

server-typecheck:
	cd server && uv run mypy .

server-check: server-test server-lint server-typecheck

docker-up:
	docker compose up --build

docker-down:
	docker compose down