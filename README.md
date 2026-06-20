# 🍔 Kinematic Kitchen

**Kinematic Kitchen** is an advanced robotics simulation project that creates a digital twin of a high-throughput fast-food restaurant. Leveraging **NVIDIA Isaac Sim** for high-fidelity physics and rendering, and **ROS 2** for robotic control and middleware, this project automates the end-to-end pipeline of burger assembly.

Unlike monolithic simulation scripts, Kinematic Kitchen strictly adheres to **Hexagonal Architecture (Ports and Adapters)**. By isolating the core business logic—such as order management, cooking times, and recipe states—from the simulation environment and ROS middleware, the system remains highly modular, testable, and hardware-agnostic.

## 🛠️ Core Technologies
*   **NVIDIA Isaac Sim:** Provides photorealistic rendering, accurate rigid-body physics, and robot articulation.
*   **ROS 2:** Handles inter-node communication, trajectory planning, and robot control interfaces.
*   **Hexagonal Architecture:** 
    *   **Core Domain:** Kitchen state machine, recipe logic, and order queuing.
    *   **Ports:** Interfaces defining how the kitchen interacts with the physical/simulated world.
    *   **Adapters:** ROS 2 action clients, Isaac Sim bridges, and UI controllers that plug into the core domain.

## 🎯 Project Goals
1.  **Digital Twin Automation:** Simulate a complete Quick Service Restaurant (QSR) environment.
2.  **Robotic Manipulation:** Automate tasks like flipping patties, moving buns, and packaging orders using simulated robotic arms and end-effectors.
3.  **Modular Engineering:** Prove that complex robotic simulations can maintain clean, decoupled software architecture.



## Development

```bash
make install   # set up virtualenv and install dev dependencies
make test      # run domain tests
make lint      # check code style
make typecheck # run static type checker
```

CI runs automatically on every pull request. A passing pipeline (lint + typecheck + tests + Docker build) is required before merging to main.