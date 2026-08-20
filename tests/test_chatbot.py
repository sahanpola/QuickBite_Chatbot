from app.chatbot import QuickBiteChatbot


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