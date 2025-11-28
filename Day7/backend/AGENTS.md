# AGENTS.md - Day 7: Food & Grocery Ordering Voice Agent

This is a LiveKit Agents project implementing a **Food & Grocery Ordering Voice Agent** for "FreshCart Express". The agent helps customers order food and groceries with intelligent cart management and recipe-based ordering.

## Overview

Day 7's agent focuses on **e-commerce cart management** and **intelligent recipe-based ordering**. It uses a single-agent pattern with function tools to:
- Search for items in a product catalog.
- Add items to a shopping cart with quantity management.
- Understand recipe requests and add multiple ingredients automatically.
- Place orders and persist them to JSON files.

### Key Features

1.  **Friendly Shopping Assistant Persona** - Warm, helpful, and knowledgeable.
2.  **Catalog Management** - JSON-based catalog with 30+ items across 4 categories.
3.  **Cart Operations** - Add, remove, update quantities, and view cart.
4.  **Recipe Intelligence** - Understand requests like "ingredients for pasta" and add all needed items.
5.  **Order Persistence** - Save completed orders to JSON with timestamps and order IDs.

## Project Structure

This Python project uses the `uv` package manager.

### Key Files

```
Day7/backend/
├── src/
│   ├── agent.py              # Main Food Ordering Agent with cart tools
│   └── database.py           # JSON catalog loader and order persistence
├── data/
│   ├── catalog.json          # Product catalog (30+ items)
│   ├── orders.json           # All placed orders (auto-created)
│   └── current_order.json    # Last placed order (auto-created)
└── .env                      # Environment variables
```

## Catalog Structure

The `catalog.json` file contains:

### Categories
- **Groceries**: Bread, milk, eggs, pasta, sauces, etc.
- **Snacks**: Chips, cookies, chocolate, etc.
- **Prepared Food**: Pizzas, sandwiches, biryani, etc.
- **Beverages**: Juices, coffee, tea

### Recipes
Pre-defined recipe mappings:
- "peanut butter sandwich" → Whole Wheat Bread + Peanut Butter
- "pasta" / "pasta for two" → Pasta + Pasta Sauce
- "breakfast" → Bread + Butter + Milk + Eggs

Each item includes:
- `id`, `name`, `category`, `price`, `brand`, `size`, `tags`

## Agent Tools

The agent has 7 function tools:

### 1. `search_items_tool(query)`

**Purpose**: Search for items in the catalog.

**How it works**:
- Searches by name, brand, category, or tags.
- Returns exact match if found, or lists multiple options.
- Example: "bread" → Shows all bread options with details.

### 2. `get_recipe_items_tool(recipe_name)`

**Purpose**: Get all ingredients for a recipe/meal.

**How it works**:
- Looks up recipe in the recipes database.
- Automatically adds all required items to cart.
- Confirms what was added.

**Example**: "ingredients for pasta" → Adds pasta + pasta sauce to cart.

### 3. `add_to_cart_tool(item_id, quantity)`

**Purpose**: Add a specific item to the cart.

**How it works**:
- Takes item ID from search results.
- Adds specified quantity to cart.
- If item already exists, increases quantity.

### 4. `remove_from_cart_tool(item_id)`

**Purpose**: Remove an item from the cart.

### 5. `update_cart_quantity_tool(item_id, quantity)`

**Purpose**: Update quantity of an item in cart.

**Note**: Setting quantity to 0 removes the item.

### 6. `view_cart_tool()`

**Purpose**: Show all items in cart with prices and total.

**Returns**: List of cart items with subtotals and grand total.

### 7. `place_order_tool(customer_name, delivery_address)`

**Purpose**: Place the order and save to JSON.

**How it works**:
- Creates order object with all cart items.
- Calculates total.
- Generates unique order ID.
- Saves to `orders.json` and `current_order.json`.
- Clears the cart.

## Conversation Flow

1.  **Greeting**: Agent introduces FreshCart Express and explains capabilities.
2.  **Shopping**: User requests items or recipes.
    - Agent searches catalog.
    - Agent adds items to cart and confirms.
3.  **Cart Management**: User can view cart, modify quantities, or remove items.
4.  **Checkout**: When user says "place my order", agent:
    - Shows final cart and total.
    - Asks for name and address.
    - Places order and provides order ID.

## Running the Agent

### Development Mode

```bash
cd Day7/backend
python src/agent.py dev
```

## Example Interactions

### Basic Item Order
**User**: "I want some bread"  
**Agent**: *Searches* → "Found: Whole Wheat Bread..." → *Adds to cart*

### Recipe-Based Order
**User**: "I need ingredients for a peanut butter sandwich"  
**Agent**: "I've added Whole Wheat Bread and Peanut Butter to your cart..."

### Cart Operations
**User**: "What's in my cart?"  
**Agent**: "Your cart: Whole Wheat Bread x1 = ₹45, Peanut Butter x1 = ₹180. Total: ₹225"

### Checkout
**User**: "Place my order"  
**Agent**: *Shows cart* → "May I have your name and delivery address?"  
**User**: "John, 123 Main Street"  
**Agent**: "Order placed! Order ID: ORDER_20251128_103045. Total: ₹225..."

## Order JSON Format

Saved orders include:
```json
{
  "order_id": "ORDER_20251128_103045",
  "timestamp": "2025-11-28T10:30:45.123456",
  "customer_name": "John",
  "delivery_address": "123 Main Street",
  "items": [
    {
      "item_id": "grocery_001",
      "name": "Whole Wheat Bread",
      "brand": "Harvest Gold",
      "quantity": 1,
      "unit_price": 45,
      "subtotal": 45
    }
  ],
  "total": 225,
  "status": "placed"
}
```

## Environment Variables

Required in `.env`:
```
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
MURF_API_KEY=
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
```
