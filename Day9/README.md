# Day 9: E-commerce Voice Agent 🛒

An interactive voice-powered shopping assistant following the Agentic Commerce Protocol (ACP) pattern. Browse products, manage your cart, and place orders—all with your voice!

## Features
- **Smart Catalog Browsing**: Search products by category, price, color, or size
- **Voice Shopping**: Natural conversations like "Show me black hoodies under 1500"
- **Shopping Cart**: Add, remove, view items with real-time totals
- **Multi-Item Orders**: Buy multiple products in a single transaction
- **Order Persistence**: All orders saved to `orders.json`
- **Order History**: Check your last order anytime
- **Friendly Assistant**: Enthusiastic and helpful shopping companion
- **Auto-Greeting**: Agent welcomes you when you connect

## Product Catalog

### Categories (9 Products Total)
1. **Clothing** (₹799 - ₹1,999)
   - Classic Cotton T-Shirt (various sizes & colors)
   - Premium Fleece Hoodie
   - Slim Fit Denim Jeans

2. **Accessories** (₹499 - ₹1,299)
   - Travel Backpack 25L
   - Baseball Cap
   - Leather Wallet

3. **Home & Kitchen** (₹349 - ₹1,199)
   - Ceramic Coffee Mug
   - Stainless Steel Water Bottle
   - Premium Lunch Box Set

All products have multiple variants (sizes/colors) to choose from!

## Quick Start

### 1. Start Backend (Shopping Agent)
```bash
cd backend
python src/agent.py dev
```

### 2. Start Frontend (UI)
```bash
cd frontend
npm run dev
```

### 3. Start Shopping
- Open http://localhost:3000
- Click **"🛒 Start Shopping"** and allow microphone access
- The assistant will greet you
- Start browsing and shopping!

## Example Voice Commands

### Browsing Products
- "Show me all products"
- "Show me t-shirts under 1000 rupees"
- "Do you have any black hoodies?"
- "Show me accessories"
- "What mugs do you have in blue?"

### Adding to Cart
- "Add a black t-shirt size M to my cart"
- "I'll take 2 white coffee mugs"
- "Add the gray hoodie in size L"

### Managing Cart
- "What's in my cart?"
- "Show me my cart"
- "Remove the t-shirt"
- "Clear my cart"

### Checkout
- "Place my order"
- "I'm ready to checkout"
- "What did I just order?"

## ACP-Inspired Architecture

This agent follows key patterns from the Agentic Commerce Protocol:

```
┌─────────────────┐
│  Voice Layer    │  ← User speaks
│  (LLM + TTS)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Agent Tools    │  ← 8 function tools
│  (Functions)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Commerce Logic │  ← Catalog, Cart, Orders
│  (Python)       │
└────────┬────────┘
         │
┌────────▼────────┐
│  Persistence    │  ← orders.json
│  (JSON File)    │
└─────────────────┘
```

**Clean Separation of Concerns:**
- **Conversation**: Handled by LLM with voice interface
- **Commerce Logic**: Product catalog, cart management, order creation
- **Persistence**: JSON-based order storage

## Complete Shopping Flow

1. **Browse** → Agent shows products with filters
2. **Add to Cart** → Confirm variant (size/color) and quantity
3. **Review Cart** → See all items and total
4. **Checkout** → Place order and get confirmation
5. **Order Saved** → Persisted to `orders.json` with unique ID

## Documentation
- [Backend README](backend/README.md) - Technical details and tools
- [AGENTS.md](backend/AGENTS.md) - Agent capabilities and data models

---

**Murf AI Voice Agents Challenge - Day 9/10**
