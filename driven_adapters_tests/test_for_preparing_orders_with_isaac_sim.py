import pytest

from driven_adapters.forPreparingOrders.for_preparing_orders_with_isaac_sim import (
    forPreparingOrdersWithIsaacSim,
)
from hexagon.driven_ports.for_preparing_orders import forPreparingOrders
from hexagon.order import Order


def test_prepare_does_not_raise() -> None:
    adapter: forPreparingOrders = forPreparingOrdersWithIsaacSim()
    order = Order("order-1", ["burger"])

    adapter.prepare(order)


def test_prepare_outputs_the_order_id(capsys: pytest.CaptureFixture[str]) -> None:
    adapter: forPreparingOrders = forPreparingOrdersWithIsaacSim()
    order = Order("order-1", ["burger"])

    adapter.prepare(order)

    assert "order-1" in capsys.readouterr().out
