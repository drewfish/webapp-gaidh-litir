
build-css:
	npx @tailwindcss/cli --minify --input ./app/tailwind.css --output ./static/tailwind.css

check-types: app/*.py
	uv run pyright $^

local-setup:
	uv sync
	npm install
	@echo 'now run `source .venv/bin/activate.{sh,fish}`'
	@echo 'now run `nvm use`'

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
	npx @tailwindcss/cli --input ./app/tailwind.css --output ./static/tailwind.css --watch &
	uv run -- uvicorn --host 0.0.0.0 --port 8000 --reload app.main:app

pre-commit:
	make build-css
	make local-ci
