# E-commerce Voice Agent - Backend

A voice-powered shopping assistant built with LiveKit Agents, following the Agentic Commerce Protocol (ACP) pattern.

## Features

### 🛍️ Smart Shopping Experience
- **Voice Catalog Browsing**: Search by category, price, color, or size
- **Intelligent Cart Management**: Add, view, remove, clear cart operations
- **Multi-Item Orders**: Buy multiple products in one transaction
- **Order Persistence**: All orders saved to `orders.json`
- **Order History**: Check your last order anytime

### 🎯 ACP-Inspired Architecture
- **Conversation Layer**: LLM + Voice (STT/TTS)
- **Commerce Logic**: Catalog, cart, and order management
- **Persistence Layer**: JSON-based order storage

## Product Catalog

**9 Products** across **3 Categories**:
- **Clothing**: T-shirts, hoodies, jeans
- **Accessories**: Backpacks, caps, wallets
- **Home & Kitchen**: Mugs, water bottles, lunch boxes

All products have multiple variants (sizes/colors).

## Function Tools

The agent provides **8 function tools**:

1. **browse_catalog_tool** - Search products with filters
2. **get_product_details_tool** - View product details and variants
3. **add_to_cart_tool** - Add items to cart
4. **view_cart_tool** - Display cart contents
5. **remove_from_cart_tool** - Remove items from cart
6. **clear_cart_tool** - Empty the cart
7. **place_order_tool** - Create and save order
8. **get_last_order_tool** - View recent order

See [AGENTS.md](AGENTS.md) for detailed documentation.

## Quick Start

### Prerequisites
- Python 3.11+
- LiveKit Cloud account
- API keys: Google (Gemini), Murf, Deepgram

### Installation

1. **Install dependencies** (using uv):
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

2. **Configure environment** (`.env`):
```bash
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
GOOGLE_API_KEY=your_gemini_key
MURF_API_KEY=your_murf_key
DEEPGRAM_API_KEY=your_deepgram_key
```

3. **Run the agent**:
```bash
python src/agent.py dev
```

4. **Connect** via frontend at http://localhost:3000

## Example Voice Interactions

### Browsing
```
User: "Show me hoodies under 1600"
Agent: [Searches catalog] "We have a Premium Fleece Hoodie..."
```

### Adding to Cart
```
User: "Add a black hoodie in size L"
Agent: "Added 1x Premium Fleece Hoodie (L, black) - ₹1,599. Cart total: ₹1,599"
```

### Checkout
```
User: "Place my order"
Agent: "Order placed! Order ID: ORD-1732901234567. Total: ₹1,599 INR. Thank you!"
```

## Data Storage

Orders are persisted to `orders.json` in the backend directory:

```json
[
  {
    "order_id": "ORD-1732901234567",
    "items": [...],
    "total_amount": 1599,
    "currency": "INR",
    "created_at": "2025-11-29T21:59:17+05:30",
    "status": "confirmed"
  }
]
```

**Note:** Shopping cart is session-based (in-memory) and not persisted.

## Architecture

```
Voice Input → Deepgram STT → Gemini LLM → Function Tools
                                              ↓
                                      Commerce Logic
                                              ↓
                                    JSON Persistence ← Orders
                                              ↓
                                       Murf TTS → Voice Output
```

## Tech Stack

- **Framework**: LiveKit Agents
- **STT**: Deepgram Nova-3
- **LLM**: Google Gemini 2.5 Flash
- **TTS**: Murf AI (en-US-alicia)
- **VAD**: Silero
- **Language**: Python 3.11+

## Agent Persona

**Tone**: Friendly and enthusiastic shopping assistant

**Auto-Greeting**:
> "Welcome to our store! I'm your shopping assistant. We have a great selection of clothing, accessories, and home & kitchen items. How can I help you find something today?"

## Development

### Project Structure
```
backend/
├── src/
│   ├── agent.py          # Main agent with all tools
│   └── __init__.py
├── .env                   # Environment variables
├── orders.json           # Order persistence (created at runtime)
├── pyproject.toml        # Dependencies
└── README.md            # This file
```

### Testing

Start the agent and test each flow:

1. **Catalog browsing**:
   - "Show me all products"
   - "Show me black items"
   - "Accessories under 1000"

2. **Cart operations**:
   - "Add a t-shirt"
   - "What's in my cart?"
   - "Remove the t-shirt"

3. **Order placement**:
   - Add items → "Place my order"
   - Check `orders.json` for saved order

## Troubleshooting

**Agent not responding:**
- Check all API keys in `.env`
- Verify LiveKit connection
- Check logs for errors

**Order not saving:**
- Ensure write permissions in backend directory
- Check `orders.json` is not locked by another process

**Voice quality issues:**
- Check microphone permissions
- Verify Murf API quota
- Test internet connection

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed tool documentation and data models
- [Day9 README](../README.md) - User guide and examples

---

**Murf AI Voice Agents Challenge - Day 9/10**
