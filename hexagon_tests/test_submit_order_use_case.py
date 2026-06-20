import pytest

from hexagon.driven_ports.for_generating_ids import forGeneratingIds
from hexagon.driven_ports.for_persisting_orders import forPersistingOrders
from hexagon.driving_ports.for_submitting_orders import forSubmittingOrders
from hexagon.order import Order, OrderStatus
from hexagon.use_cases.submit_order import SubmitOrderUseCase


class FakeOrderRepository(forPersistingOrders):
    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    @property
    def saved_orders(self) -> list[Order]:
        return list(self._store.values())


class SequentialIdGenerator(forGeneratingIds):
    def __init__(self) -> None:
        self._counter = 0

    def generate(self) -> str:
        self._counter += 1
        return f"order-{self._counter}"


def make_use_case() -> tuple[forSubmittingOrders, FakeOrderRepository]:
    repository = FakeOrderRepository()
    id_generator = SequentialIdGenerator()
    return SubmitOrderUseCase(repository, id_generator), repository


def test_submit_order_persists_the_order() -> None:
    use_case, repository = make_use_case()

    use_case.submit_order(["burger", "fries"])

    assert len(repository.saved_orders) == 1


def test_submitted_order_has_correct_items() -> None:
    use_case, repository = make_use_case()

    use_case.submit_order(["burger", "fries"])

    assert repository.saved_orders[0].items == ["burger", "fries"]


def test_submitted_order_starts_as_pending() -> None:
    use_case, repository = make_use_case()

    use_case.submit_order(["burger"])

    assert repository.saved_orders[0].status == OrderStatus.PENDING


def test_submitted_order_can_be_retrieved_by_id() -> None:
    use_case, repository = make_use_case()

    use_case.submit_order(["burger"])

    saved = repository.saved_orders[0]
    assert repository.find_by_id(saved.id) is saved


def test_each_submitted_order_gets_a_unique_id() -> None:
    use_case, repository = make_use_case()

    use_case.submit_order(["burger"])
    use_case.submit_order(["fries"])

    ids = [o.id for o in repository.saved_orders]
    assert ids[0] != ids[1]


def test_submit_order_raises_for_empty_items() -> None:
    use_case, _ = make_use_case()

    with pytest.raises(ValueError):
        use_case.submit_order([])
