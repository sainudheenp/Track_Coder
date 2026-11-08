.PHONY: install test check report docker-build

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

check: test
	python -m compileall -q trackcoder utils main.py
	ruff check main.py config.py trackcoder utils tests

report:
	python main.py report --html

docker-build:
	docker build -t track-coder .
