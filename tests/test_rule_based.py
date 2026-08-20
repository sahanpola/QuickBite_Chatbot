from app.backend.mock_backend import MockBackend
from app.models.schemas import Intent
from app.nlp.rule_based import RuleBasedNLP


def create_nlp() -> RuleBasedNLP:
    backend = MockBackend()
    return RuleBasedNLP(backend.get_menu())


def test_order_intent_and_entities() -> None:
    nlp = create_nlp()

    result = nlp.classify(
        "I want 2 Pepperoni Pizza"
    )

    assert result.intent == Intent.ORDER_FOOD
    assert result.entities.dish == "Pepperoni Pizza"
    assert result.entities.quantity == 2
    assert result.confidence == 0.95


def test_track_order() -> None:
    nlp = create_nlp()

    result = nlp.classify(
        "Where is my order QB-1001?"
    )

    assert result.intent == Intent.TRACK_ORDER
    assert result.entities.order_id == "QB-1001"


def test_cancel_order() -> None:
    nlp = create_nlp()

    result = nlp.classify(
        "Please cancel order QB-1001"
    )

    assert result.intent == Intent.CANCEL_ORDER
    assert result.entities.order_id == "QB-1001"


def test_greeting() -> None:
    nlp = create_nlp()

    result = nlp.classify("Hi")

    assert result.intent == Intent.GREETING


def test_unknown_message() -> None:
    nlp = create_nlp()

    result = nlp.classify(
        "What is the weather today?"
    )

    assert result.intent == Intent.UNKNOWN
    assert result.confidence == 0.0

def test_generic_pizza_does_not_select_specific_dish() -> None:
    nlp = create_nlp()

    result = nlp.classify("I want a pizza")

    assert result.intent == Intent.ORDER_FOOD
    assert result.entities.dish is None


def test_specific_dish_keyword() -> None:
    nlp = create_nlp()

    result = nlp.classify("I want pepperoni")

    assert result.intent == Intent.ORDER_FOOD
    assert result.entities.dish == "Pepperoni Pizza"


def test_generic_burger_does_not_select_specific_dish() -> None:
    nlp = create_nlp()

    result = nlp.classify("I want a burger")

    assert result.intent == Intent.ORDER_FOOD
    assert result.entities.dish is None


def test_specific_burger_keyword() -> None:
    nlp = create_nlp()

    result = nlp.classify("I want a cheeseburger")

    assert result.intent == Intent.ORDER_FOOD
    assert result.entities.dish == "Classic Cheeseburger"