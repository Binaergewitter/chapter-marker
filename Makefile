lint:
	poetry run flake8 --max-line-length 100 chapter_marker
format:
	poetry run black chapter_marker
