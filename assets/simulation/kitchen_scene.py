"""
Minimal Isaac Sim 6.0 kitchen scene.

Run headlessly:
    ./python.sh assets/simulation/kitchen_scene.py

The scene opens a stage with a ground plane, a distant light, and a Franka
Panda arm loaded from the Isaac Sim asset library.  The isaacsim.ros2.bridge
extension is enabled so the scene subscribes to
/kinematic_kitchen/prepare_order (std_msgs/String, payload: order ID).  On
each message the arm executes a simple reach-and-return joint motion
representing order preparation.
"""

import sys

import carb
from isaacsim.simulation_app import SimulationApp

simulation_app = SimulationApp({"headless": False})

# All Omniverse imports must come after SimulationApp is instantiated.
import numpy as np
import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation
from isaacsim.storage.native import get_assets_root_path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# ---------------------------------------------------------------------------------
# Enable ROS 2 bridge extension
# ---------------------------------------------------------------------------------

app_utils.enable_extension("isaacsim.ros2.bridge")
simulation_app.update()

# ---------------------------------------------------------------------------------
# Scene setup
# ---------------------------------------------------------------------------------

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit(1)

stage_utils.create_new_stage()

GroundPlane("/World/GroundPlane")
light = DistantLight("/World/DistantLight")
light.set_intensities(300)

franka_usd = assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
stage_utils.add_reference_to_stage(usd_path=franka_usd, path="/World/Franka")

franka = Articulation("/World/Franka")

app_utils.play()
simulation_app.update()

# ---------------------------------------------------------------------------------
# ROS 2 preparation subscriber
# ---------------------------------------------------------------------------------

_pending_orders: list[str] = []


class PrepareOrderSubscriber(Node):
    def __init__(self) -> None:
        super().__init__("kinematic_kitchen_scene")
        self.create_subscription(
            String,
            "/kinematic_kitchen/prepare_order",
            self._on_prepare_order,
            10,
        )

    def _on_prepare_order(self, msg: String) -> None:
        self.get_logger().info(f"Preparing order: {msg.data}")
        _pending_orders.append(msg.data)


rclpy.init()
subscriber = PrepareOrderSubscriber()

# ---------------------------------------------------------------------------------
# Joint motion helpers
# ---------------------------------------------------------------------------------

# Franka home configuration (7 arm joints + 2 finger joints = 9 DOF)
_HOME = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785, 0.04, 0.04])
_REACH = np.array([0.0, 0.2, 0.0, -1.6, 0.0, 1.8, 0.785, 0.04, 0.04])

_REACH_STEPS = 60
_RETURN_STEPS = 60
_TOTAL_STEPS = _REACH_STEPS + _RETURN_STEPS


def _lerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    return a + (b - a) * t


def _target_for_frame(frame: int) -> np.ndarray:
    if frame < _REACH_STEPS:
        return _lerp(_HOME, _REACH, frame / _REACH_STEPS)
    return _lerp(_REACH, _HOME, (frame - _REACH_STEPS) / _RETURN_STEPS)


# ---------------------------------------------------------------------------------
# Simulation loop
# ---------------------------------------------------------------------------------

_motion_frame = 0
_active_order: str | None = None

while simulation_app.is_running():
    rclpy.spin_once(subscriber, timeout_sec=0.0)
    simulation_app.update()

    if _active_order is None and _pending_orders:
        _active_order = _pending_orders.pop(0)
        _motion_frame = 0
        subscriber.get_logger().info(f"Starting motion for order {_active_order}")

    if _active_order is not None:
        franka.set_dof_position_targets(_target_for_frame(_motion_frame))
        _motion_frame += 1
        if _motion_frame >= _TOTAL_STEPS:
            subscriber.get_logger().info(f"Order {_active_order} preparation complete")
            _active_order = None

subscriber.destroy_node()
rclpy.shutdown()
simulation_app.close()
