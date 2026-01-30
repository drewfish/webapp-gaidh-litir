
check-types: app/*.py
	uv run pyright $^

local-ci: app/*.py
	uv run ruff check $^
	make check-types
	shellcheck .render/*.sh

local-format: app/*.py
	uv run ruff check --fix $^
	uv run ruff format $^

local-run:
	uv run -- uvicorn --host 0.0.0.0 --port 8000 --reload app.main:app
