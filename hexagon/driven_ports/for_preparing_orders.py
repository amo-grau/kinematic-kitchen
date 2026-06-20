from abc import ABC, abstractmethod

from hexagon.order import Order


class forPreparingOrders(ABC):
    @abstractmethod
    def prepare(self, order: Order) -> None: ...
