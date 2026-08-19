from app.backend.mock_backend import MockBackend


def test_create_order() -> None:
    backend = MockBackend()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    assert order["order_id"].startswith("QB-")
    assert order["dish"] == "Pepperoni Pizza"
    assert order["quantity"] == 2
    assert order["status"] == "preparing"


def test_get_order() -> None:
    backend = MockBackend()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    result = backend.get_order(order["order_id"])

    assert result is not None
    assert result["order_id"] == order["order_id"]


def test_cancel_order() -> None:
    backend = MockBackend()

    order = backend.create_order(
        dish="Pepperoni Pizza",
        quantity=2,
        address="123 Main Street",
    )

    result = backend.cancel_order(order["order_id"])

    assert result is True
    assert backend.get_order(order["order_id"])["status"] == "cancelled"