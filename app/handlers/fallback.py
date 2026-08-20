from app.models.schemas import HandlerResult, Route


class FallbackHandler:
    

    def handle(self, route: Route) -> HandlerResult:
       

        if route == Route.GREETING:
            return HandlerResult(
                message=(
                    "Welcome to QuickBite! "
                    "You can order food, track an order, "
                    "cancel an order, or ask for help."
                ),
                completed=True,
            )

        if route == Route.HELP:
            return HandlerResult(
                message=(
                    "I can help you order food, track an order, "
                    "or cancel an existing order."
                ),
                completed=True,
            )

        return HandlerResult(
            message=(
                "Sorry, I didn't understand that. "
                "You can order food, track an order, "
                "cancel an order, or ask for help."
            ),
            completed=True,
        )