
check-types: app/*.py
	uv run pyright $^

local-setup:
	uv sync
	@echo 'now run `source .venv/bin/activate.{sh,fish}`'

local-ci: app/*.py
	uv run ruff check $^
	make check-types
	shellcheck .render/*.sh

local-format-html: templates/*.html templates/*/*.html
	uv run djhtml $^

local-format-python: app/*.py
	uv run ruff check --fix $^
	uv run ruff format $^

local-format: app/*.py
	make local-format-html
	make local-format-python

local-run:
	uv run -- uvicorn --host 0.0.0.0 --port 8000 --reload app.main:app
