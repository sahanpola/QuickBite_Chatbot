from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.models.schemas import (
    ConversationStep,
    HandlerResult,
    Intent,
    NLPResult,
)

 # Handle the multi-turn order tracking flow.
class TrackHandler:
    
    def __init__(self, state_manager: StateManager, backend: MockBackend, ) -> None:
        self.state_manager = state_manager
        self.backend = backend

    def handle(self, user_id: str, result: NLPResult,) -> HandlerResult:

        state = self.state_manager.get_state(user_id)
        state.intent = Intent.TRACK_ORDER

        self.state_manager.update_entities(
            user_id,
            result.entities,
        )

        state = self.state_manager.get_state(user_id)

        if state.entities.order_id is None:
            state.step = ConversationStep.AWAITING_ORDER_ID

            return HandlerResult(
                message="What is your order ID?"
            )

        order = self.backend.get_order(
            state.entities.order_id
        )

        if order is None:
            invalid_order_id = state.entities.order_id

            # Keep the user in the tracking flow so they
            # can provide another order ID.
            state.entities.order_id = None
            state.step = ConversationStep.AWAITING_ORDER_ID

            return HandlerResult(
                message=(
                    f"I couldn't find an order with ID "
                    f"{invalid_order_id}. "
                    "Please check the order ID and try again."
                )
            )

        order_id = order["order_id"]
        status = order["status"]

        response = HandlerResult(
            message=(
                f"Your order {order_id} is currently "
                f"{status}."
            ),
            completed=True,
        )

        self.state_manager.clear_state(user_id)

        return response