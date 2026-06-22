# Recipes source ROS 2's setup.bash, which uses bash-only syntax, so run them
# under bash rather than the default /bin/sh (dash).
SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Overridable locations for the live `run` target (Isaac Sim + ROS 2).
ISAAC_SIM ?= $(HOME)/isaacsim
ROS_SETUP ?= /opt/ros/jazzy/setup.bash
SCENE := assets/simulation/kitchen_scene.py
TOPIC := /kinematic_kitchen/prepare_order
ORDER ?= patty,bun,sauce

.PHONY: install lint lint-domain typecheck typecheck-domain test test-domain run docker-build docker-test

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

# Launch the Isaac Sim scene and submit one order in a single command. The
# scene takes 30-60s to load, so we wait for its subscriber to appear before
# submitting -- otherwise the order would be published before anything is
# listening and the arm would not move. Override ORDER=... to change the items.
run:
	@if [ ! -x "$(ISAAC_SIM)/python.sh" ]; then \
		echo "Isaac Sim not found at $(ISAAC_SIM). Set ISAAC_SIM=/path/to/isaacsim" >&2; exit 1; fi
	@if [ ! -f "$(ROS_SETUP)" ]; then \
		echo "ROS 2 setup not found at $(ROS_SETUP). Set ROS_SETUP=/path/to/setup.bash" >&2; exit 1; fi
	@set -e; \
	. "$(ROS_SETUP)"; \
	echo "Starting Isaac Sim scene (this can take 30-60s to load)..."; \
	"$(ISAAC_SIM)/python.sh" $(SCENE) & \
	SCENE_PID=$$!; \
	trap 'kill $$SCENE_PID 2>/dev/null' EXIT; \
	echo "Waiting for the scene to subscribe to $(TOPIC)..."; \
	for i in $$(seq 1 120); do \
		if ros2 topic info $(TOPIC) 2>/dev/null | grep -q 'Subscription count: [1-9]'; then \
			READY=1; break; \
		fi; \
		if ! kill -0 $$SCENE_PID 2>/dev/null; then \
			echo "Scene exited before becoming ready." >&2; exit 1; fi; \
		sleep 1; \
	done; \
	if [ -z "$$READY" ]; then echo "Timed out waiting for the scene." >&2; exit 1; fi; \
	echo "Scene ready. Submitting order: $(ORDER)"; \
	$(VENV)/bin/python -m kinematic_kitchen submit "$(ORDER)"; \
	echo "Order submitted. Scene is running -- press Ctrl+C to stop."; \
	wait $$SCENE_PID

docker-build:
	docker build -t kinematic-kitchen .

docker-test:
	docker run --rm kinematic-kitchen
