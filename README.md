# QuickBite Chatbot

QuickBite is a conversational food ordering chatbot that allows customers to place, track, and cancel orders through natural conversations.

It uses a **hybrid NLP approach**, combining rule based intent/entity extraction with an **LLM fallback** for more ambiguous requests. Conversation state is maintained to support smooth multi turn ordering.

## Features

- Food ordering with multi-turn conversation
- Order tracking
- Order cancellation with confirmation
- Menu/category matching
- Graceful fallback handling
- Per user conversation state
- Hybrid NLP:
  - Rule based intent/entity extraction
  - LLM fallback for low-confidence requests
- Local Ollama support
- Mock backend for menu and orders
- Automated tests

## Architecture

User
→ Input Parser
→ Rule Based NLP
→ LLM fallback for low confidence requests
→ Dispatcher
→ State Manager
→ Handler
→ Mock Backend
→ Response Generator
→ User

## NLP Strategy

QuickBite uses a hybrid NLP approach.

High confidence and predictable requests are handled using deterministic rules and regex based entity extraction.

Examples:

- `Track QB-1001`
- `I want Pepperoni Pizza`
- `Cancel QB-1001`

Low confidence or more natural requests can fall back to a local LLM through Ollama.

The LLM is only responsible for intent and entity extraction. Business logic, state transitions, order creation, tracking, and cancellation remain deterministic.

## Supported Intents

- `order_food`
- `track_order`
- `cancel_order`
- `help`
- `greeting`
- `unknown`

## Extracted Entities

- dish
- category
- quantity
- address
- order_id
- confirmation

## Requirements

- Python 3.11+
- Ollama 

## Setup

Create a virtual environment:

```bash
python -m venv .venv

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## LLM Setup

QuickBite uses a local Ollama model as the LLM component of the hybrid NLP pipeline.

Download the model:

```bash
ollama pull qwen2.5:3b
```

Start Ollama:

```bash
ollama serve
```

If Ollama is unavailable, the chatbot continues using the rule-based NLP path and deterministic fallback behaviour.

## Running the Chatbot

From the project root, run:

```bash
python -m app.main
```

The command-line interface simulates a WhatsApp-style conversation.

Example:

```text
QuickBite Bot: Welcome to QuickBite! Type 'exit' to end the conversation.

You: I want pizza
QuickBite Bot: Which pizza would you like? Margherita Pizza, Pepperoni Pizza, or Veggie Supreme Pizza?

You: Pepperoni
QuickBite Bot: How many Pepperoni Pizza would you like?

You: 2
QuickBite Bot: What is your delivery address?

You: 123 Main Street
QuickBite Bot: Please confirm your order: 2 x Pepperoni Pizza to 123 Main Street. Total: £20.98. Confirm?

You: yes
QuickBite Bot: Order placed successfully! Your order ID is QB-1001.
```

Type `exit` to stop the chatbot.

## Error Recovery

QuickBite handles invalid menu requests without terminating the conversation.

Example:

```text
You: I want a unicorn burger
QuickBite Bot: Sorry, I couldn't find "unicorn burger" on our menu. Here are today's options: Margherita Pizza, Pepperoni Pizza, Veggie Supreme Pizza, Classic Cheeseburger, BBQ Bacon Burger, Caesar Salad, Grilled Chicken Wrap, Chocolate Lava Cake. Which would you like?

You: BBQ
QuickBite Bot: How many BBQ Bacon Burger would you like?
```

The chatbot keeps the current conversation state and allows the customer to correct the request.

## LLM-Assisted Understanding

The LLM is used when rule-based NLP has low confidence and when semantic understanding can improve dish selection.

For example:

```text
You: Something smoky and filling, please
QuickBite Bot: How many BBQ Bacon Burger would you like?
```

In this case, the rule-based classifier does not confidently identify a menu item, so the request is passed to the local LLM. The LLM maps the description to the closest appropriate menu item.

The LLM does not perform pricing, create orders, cancel orders, or modify application state. These operations remain deterministic.

## Testing

Run the complete test suite with:

```bash
python -m pytest -v
```

The project currently contains 53 automated tests covering:

- Rule-based intent and entity extraction
- Conversation state management
- Dispatcher routing
- Order flow
- Order tracking
- Order cancellation
- Mock backend operations
- Invalid quantity handling
- Invalid dish recovery
- LLM fallback routing
- Graceful LLM failure handling
- End-to-end chatbot behaviour

## Project Structure

```text
QuickBite_Chatbot/
├── app/
│   ├── backend/
│   ├── core/
│   ├── handlers/
│   ├── models/
│   ├── nlp/
│   ├── chatbot.py
│   └── main.py
├── tests/
├── docs/
├── README.md
└── requirements.txt
```

