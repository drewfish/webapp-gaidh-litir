
PYTHON_FILES := $(wildcard app/*.py .render/*.py)
HTML_FILES := $(wildcard templates/*.html templates/*/*.html)

build-css:
	npx @tailwindcss/cli --minify --input ./app/tailwind.css --output ./static/tailwind.css

check-types: $(PYTHON_FILES)
	uv run pyright $^

local-setup:
	uv sync
	npm install
	@echo 'now run `source .venv/bin/activate.{sh,fish}`'
	@echo 'now run `nvm use`'

local-ci: $(PYTHON_FILES)
	uv run ruff check $^
	make check-types
	shellcheck .render/*.sh

local-format-html: $(HTML_FILES)
	uv run djhtml $^

local-format-python: $(PYTHON_FILES)
	uv run ruff check --fix $^
	uv run ruff format $^

local-format: $(PYTHON_FILES)
	make local-format-html
	make local-format-python

local-run:
	npx @tailwindcss/cli --input ./app/tailwind.css --output ./static/tailwind.css --watch=always &
	uv run -- uvicorn --host 0.0.0.0 --port 8000 --reload app.main:app

pre-commit:
	make build-css
	make local-format
	make local-ci
