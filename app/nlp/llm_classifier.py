import json

import ollama

from app.models.schemas import Entities, Intent, NLPResult

class LLMClassifierError(RuntimeError):
    """Raised when the local LLM classifier cannot produce a result."""
    
# Use a local Ollama model for flexible intent and entity extraction.
class LLMClassifier:
   

    def __init__(self, model: str = "qwen2.5:3b", ) -> None:
        self.model = model

    # Classify intent and extract entities using the LLM.
    def classify(self, message: str) -> NLPResult:
        """Classify intent and extract entities using the LLM."""

        prompt = f"""
    You are the NLP classifier for a food delivery chatbot called QuickBite.

    Classify the customer message into exactly one intent:

    - order_food
    - track_order
    - cancel_order
    - help
    - greeting
    - unknown

    Extract these entities when present:

    - dish
    - category
    - quantity
    - address
    - order_id
    - confirmation

    Available menu items:

    - Margherita Pizza
    - Pepperoni Pizza
    - Veggie Supreme Pizza
    - Classic Cheeseburger
    - BBQ Bacon Burger
    - Caesar Salad
    - Grilled Chicken Wrap
    - Chocolate Lava Cake

    Return ONLY valid JSON in this exact structure:

    {{
    "intent": "order_food",
    "entities": {{
        "dish": null,
        "category": null,
        "quantity": null,
        "address": null,
        "order_id": null,
        "confirmation": null
    }}
    }}

    Customer message:
    {message}
    """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                format="json",
            )

            content = response["message"]["content"]
            data = json.loads(content)

        except Exception as exc:
            raise LLMClassifierError(
                "LLM classification failed."
            ) from exc

        intent = self._parse_intent(
            data.get("intent", "unknown")
        )

        entities_data = data.get("entities", {})

        entities = Entities(
            dish=entities_data.get("dish"),
            category=entities_data.get("category"),
            quantity=entities_data.get("quantity"),
            address=entities_data.get("address"),
            order_id=entities_data.get("order_id"),
            confirmation=entities_data.get("confirmation"),
        )

        return NLPResult(
            intent=intent,
            entities=entities,
            confidence=1.0,
        )
    @staticmethod
    def _parse_intent(value: str) -> Intent:
        try:
            return Intent(value)
        except ValueError:
            return Intent.UNKNOWN