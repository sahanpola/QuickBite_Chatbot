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