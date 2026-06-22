import time

import pytest

# These are integration tests for the Isaac Sim adapter: they require a working
# ROS 2 environment (rclpy). When ROS 2 is not available — e.g. in CI or the
# Docker image — the whole module is skipped rather than failing.
rclpy = pytest.importorskip("rclpy")

from rclpy.node import Node
from std_msgs.msg import String

from driven_adapters.forPreparingOrders.for_preparing_orders_with_isaac_sim import (
    forPreparingOrdersWithIsaacSim,
)
from hexagon.driven_ports.for_preparing_orders import forPreparingOrders
from hexagon.order import Order

TOPIC = "/kinematic_kitchen/prepare_order"


def test_prepare_does_not_raise() -> None:
    adapter: forPreparingOrders = forPreparingOrdersWithIsaacSim()
    order = Order("order-1", ["burger"])

    adapter.prepare(order)


def test_prepare_publishes_the_order_id() -> None:
    received: list[str] = []
    listener = Node("test_listener")
    listener.create_subscription(
        String, TOPIC, lambda msg: received.append(msg.data), 10
    )

    adapter: forPreparingOrders = forPreparingOrdersWithIsaacSim()
    order = Order("order-1", ["burger"])

    # Let the subscriber discover the adapter's publisher before publishing,
    # then publish and spin briefly to receive the message.
    deadline = time.time() + 5.0
    while time.time() < deadline and not received:
        adapter.prepare(order)
        rclpy.spin_once(listener, timeout_sec=0.2)

    listener.destroy_node()

    assert "order-1" in received
