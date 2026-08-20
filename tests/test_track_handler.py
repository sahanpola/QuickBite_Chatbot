from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.handlers.track import TrackHandler
from app.models.schemas import (
    ConversationStep,
    Entities,
    Intent,
    NLPResult,
)


def create_handler() -> tuple[
    TrackHandler,
    StateManager,
    MockBackend,
]:
    state_manager = StateManager()
    backend = MockBackend()

    handler = TrackHandler(
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


def test_track_flow_asks_for_missing_order_id() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        "user_001",
        make_result(
            Entities(),
            Intent.TRACK_ORDER,
        ),
    )

    state = state_manager.get_state("user_001")

    assert state.intent == Intent.TRACK_ORDER
    assert state.step == ConversationStep.AWAITING_ORDER_ID
    assert "order ID" in response.message
    assert response.completed is False


def test_existing_order_returns_status() -> None:
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
            Intent.TRACK_ORDER,
        ),
    )

    assert response.completed is True
    assert order["order_id"] in response.message
    assert "preparing" in response.message

    # Tracking conversation is complete,
    # so temporary state should be cleared.
    state = state_manager.get_state("user_001")

    assert state.intent == Intent.UNKNOWN
    assert state.step == ConversationStep.START


def test_unknown_order_id_allows_retry() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        "user_001",
        make_result(
            Entities(order_id="QB-9999"),
            Intent.TRACK_ORDER,
        ),
    )

    state = state_manager.get_state("user_001")

    assert response.completed is False
    assert "couldn't find" in response.message
    assert state.intent == Intent.TRACK_ORDER
    assert state.step == ConversationStep.AWAITING_ORDER_ID
    assert state.entities.order_id is None