from app.chatbot import QuickBiteChatbot


 #Run the QuickBite chatbot CLI.
def main() -> None:
   

    chatbot = QuickBiteChatbot()

    user_id = "cli_user"

    print(
        "QuickBite Bot: Welcome to QuickBite! "
        "Type 'exit' to end the conversation."
    )

    while True:
        message = input("You: ").strip()

        if message.lower() in {"exit", "quit"}:
            print("QuickBite Bot: Goodbye!")
            break

        response = chatbot.process_message(
            user_id=user_id,
            message=message,
        )

        print(f"QuickBite Bot: {response}")


if __name__ == "__main__":
    main()