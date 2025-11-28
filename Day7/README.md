# Day 7: Food & Grocery Ordering Voice Agent 🛒

A voice agent that helps customers order food and groceries from a catalog, intelligently handles recipe-based requests, and manages cart operations.

## Features
- **Catalog Search**: Search for items by name, brand, category, or tags.
- **Smart Recipe Ordering**: Ask for "ingredients for pasta" or "peanut butter sandwich" and get all items added to cart.
- **Cart Management**: Add, remove, update quantities, and view cart contents.
- **Order Persistence**: Orders are saved to JSON files with timestamps and order IDs.

## Quick Start

1.  **Navigate to backend**:
    ```bash
    cd backend
    ```

2.  **Install dependencies** (if not already installed):
    ```bash
    uv sync
    ```

3.  **Run the agent**:
    ```bash
    python src/agent.py dev
    ```

4.  **Connect**:
    - Open the LiveKit Agent Playground (link printed in terminal).
    - Speak to the agent.
    - **Try These Commands**:
        - "I want to order some bread"
        - "Add milk to my cart"
        - "I need ingredients for a peanut butter sandwich"
        - "What's in my cart?"
        - "Place my order" (agent will ask for name and address)

## Documentation
See [backend/AGENTS.md](backend/AGENTS.md) for full details on architecture and configuration.
