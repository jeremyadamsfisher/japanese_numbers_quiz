run:
	@uv run uvicorn main:app

lock:
	@uv export --no-hashes --format requirements-txt > requirements.txt

clean:
	@uvx isort .
	@uvx ruff format .
	# % brew install prettier
	@prettier --write templates/*.html