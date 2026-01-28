
check-types: *.py
	uv run pyright $^

local-ci: *.py
	uv run ruff check $^
	make check-types

local-format: *.py
	uv run ruff check --fix $^
	uv run ruff format $^

