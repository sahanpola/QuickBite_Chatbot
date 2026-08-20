import re

from app.models.schemas import Entities, Intent, NLPResult

# Rule-based intent classification and entity extraction.
class RuleBasedNLP:
   

    ORDER_PATTERNS = (
        r"\b(order|buy|get|want)\b",
        r"\b(i'd like|i would like)\b",
    )


    TRACK_PATTERNS = (
        r"\btrack\b",
        r"\bwhere\s+(?:is|are)\b",
        r"\border\s+status\b",
        r"\bstatus\s+of\b",
        r"\bwhen\s+will\b",
    )

    CANCEL_PATTERNS = (
        r"\bcancel\b",
        r"\bcancellation\b",
    )

    HELP_PATTERNS = (
        r"\bhelp\b",
        r"\bwhat\s+can\s+you\s+do\b",
        r"\bhow\s+can\s+you\s+help\b",
    )

    GREETING_PATTERNS = (
        r"^\s*(hi|hello|hey)\s*[!.]?\s*$",
        r"^\s*good\s+(morning|afternoon|evening)\s*[!.]?\s*$",
    )

    ORDER_ID_PATTERN = re.compile(r"\bQB-\d{4}\b", re.IGNORECASE)
    QUANTITY_PATTERN = re.compile(r"\b(\d+)\b")

    CATEGORY_MAP = {
        "pizza": "Pizza",
        "burger": "Burger",
        "salad": "Salad",
        "wrap": "Wrap",
        "dessert": "Dessert",
        "cake": "Dessert",
        }

    DISH_ALIASES = {
    "margherita": "Margherita Pizza",
    "pepperoni": "Pepperoni Pizza",
    "veggie": "Veggie Supreme Pizza",
    "veggie supreme": "Veggie Supreme Pizza",

    "cheese": "Classic Cheeseburger",
    "cheeseburger": "Classic Cheeseburger",
    "classic": "Classic Cheeseburger",

    "bbq": "BBQ Bacon Burger",
    "bacon": "BBQ Bacon Burger",
    "bbq bacon": "BBQ Bacon Burger",

    "caesar": "Caesar Salad",

    "chicken wrap": "Grilled Chicken Wrap",
    "grilled chicken": "Grilled Chicken Wrap",

    "lava cake": "Chocolate Lava Cake",
    "chocolate": "Chocolate Lava Cake",
}

    def __init__(self, menu: dict[str, float]) -> None:
        self.menu = menu

    
    #Classify intent and extract entities from a message.
    def classify(self, message: str) -> NLPResult:
        

        normalized = message.strip().lower()

        if not normalized:
            return NLPResult(
                intent=Intent.UNKNOWN,
                entities=Entities(),
                confidence=0.0,
            )

        intent = self._classify_intent(normalized)
        entities = self._extract_entities(message)

        confidence = self._calculate_confidence(
            intent=intent,
            entities=entities,
        )

        return NLPResult(
            intent=intent,
            entities=entities,
            confidence=confidence,
        )

    #Determine the most likely intent using ordered rules.
    
    def _classify_intent(self, message: str) -> Intent:
        
        if self._matches_any(message, self.CANCEL_PATTERNS):
            return Intent.CANCEL_ORDER

        if self._matches_any(message, self.TRACK_PATTERNS):
            return Intent.TRACK_ORDER

        if self._matches_any(message, self.ORDER_PATTERNS):
            return Intent.ORDER_FOOD

        if self._match_dish(message) or self._match_category(message):
            return Intent.ORDER_FOOD

        if self._matches_any(message, self.HELP_PATTERNS):
            return Intent.HELP

        if self._matches_any(message, self.GREETING_PATTERNS):
            return Intent.GREETING

        return Intent.UNKNOWN

    #Extract supported entities from a message.
    def _extract_entities(self, message: str) -> Entities:
        

        entities = Entities()

        order_id_match = self.ORDER_ID_PATTERN.search(message)
        if order_id_match:
            entities.order_id = order_id_match.group(0).upper()

        quantity_match = self.QUANTITY_PATTERN.search(message)
        if quantity_match:
            entities.quantity = int(quantity_match.group(1))

        entities.dish = self._match_dish(message)
        entities.category = self._match_category(message)

        confirmation = self._extract_confirmation(message)
        if confirmation is not None:
            entities.confirmation = confirmation

        return entities

    # Match a known menu item using normalized names.
    def _match_dish(self, message: str) -> str | None:

        normalized = message.lower()

        #  Prefer full menu-item matches.
        for dish in self.menu:
            if dish.lower() in normalized:
                return dish

         # Known natural aliases.
        for alias, dish in self.DISH_ALIASES.items():
            if re.search(
                rf"\b{re.escape(alias)}\b",
                normalized,
            ):
                return dish
        return None
        # Match distinctive words from menu items.
        generic_words = {
            "pizza",
            "burger",
            "salad",
            "wrap",
            "cake",
        }

        for dish in self.menu:
            dish_words = dish.lower().split()

            specific_words = [
                word
                for word in dish_words
                if len(word) > 3 and word not in generic_words
            ]

            if any(word in normalized for word in specific_words):
                return dish

        return None

    #Extract explicit confirmation responses.
    def _extract_confirmation(self, message: str) -> bool | None:
        

        normalized = message.strip().lower()

        positive = {
            "confirm",
            "confirmed",
            "yes",
            "y",
            "okay",
            "ok",
            "sure",
        }

        negative = {
            "no",
            "n",
            "nope",
        }

        if normalized in positive:
            return True

        if normalized in negative:
            return False

        return None

    @staticmethod
    def _matches_any(
        message: str,
        patterns: tuple[str, ...],
    ) -> bool:
        return any(
            re.search(pattern, message)
            for pattern in patterns
        )


    #Assign an explainable rule-based confidence score.
    @staticmethod
    def _calculate_confidence(
        intent: Intent,
        entities: Entities,
    ) -> float:

        if intent == Intent.UNKNOWN:
            return 0.0

        if intent == Intent.ORDER_FOOD:
            if entities.dish and entities.quantity:
                return 0.95

            if entities.dish or entities.quantity:
                return 0.90

            return 0.80

        if intent in {
            Intent.TRACK_ORDER,
            Intent.CANCEL_ORDER,
        }:
            if entities.order_id:
                return 0.95

            return 0.90

        if intent in {
            Intent.HELP,
            Intent.GREETING,
        }:
            return 0.95

        return 0.50

    def _match_category(self, message: str) -> str | None:
        normalized = message.lower()
                    
        for keyword, category in self.CATEGORY_MAP.items():
            if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                return category
        
        return None