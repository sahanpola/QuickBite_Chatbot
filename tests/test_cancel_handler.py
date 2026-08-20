from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.handlers.cancel import CancelHandler
from app.models.schemas import (
    ConversationStep,
    Entities,
    Intent,
    NLPResult,
)


def create_handler() -> tuple[
    CancelHandler,
    StateManager,
    MockBackend,
]:
    state_manager = StateManager()
    backend = MockBackend()

    handler = CancelHandler(
        state_manager=state_manager,
        backend=backend,
    )

    return handler, state_manager, backend


def make_result(
    entities: Entities,
    intent: Intent = Intent.UNKNOWN,
) -> NLPResult:
    return NLPResult(
        intent=intent,
        entities=entities,
    )


def test_cancel_flow_asks_for_missing_order_id() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        "user_001",
        make_result(
            Entities(),
            Intent.CANCEL_ORDER,
        ),
    )

    state = state_manager.get_state("user_001")

    assert state.intent == Intent.CANCEL_ORDER
    assert state.step == ConversationStep.AWAITING_ORDER_ID
    assert "order ID" in response.message
    assert response.completed is False


def test_cancel_flow_asks_for_confirmation() -> None:
    handler, state_manager, backend = create_handler()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    response = handler.handle(
        "user_001",
        make_result(
            Entities(order_id=order["order_id"]),
            Intent.CANCEL_ORDER,
        ),
    )

    state = state_manager.get_state("user_001")

    assert (
        state.step
        == ConversationStep.AWAITING_CANCELLATION_CONFIRMATION
    )

    assert order["order_id"] in response.message
    assert "sure" in response.message.lower()
    assert response.completed is False


def test_confirmed_cancellation_updates_backend() -> None:
    handler, state_manager, backend = create_handler()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    handler.handle(
        "user_001",
        make_result(
            Entities(order_id=order["order_id"]),
            Intent.CANCEL_ORDER,
        ),
    )

    response = handler.handle(
        "user_001",
        make_result(
            Entities(confirmation=True),
        ),
    )

    updated_order = backend.get_order(order["order_id"])

    assert response.completed is True
    assert "cancelled successfully" in response.message
    assert updated_order is not None
    assert updated_order["status"] == "cancelled"

    state = state_manager.get_state("user_001")

    assert state.intent == Intent.UNKNOWN
    assert state.step == ConversationStep.START


def test_rejected_cancellation_keeps_order_active() -> None:
    handler, state_manager, backend = create_handler()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    handler.handle(
        "user_001",
        make_result(
            Entities(order_id=order["order_id"]),
            Intent.CANCEL_ORDER,
        ),
    )

    response = handler.handle(
        "user_001",
        make_result(
            Entities(confirmation=False),
        ),
    )

    stored_order = backend.get_order(order["order_id"])

    assert response.completed is True
    assert stored_order is not None
    assert stored_order["status"] == "preparing"


def test_unknown_order_id_allows_retry() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        "user_001",
        make_result(
            Entities(order_id="QB-9999"),
            Intent.CANCEL_ORDER,
        ),
    )

    state = state_manager.get_state("user_001")

    assert response.completed is False
    assert "couldn't find" in response.message
    assert state.step == ConversationStep.AWAITING_ORDER_ID
    assert state.entities.order_id is None