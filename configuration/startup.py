from driven_adapters.forGeneratingIds.for_generating_ids_with_uuid import (
    forGeneratingIdsWithUuid,
)
from driven_adapters.forPersistingOrders.for_persisting_orders_with_memory import (
    forPersistingOrdersWithMemory,
)
from driving_adapters.forSubmittingOrders.cli import CliAdapter
from hexagon.use_cases.submit_order import SubmitOrderUseCase


def run(args: list[str]) -> None:
    id_generator = forGeneratingIdsWithUuid()
    repository = forPersistingOrdersWithMemory()
    use_case = SubmitOrderUseCase(repository, id_generator)
    cli = CliAdapter(use_case, get_last_id=lambda: id_generator.last_id)
    cli.run(args)
