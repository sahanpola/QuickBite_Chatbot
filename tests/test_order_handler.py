from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.handlers.order import OrderHandler
from app.models.schemas import (
    ConversationStep,
    Entities,
    Intent,
    NLPResult,
)


def create_handler() -> tuple[
    OrderHandler,
    StateManager,
    MockBackend,
]:
    state_manager = StateManager()
    backend = MockBackend()

    handler = OrderHandler(
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


def test_order_flow_asks_for_missing_quantity() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        user_id="user_001",
        message="I want Pepperoni Pizza",
        result=make_result(
            Entities(dish="Pepperoni Pizza"),
            Intent.ORDER_FOOD,
        ),
    )

    state = state_manager.get_state("user_001")

    assert state.step == ConversationStep.AWAITING_QUANTITY
    assert "How many" in response.message
    assert response.completed is False


def test_order_flow_collects_address() -> None:
    handler, state_manager, _ = create_handler()

    handler.handle(
        "user_001",
        "I want 2 Pepperoni Pizza",
        make_result(
            Entities(
                dish="Pepperoni Pizza",
                quantity=2,
            ),
            Intent.ORDER_FOOD,
        ),
    )

    response = handler.handle(
        "user_001",
        "123 Main Street",
        make_result(Entities()),
    )

    state = state_manager.get_state("user_001")

    assert state.entities.address == "123 Main Street"
    assert state.entities.quantity == 2
    assert state.step == ConversationStep.AWAITING_CONFIRMATION
    assert "confirm" in response.message.lower()


def test_confirmed_order_is_created() -> None:
    handler, state_manager, backend = create_handler()

    # Initial order request.
    handler.handle(
        "user_001",
        "I want 2 Pepperoni Pizza",
        make_result(
            Entities(
                dish="Pepperoni Pizza",
                quantity=2,
            ),
            Intent.ORDER_FOOD,
        ),
    )

    # Address.
    handler.handle(
        "user_001",
        "123 Main Street",
        make_result(Entities()),
    )

    # Confirmation.
    response = handler.handle(
        "user_001",
        "confirm",
        make_result(
            Entities(confirmation=True),
        ),
    )

    assert response.completed is True
    assert "QB-1001" in response.message

    order = backend.get_order("QB-1001")

    assert order is not None
    assert order["dish"] == "Pepperoni Pizza"
    assert order["quantity"] == 2
    assert order["address"] == "123 Main Street"

    # Temporary conversation state should be cleared.
    state = state_manager.get_state("user_001")

    assert state.step == ConversationStep.START
    assert state.intent == Intent.UNKNOWN


def test_invalid_quantity_is_rejected() -> None:
    handler, state_manager, _ = create_handler()

    response = handler.handle(
        "user_001",
        "I want 0 Pepperoni Pizza",
        make_result(
            Entities(
                dish="Pepperoni Pizza",
                quantity=0,
            ),
            Intent.ORDER_FOOD,
        ),
    )

    state = state_manager.get_state("user_001")

    assert state.entities.quantity is None
    assert state.step == ConversationStep.AWAITING_QUANTITY
    assert "greater than zero" in response.message.lower()
    assert response.completed is False