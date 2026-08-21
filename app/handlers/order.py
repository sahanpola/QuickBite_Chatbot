from app.backend.mock_backend import MockBackend
from app.core.state_manager import StateManager
from app.models.schemas import (ConversationStep,HandlerResult,Intent,NLPResult,)

# Handle the multi-turn food ordering flow.
class OrderHandler:

    def __init__(self,state_manager: StateManager,backend: MockBackend,) -> None:
        self.state_manager = state_manager
        self.backend = backend

    def handle( self,user_id: str, message: str, result: NLPResult,) -> HandlerResult:

        state = self.state_manager.get_state(user_id)

        state.intent = Intent.ORDER_FOOD

        # When waiting for an address, the raw message should be
        # interpreted as the address rather than generic NLP entities.
        if state.step == ConversationStep.AWAITING_ADDRESS:
            address = message.strip()

            if address:
                state.entities.address = address

        else:
            self.state_manager.update_entities(
                user_id,
                result.entities,
            )

        state = self.state_manager.get_state(user_id)

        # Validate quantity before continuing the flow.
        if (
            state.entities.quantity is not None
            and state.entities.quantity <= 0
        ):
            state.entities.quantity = None
            state.step = ConversationStep.AWAITING_QUANTITY

            return HandlerResult(
                message=(
                    "Quantity must be greater than zero. "
                    "How many would you like?"
                )
            )

        if (
                    state.entities.dish is None
                    and state.entities.requested_dish is not None
                ):
                    invalid_dish = state.entities.requested_dish
        
                    state.entities.requested_dish = None
                    state.step = ConversationStep.AWAITING_DISH
        
                    menu_items = ", ".join(
                        self.backend.get_menu().keys()
                    )
        
                    return HandlerResult(
                        message=(
                            f'Sorry, I couldn\'t find "{invalid_dish}" '
                            f"on our menu. Here are today's options: "
                            f"{menu_items}. Which would you like?"
                        )
                )

        # 1. Dish
        if state.entities.dish is None:
            state.step = ConversationStep.AWAITING_DISH

            if state.entities.category == "Pizza":
                return HandlerResult(
                    message=(
                        "Which pizza would you like? "
                        "Margherita Pizza, Pepperoni Pizza, "
                        "or Veggie Supreme Pizza?"
                    )
            )

            if state.entities.category == "Burger":
                return HandlerResult(
                    message=(
                        "Which burger would you like? "
                        "Classic Cheeseburger or BBQ Bacon Burger?"
                    )
                )



            return HandlerResult(
                message="Which dish would you like?",
            )
        
       

        # 2. Quantity
        if state.entities.quantity is None:
            state.step = ConversationStep.AWAITING_QUANTITY

            return HandlerResult(
                message=(
                    f"How many {state.entities.dish} "
                    "would you like?"
                ),
            )

        # 3. Address
        if state.entities.address is None:
            state.step = ConversationStep.AWAITING_ADDRESS

            return HandlerResult(
                message="What is your delivery address?",
            )

        # 4. Confirmation
        if state.entities.confirmation is None:
            state.step = ConversationStep.AWAITING_CONFIRMATION

            unit_price = self.backend.get_menu()[
                state.entities.dish
            ]

            total = unit_price * state.entities.quantity

            return HandlerResult(
                message=(
                    f"Please confirm your order: "
                    f"{state.entities.quantity} x "
                    f"{state.entities.dish} to "
                    f"{state.entities.address}. "
                    f"Total: £{total:.2f}. "
                    "Confirm?"
                ),
            )

        # 5. User rejected confirmation.
        if state.entities.confirmation is False:
            self.state_manager.clear_state(user_id)

            return HandlerResult(
                message="Order cancelled.",
                completed=True,
            )

        # 6. Confirmed — create the order.
        order = self.backend.create_order(
            dish=state.entities.dish,
            quantity=state.entities.quantity,
            address=state.entities.address,
        )

        state.step = ConversationStep.COMPLETED

        response = HandlerResult(
            message=(
                f"Order placed successfully! "
                f"Your order ID is {order['order_id']}."
            ),
            completed=True,
        )

        self.state_manager.clear_state(user_id)

        return response