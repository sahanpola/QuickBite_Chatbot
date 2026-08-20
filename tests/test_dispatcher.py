from app.core.dispatcher import Dispatcher
from app.models.schemas import (
    ConversationState,
    ConversationStep,
    Entities,
    Intent,
    NLPResult,
    Route,
)


def create_state() -> ConversationState:
    return ConversationState(user_id="user_001")


def test_order_intent_routes_to_order() -> None:
    dispatcher = Dispatcher()
    state = create_state()

    result = NLPResult(
        intent=Intent.ORDER_FOOD,
        entities=Entities(dish="Pepperoni Pizza"),
    )

    assert dispatcher.dispatch(result, state) == Route.ORDER


def test_track_intent_routes_to_track() -> None:
    dispatcher = Dispatcher()
    state = create_state()

    result = NLPResult(
        intent=Intent.TRACK_ORDER,
        entities=Entities(order_id="QB-1001"),
    )

    assert dispatcher.dispatch(result, state) == Route.TRACK


def test_cancel_intent_routes_to_cancel() -> None:
    dispatcher = Dispatcher()
    state = create_state()

    result = NLPResult(
        intent=Intent.CANCEL_ORDER,
        entities=Entities(order_id="QB-1001"),
    )

    assert dispatcher.dispatch(result, state) == Route.CANCEL


def test_active_order_state_continues_order_flow() -> None:
    dispatcher = Dispatcher()

    state = ConversationState(
        user_id="user_001",
        intent=Intent.ORDER_FOOD,
        step=ConversationStep.AWAITING_QUANTITY,
    )

    result = NLPResult(
        intent=Intent.UNKNOWN,
        entities=Entities(quantity=2),
    )

    assert dispatcher.dispatch(result, state) == Route.ORDER


def test_unknown_message_routes_to_fallback() -> None:
    dispatcher = Dispatcher()
    state = create_state()

    result = NLPResult(
        intent=Intent.UNKNOWN,
        entities=Entities(),
    )

    assert dispatcher.dispatch(result, state) == Route.FALLBACK


def test_new_intent_overrides_old_order_flow() -> None:
    dispatcher = Dispatcher()

    state = ConversationState(
        user_id="user_001",
        intent=Intent.ORDER_FOOD,
        step=ConversationStep.AWAITING_ADDRESS,
    )

    result = NLPResult(
        intent=Intent.CANCEL_ORDER,
        entities=Entities(order_id="QB-1001"),
    )

    assert dispatcher.dispatch(result, state) == Route.CANCEL