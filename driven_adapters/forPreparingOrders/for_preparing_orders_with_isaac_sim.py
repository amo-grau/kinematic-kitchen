from hexagon.driven_ports.for_preparing_orders import forPreparingOrders
from hexagon.order import Order


class forPreparingOrdersWithIsaacSim(forPreparingOrders):
    def prepare(self, order: Order) -> None:
        print(f"[IsaacSim] Preparing order {order.id}: {order.items}")
