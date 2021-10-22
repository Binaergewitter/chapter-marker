lint:
	poetry run pflake8 chapter_marker
format:
	poetry run isort --apply
	poetry run black chapter_marker
