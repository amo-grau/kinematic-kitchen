from typing import Any

from hexagon.driven_ports.for_preparing_orders import forPreparingOrders
from hexagon.order import Order


class forPreparingOrdersWithIsaacSim(forPreparingOrders):
    def __init__(self) -> None:
        self._node: Any = None
        self._publisher: Any = None

    def _ensure_initialised(self) -> None:
        if self._node is not None:
            return
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String

        if not rclpy.ok():
            rclpy.init()
        self._node = Node("kinematic_kitchen_publisher")
        self._publisher = self._node.create_publisher(
            String, "/kinematic_kitchen/prepare_order", 10
        )

    def prepare(self, order: Order) -> None:
        self._ensure_initialised()
        from std_msgs.msg import String

        msg = String()
        msg.data = order.id
        self._publisher.publish(msg)
