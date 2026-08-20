from app.core.state_manager import StateManager
from app.models.schemas import (
    ConversationStep,
    Entities,
    Intent,
)


def test_new_user_gets_initial_state() -> None:
    manager = StateManager()

    state = manager.get_state("user_001")

    assert state.user_id == "user_001"
    assert state.intent == Intent.UNKNOWN
    assert state.step == ConversationStep.START


def test_update_intent() -> None:
    manager = StateManager()

    state = manager.update_intent(
        "user_001",
        Intent.ORDER_FOOD,
    )

    assert state.intent == Intent.ORDER_FOOD


def test_update_entities() -> None:
    manager = StateManager()

    manager.update_entities(
        "user_001",
        Entities(
            dish="Pepperoni Pizza",
            quantity=2,
        ),
    )

    state = manager.get_state("user_001")

    assert state.entities.dish == "Pepperoni Pizza"
    assert state.entities.quantity == 2


def test_state_is_separate_per_user() -> None:
    manager = StateManager()

    manager.update_intent(
        "user_001",
        Intent.ORDER_FOOD,
    )

    manager.update_intent(
        "user_002",
        Intent.TRACK_ORDER,
    )

    state_1 = manager.get_state("user_001")
    state_2 = manager.get_state("user_002")

    assert state_1.intent == Intent.ORDER_FOOD
    assert state_2.intent == Intent.TRACK_ORDER