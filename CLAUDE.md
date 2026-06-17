# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kinematic Kitchen is a robotics simulation of a high-throughput fast-food restaurant (digital twin), automating the end-to-end burger assembly pipeline. It uses **NVIDIA Isaac Sim** for physics/rendering and **ROS 2** for robotic control/middleware.

## Architecture

The project follows **Hexagonal Architecture (Ports and Adapters)** with three explicit layers:

- **Core Domain** — kitchen state machine, recipe logic, order queuing. No dependencies on ROS or Isaac Sim.
- **Ports** — abstract interfaces defined as abstract Python classes, named following the `forDoingSomething` convention. Define how the core domain interacts with the outside world (simulation, hardware, UI).
  - Driving ports live in `hexagon/driving_ports/`
  - Driven ports live in `hexagon/driven_ports/`

- **Adapters** — concrete implementations that plug into the ports: ROS 2 action clients, Isaac Sim bridges, UI controllers.
  - Driven adapters implement a driven port; placed under `driven_adapters/<port>/`, named `forDoingSomethingWith<Technology>`.
  - Driving adapters hold and use a driving port; placed under `driving_adapters/<port>/`, named `forDoingSomethingWith<Technology>`.

The key invariant: core business logic (cooking times, recipe states, order management) must never import ROS or Isaac Sim directly. All simulation/hardware coupling flows through adapters that implement the port interfaces.

## Test-Driven Development

Domain code (core state machine, recipe logic, order queuing) must be written test-first: write a failing test, make it pass with the minimal implementation, then refactor. No domain class or method should exist without a corresponding test written before it.

Adapter and integration tests follow after the port interface is defined — the port contract is the spec.

## Coding Principles

- **SOLID:** Each class has one reason to change (SRP); depend on port interfaces, not concrete adapters (DIP); extend behaviour by adding new adapters, not modifying existing ones (OCP); keep interfaces narrow and role-specific (ISP); subtypes must be substitutable for their base (LSP).
- **Command Query Separation:** Methods either mutate state (commands, return nothing) or return data (queries, cause no side effects) — never both. This is especially important for the core domain where state transitions must be explicit and auditable.
- **Dependency direction:** Dependencies always point inward — adapters depend on ports, ports depend on the core domain, the core domain depends on nothing external.

## Continuous Integration

The deployment target is a **Docker container**. CI is the gate that proves the image is safe to ship.

A passing CI pipeline is required before any branch can be merged to `main`. The pipeline must:

1. **Unit tests** — run all domain tests; any failure blocks the merge.
2. **Linting** — enforce code style (e.g. `ruff check .`); fail on violations.
3. **Type checking** — run `mypy` (or `pyright`) across the codebase; fail on errors.
4. **Docker build** — build the container image to confirm it assembles cleanly.

Domain tests must be runnable inside the Docker image without Isaac Sim or a live ROS 2 environment — this is a direct consequence of the hexagonal architecture keeping the core domain dependency-free.

## Technology Stack

- **NVIDIA Isaac Sim** — physics simulation, photorealistic rendering, robot articulation
- **ROS 2** — inter-node communication, trajectory planning, robot control interfaces
- **Python** — primary language (standard for both ROS 2 nodes and Isaac Sim scripting)
