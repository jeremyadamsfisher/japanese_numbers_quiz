run:
	uv run uvicorn main:app

lock:
	uv export --no-hashes --format requirements-txt > requirements.txt