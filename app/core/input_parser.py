#Normalize raw user input before NLP processing.
class InputParser:
    

    @staticmethod
    def parse(message: str) -> str:
        """Clean and normalize a raw user message."""
        return " ".join(message.strip().split())