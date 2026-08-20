from app.handlers.fallback import FallbackHandler
from app.models.schemas import Route


def test_greeting_response() -> None:
    handler = FallbackHandler()

    response = handler.handle(Route.GREETING)

    assert response.completed is True
    assert "QuickBite" in response.message


def test_help_response() -> None:
    handler = FallbackHandler()

    response = handler.handle(Route.HELP)

    assert response.completed is True
    assert "order food" in response.message.lower()
    assert "track" in response.message.lower()
    assert "cancel" in response.message.lower()


def test_fallback_response() -> None:
    handler = FallbackHandler()

    response = handler.handle(Route.FALLBACK)

    assert response.completed is True
    assert "didn't understand" in response.message.lower()