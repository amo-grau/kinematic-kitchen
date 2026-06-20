VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: install lint typecheck test docker-build docker-test

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)
	$(PIP) install -e ".[dev]" -q

lint:
	$(VENV)/bin/ruff check .

typecheck:
	$(VENV)/bin/mypy hexagon driven_adapters driving_adapters configuration

test:
	$(VENV)/bin/pytest --tb=short || [ $$? -eq 5 ]

docker-build:
	docker build -t kinematic-kitchen .

docker-test:
	docker run --rm kinematic-kitchen
