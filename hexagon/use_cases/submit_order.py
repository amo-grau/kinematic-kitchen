from hexagon.driven_ports.for_generating_ids import forGeneratingIds
from hexagon.driven_ports.for_persisting_orders import forPersistingOrders
from hexagon.driving_ports.for_submitting_orders import forSubmittingOrders
from hexagon.order import Order


class SubmitOrderUseCase(forSubmittingOrders):
    def __init__(
        self,
        repository: forPersistingOrders,
        id_generator: forGeneratingIds,
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator

    def submit_order(self, items: list[str]) -> None:
        order = Order(self._id_generator.generate(), items)
        self._repository.save(order)
