from app.models.schemas import HandlerResult

#Convert handler results into user-facing responses.
class ResponseGenerator:
    

    @staticmethod
    def generate(result: HandlerResult) -> str:
        
        return result.message