from app.models.schemas import (
    ConversationState,
    ConversationStep,
    Intent,
    NLPResult,
    Route,
)


#Route NLP results to the appropriate application flow.
class Dispatcher:

    #Determine which application flow should handle the message.
    def dispatch(self,result: NLPResult,state: ConversationState, ) -> Route:
        

        # A new explicit intent takes priority.
        if result.intent == Intent.ORDER_FOOD:
            return Route.ORDER

        if result.intent == Intent.TRACK_ORDER:
            return Route.TRACK

        if result.intent == Intent.CANCEL_ORDER:
            return Route.CANCEL

        if result.intent == Intent.HELP:
            return Route.HELP

        if result.intent == Intent.GREETING:
            return Route.GREETING

        # Continue an existing order conversation.
        if (
            state.intent == Intent.ORDER_FOOD
            and state.step
            in {
                ConversationStep.AWAITING_DISH,
                ConversationStep.AWAITING_QUANTITY,
                ConversationStep.AWAITING_ADDRESS,
                ConversationStep.AWAITING_CONFIRMATION,
            }
        ):
            return Route.ORDER

        # Continue an existing tracking conversation.
        if (
            state.intent == Intent.TRACK_ORDER
            and state.step == ConversationStep.AWAITING_ORDER_ID
        ):
            return Route.TRACK

        # Continue an existing cancellation conversation.
        if state.intent == Intent.CANCEL_ORDER and state.step in {
            ConversationStep.AWAITING_ORDER_ID,
            ConversationStep.AWAITING_CANCELLATION_CONFIRMATION,
        }:
            return Route.CANCEL

        return Route.FALLBACK