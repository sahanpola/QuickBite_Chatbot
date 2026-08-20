from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.models.schemas import (
    ConversationStep,
    HandlerResult,
    Intent,
    NLPResult,
)


class CancelHandler:
    

    def __init__(
        self,
        state_manager: StateManager,
        backend: MockBackend,
    ) -> None:
        self.state_manager = state_manager
        self.backend = backend

    def handle(
        self,
        user_id: str,
        result: NLPResult,
    ) -> HandlerResult:
       

        state = self.state_manager.get_state(user_id)
        state.intent = Intent.CANCEL_ORDER

        self.state_manager.update_entities(
            user_id,
            result.entities,
        )

        state = self.state_manager.get_state(user_id)

        # 1. Ask for order ID if missing.
        if state.entities.order_id is None:
            state.step = ConversationStep.AWAITING_ORDER_ID

            return HandlerResult(
                message="What is your order ID?"
            )

        # 2. Validate that the order exists.
        order = self.backend.get_order(
            state.entities.order_id
        )

        if order is None:
            invalid_order_id = state.entities.order_id

            state.entities.order_id = None
            state.step = ConversationStep.AWAITING_ORDER_ID

            return HandlerResult(
                message=(
                    f"I couldn't find an order with ID "
                    f"{invalid_order_id}. "
                    "Please check the order ID and try again."
                )
            )

        # 3. Ask for cancellation confirmation.
        if state.entities.confirmation is None:
            state.step = (
                ConversationStep.AWAITING_CANCELLATION_CONFIRMATION
            )

            return HandlerResult(
                message=(
                    f"Are you sure you want to cancel "
                    f"order {state.entities.order_id}? "
                    "Please confirm yes or no."
                )
            )

        # 4. User decided not to cancel.
        if state.entities.confirmation is False:
            order_id = state.entities.order_id

            self.state_manager.clear_state(user_id)

            return HandlerResult(
                message=(
                    f"Cancellation stopped. "
                    f"Order {order_id} is still active."
                ),
                completed=True,
            )

        # 5. User confirmed cancellation.
        order_id = state.entities.order_id

        success = self.backend.cancel_order(order_id)

        self.state_manager.clear_state(user_id)

        if not success:
            return HandlerResult(
                message=(
                    f"Order {order_id} could not be cancelled."
                ),
                completed=True,
            )

        return HandlerResult(
            message=(
                f"Order {order_id} has been cancelled successfully."
            ),
            completed=True,
        )