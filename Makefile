VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: install lint lint-domain typecheck typecheck-domain test test-domain docker-build docker-test

# --system-site-packages lets the venv see apt-installed packages (numpy, yaml)
# that ROS 2's rclpy depends on, so the Isaac Sim adapter tests can run locally
# when ROS 2 is sourced. CI never sources ROS 2 and runs domain tests only.
$(VENV):
	python3 -m venv --system-site-packages $(VENV)

install: $(VENV)
	$(PIP) install -e ".[dev]" -q

lint:
	$(VENV)/bin/ruff check .

lint-domain:
	$(VENV)/bin/ruff check hexagon hexagon_tests

typecheck:
	$(VENV)/bin/mypy hexagon driven_adapters driving_adapters configuration

typecheck-domain:
	$(VENV)/bin/mypy hexagon

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(VENV)/bin/pytest --tb=short || [ $$? -eq 5 ]

test-domain:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(VENV)/bin/pytest hexagon_tests/ --tb=short

docker-build:
	docker build -t kinematic-kitchen .

docker-test:
	docker run --rm kinematic-kitchen
