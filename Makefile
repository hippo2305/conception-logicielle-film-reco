run:
	uv run uvicorn api:app --reload

test:
	uv run pytest

lint:
	uv run ruff check src