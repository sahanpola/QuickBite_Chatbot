from app.chatbot import QuickBiteChatbot
from unittest.mock import MagicMock

from app.models.schemas import Entities, Intent, NLPResult
from app.nlp.llm_classifier import LLMClassifierError


def test_complete_order_flow() -> None:
    chatbot = QuickBiteChatbot()
    user_id = "user_001"

    response = chatbot.process_message(
        user_id,
        "I want Pepperoni Pizza",
    )
    assert "How many" in response

    response = chatbot.process_message(
        user_id,
        "2",
    )
    assert "delivery address" in response

    response = chatbot.process_message(
        user_id,
        "123 Main Street",
    )
    assert "confirm" in response.lower()

    response = chatbot.process_message(
        user_id,
        "confirm",
    )
    assert "QB-1001" in response


def test_complete_track_flow() -> None:
    chatbot = QuickBiteChatbot()

    order = chatbot.backend.create_order(
        dish="Pepperoni Pizza",
        quantity=1,
        address="123 Main Street",
    )

    response = chatbot.process_message(
        "user_001",
        f"Track {order['order_id']}",
    )

    assert order["order_id"] in response
    assert "preparing" in response


def test_fallback_flow() -> None:
    chatbot = QuickBiteChatbot()

    response = chatbot.process_message(
        "user_001",
        "What is the weather today?",
    )

    assert "didn't understand" in response.lower()

def test_quantity_during_active_order_does_not_require_llm() -> None:
    chatbot = QuickBiteChatbot()
    user_id = "user_001"

    chatbot.process_message(
        user_id,
        "I want BBQ Bacon Burger",
    )

    response = chatbot.process_message(
        user_id,
        "67",
    )

    assert "delivery address" in response.lower()

    state = chatbot.state_manager.get_state(user_id)

    assert state.entities.quantity == 67

def test_low_confidence_new_request_uses_llm() -> None:
    chatbot = QuickBiteChatbot()

    chatbot.nlp.classify = MagicMock(
        return_value=NLPResult(
            intent=Intent.UNKNOWN,
            entities=Entities(),
            confidence=0.2,
        )
    )

    chatbot.llm_classifier.classify = MagicMock(
        return_value=NLPResult(
            intent=Intent.ORDER_FOOD,
            entities=Entities(
                dish="BBQ Bacon Burger",
            ),
            confidence=1.0,
        )
    )

    response = chatbot.process_message(
        "user_001",
        "Something smoky and filling, please.",
    )

    chatbot.nlp.classify.assert_called_once()
    chatbot.llm_classifier.classify.assert_called_once()

    assert "How many" in response
    assert "BBQ Bacon Burger" in response

def test_active_order_quantity_does_not_use_llm() -> None:
    chatbot = QuickBiteChatbot()

    chatbot.process_message(
        "user_001",
        "I want BBQ Bacon Burger",
    )

    chatbot.llm_classifier.classify = MagicMock()

    response = chatbot.process_message(
        "user_001",
        "67",
    )

    chatbot.llm_classifier.classify.assert_not_called()

    state = chatbot.state_manager.get_state(
        "user_001"
    )

    assert state.entities.quantity == 67
    assert "delivery address" in response.lower()

def test_active_order_address_does_not_use_llm() -> None:
    chatbot = QuickBiteChatbot()
    user_id = "user_001"

    chatbot.process_message(
        user_id,
        "I want Pepperoni Pizza",
    )

    chatbot.process_message(
        user_id,
        "2",
    )

    chatbot.llm_classifier.classify = MagicMock()

    response = chatbot.process_message(
        user_id,
        "67 Colombo Road",
    )

    chatbot.llm_classifier.classify.assert_not_called()

    state = chatbot.state_manager.get_state(
        user_id
    )

    assert state.entities.quantity == 2
    assert state.entities.address == "67 Colombo Road"
    assert "confirm" in response.lower()

def test_active_order_confirmation_does_not_use_llm() -> None:
    chatbot = QuickBiteChatbot()
    user_id = "user_001"

    chatbot.process_message(
        user_id,
        "I want Pepperoni Pizza",
    )

    chatbot.process_message(
        user_id,
        "2",
    )

    chatbot.process_message(
        user_id,
        "123 Main Street",
    )

    chatbot.llm_classifier.classify = MagicMock()

    response = chatbot.process_message(
        user_id,
        "yes",
    )

    chatbot.llm_classifier.classify.assert_not_called()

    assert "Order placed successfully" in response


def test_high_confidence_rule_request_skips_llm() -> None:
    chatbot = QuickBiteChatbot()

    chatbot.llm_classifier.classify = MagicMock()

    response = chatbot.process_message(
        "user_001",
        "I want Pepperoni Pizza",
    )

    chatbot.llm_classifier.classify.assert_not_called()

    assert "How many" in response


def test_llm_failure_falls_back_gracefully() -> None:
    chatbot = QuickBiteChatbot()

    chatbot.nlp.classify = MagicMock(
        return_value=NLPResult(
            intent=Intent.UNKNOWN,
            entities=Entities(),
            confidence=0.1,
        )
    )

    chatbot.llm_classifier.classify = MagicMock(
        side_effect=LLMClassifierError(
            "Ollama unavailable"
        )
    )

    response = chatbot.process_message(
        "user_001",
        "Something completely ambiguous",
    )

    chatbot.llm_classifier.classify.assert_called_once()

    assert "didn't understand" in response.lower()