from app.backend.mock_backend import MockBackend
from app.core.dispatcher import Dispatcher
from app.core.input_parser import InputParser
from app.core.response_generator import ResponseGenerator
from app.core.state_manager import StateManager
from app.handlers.cancel import CancelHandler
from app.handlers.fallback import FallbackHandler
from app.handlers.order import OrderHandler
from app.handlers.track import TrackHandler
from app.models.schemas import Route
from app.nlp.rule_based import RuleBasedNLP
from app.nlp.llm_classifier import LLMClassifier,LLMClassifierError
from app.models.schemas import ConversationStep, Route


class QuickBiteChatbot:
   
    def __init__(self) -> None:
        self.backend = MockBackend() 
        self.state_manager = StateManager()

        self.input_parser = InputParser()
        self.nlp = RuleBasedNLP(self.backend.get_menu())
        self.dispatcher = Dispatcher()
        self.response_generator = ResponseGenerator()

        self.llm_classifier = LLMClassifier()
        self.rule_confidence_threshold = 0.80

        self.order_handler = OrderHandler(
            state_manager=self.state_manager,
            backend=self.backend,
        )

        self.track_handler = TrackHandler(
            state_manager=self.state_manager,
            backend=self.backend,
        )

        self.cancel_handler = CancelHandler(
            state_manager=self.state_manager,
            backend=self.backend,
        )

        self.fallback_handler = FallbackHandler()


    #Process one user message through the chatbot pipeline.
    def process_message(
        self,
        user_id: str,
        message: str,
    ) -> str:
        """Process one user message through the chatbot pipeline."""

        parsed_message = self.input_parser.parse(message)

        state = self.state_manager.get_state(user_id)

        # First try deterministic NLP.
        nlp_result = self.nlp.classify(parsed_message)

        # LLM is useful for new requests and semantic dish selection,
        # but not for structured multi-turn fields such as quantity,
        # address, confirmation, or order ID.
        llm_allowed = state.step in {
            ConversationStep.START,
            ConversationStep.AWAITING_DISH,
        }

        if (
            llm_allowed
            and nlp_result.confidence < self.rule_confidence_threshold
        ):
            try:

                nlp_result = self.llm_classifier.classify(
                    parsed_message
                )

            except LLMClassifierError:

                # Keep the original rule-based NLP result.
                pass

        route = self.dispatcher.dispatch(
            nlp_result,
            state,
        )

        if route == Route.ORDER:
            handler_result = self.order_handler.handle(
                user_id=user_id,
                message=parsed_message,
                result=nlp_result,
            )

        elif route == Route.TRACK:
            handler_result = self.track_handler.handle(
                user_id=user_id,
                result=nlp_result,
            )

        elif route == Route.CANCEL:
            handler_result = self.cancel_handler.handle(
                user_id=user_id,
                result=nlp_result,
            )

        else:
            handler_result = self.fallback_handler.handle(
                route
            )

        return self.response_generator.generate(
            handler_result
        )