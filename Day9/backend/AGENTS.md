# E-commerce Voice Agent - Technical Documentation

## Overview
A voice-powered shopping assistant built using LiveKit Agents and following the Agentic Commerce Protocol (ACP) pattern. This agent provides a natural voice interface for browsing products, managing a shopping cart, and placing orders.

## Agent Capabilities

### Core Functions
The agent exposes **8 function tools** for complete e-commerce functionality:

#### 1. **browse_catalog_tool**
Search and filter the product catalog.

**Parameters:**
- `category` (optional): Filter by category (`clothing`, `accessories`, `home_kitchen`)
- `max_price` (optional): Maximum price in INR
- `color` (optional): Filter by color (e.g., `black`, `white`, `blue`)
- `size` (optional): Filter by size (e.g., `M`, `L`, `standard`)

**Returns:** List of matching products with details

**Example Usage:**
```
"Show me clothing under 1500 rupees"
→ browse_catalog_tool(category="clothing", max_price=1500)
```

#### 2. **get_product_details_tool**
Get comprehensive details about a specific product including all variants.

**Parameters:**
- `product_id` (required): The product ID (e.g., `tshirt-001`)

**Returns:** Full product details with all size/color variants and stock levels

#### 3. **add_to_cart_tool**
Add a product variant to the shopping cart.

**Parameters:**
- `product_id` (required): Product ID
- `size` (required): Size variant
- `color` (required): Color variant
- `quantity` (optional, default=1): Quantity to add

**Returns:** Confirmation with item details and updated cart total

**Example:**
```
"Add a black t-shirt in size M"
→ add_to_cart_tool(product_id="tshirt-001", size="M", color="black", quantity=1)
```

#### 4. **view_cart_tool**
Display current shopping cart contents.

**Parameters:** None

**Returns:** List of all cart items with quantities, prices, and total

#### 5. **remove_from_cart_tool**
Remove a product from the cart.

**Parameters:**
- `product_id` (required): Product ID to remove

**Returns:** Confirmation and updated cart total

#### 6. **clear_cart_tool**
Empty the entire shopping cart.

**Parameters:** None

**Returns:** Confirmation of cleared cart

#### 7. **place_order_tool**
Create an order from current cart contents.

**Parameters:** None

**Returns:** Order confirmation with order ID, items, and total

**Side Effects:**
- Creates order object with unique ID
- Saves order to `orders.json`
- Clears the shopping cart

#### 8. **get_last_order_tool**
Retrieve details of the most recent order.

**Parameters:** None

**Returns:** Last order details including ID, items, and total

---

## Data Models

### Product Model
```python
{
    "id": "tshirt-001",
    "name": "Classic Cotton T-Shirt",
    "description": "Comfortable 100% cotton t-shirt",
    "category": "clothing",  # clothing | accessories | home_kitchen
    "base_price": 799,
    "currency": "INR",
    "variants": [
        {
            "size": "M",
            "color": "black",
            "price": 799,
            "stock": 15
        }
        # ... more variants
    ]
}
```

### Cart Item Model
```python
{
    "product_id": "tshirt-001",
    "product_name": "Classic Cotton T-Shirt",
    "variant": {
        "size": "M",
        "color": "black"
    },
    "quantity": 2,
    "unit_price": 799,
    "total_price": 1598
}
```

### Order Model
```python
{
    "order_id": "ORD-1732901234567",
    "items": [
        # List of cart items
    ],
    "total_amount": 3500,
    "currency": "INR",
    "created_at": "2025-11-29T21:59:17+05:30",
    "status": "confirmed"
}
```

---

## ACP Pattern Implementation

This agent implements a **simplified Agentic Commerce Protocol** pattern:

### 1. Conversation Layer (Voice Interface)
- **STT**: Deepgram Nova-3 for speech recognition
- **LLM**: Google Gemini 2.5 Flash for intent understanding
- **TTS**: Murf AI (en-US-alicia) for natural voice responses
- **Turn Detection**: Multilingual model for smooth conversations

### 2. Commerce Logic Layer
Clean separation of concerns:
- **Catalog Management**: Product browsing and filtering
- **Cart Management**: Session-based cart operations
- **Order Management**: Order creation and persistence

### 3. Persistence Layer
- **Format**: JSON
- **File**: `orders.json` (created in backend directory)
- **Structure**: Append-only list of order objects

### Architecture Flow
```
User Voice Input
       ↓
  STT (Deepgram)
       ↓
  LLM (Gemini) → Determines intent & tool to call
       ↓
  Function Tool Execution
       ↓
  Commerce Logic (Python)
       ↓
  JSON Persistence (if order)
       ↓
  Response Generation (LLM)
       ↓
  TTS (Murf)
       ↓
  Voice Output to User
```

---

## Product Catalog

### Total Products: 9
**Categories:** 3

#### Clothing (3 products)
- **tshirt-001**: Classic Cotton T-Shirt (₹799)
- **hoodie-001**: Premium Fleece Hoodie (₹1,499)
- **jeans-001**: Slim Fit Denim Jeans (₹1,899)

#### Accessories (3 products)
- **backpack-001**: Travel Backpack 25L (₹1,299)
- **cap-001**: Baseball Cap (₹499)
- **wallet-001**: Leather Wallet (₹899)

#### Home & Kitchen (3 products)
- **mug-001**: Ceramic Coffee Mug (₹349)
- **bottle-001**: Stainless Steel Water Bottle (₹799)
- **lunchbox-001**: Premium Lunch Box Set (₹1,199)

All products have multiple variants (sizes and colors).

---

## Agent Persona

**Tone:** Friendly, enthusiastic, helpful

**Behavior:**
- Greets customers warmly on connection
- Asks clarifying questions (size/color) when needed
- Provides product recommendations
- Confirms actions clearly
- Thanks customers after purchase

**Example Interactions:**

**Browsing:**
> User: "Show me some t-shirts"
> 
> Agent: "Sure! Let me show you our t-shirt collection." [calls browse_catalog_tool]
> 
> Agent: "We have a great Classic Cotton T-Shirt available in various sizes and colors for just ₹799..."

**Adding to Cart:**
> User: "Add a black hoodie size L"
> 
> Agent: [calls add_to_cart_tool]
> 
> Agent: "Perfect! I've added one black Premium Fleece Hoodie in size L (₹1,599) to your cart..."

**Checkout:**
> User: "Place my order"
> 
> Agent: [calls place_order_tool]
> 
> Agent: "Order placed successfully! Your order ID is ORD-1732901234567. Total: ₹2,398 INR. Thank you for your purchase!"

---

## Technical Stack

- **Framework**: LiveKit Agents v0.10.8
- **LLM**: Google Gemini 2.5 Flash
- **STT**: Deepgram Nova-3
- **TTS**: Murf AI
- **VAD**: Silero
- **Language**: Python 3.11+
- **Persistence**: JSON file storage

---

## Running the Agent

### Development Mode
```bash
cd backend
python src/agent.py dev
```

### Environment Variables Required
```
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
GOOGLE_API_KEY=...
MURF_API_KEY=...
DEEPGRAM_API_KEY=...
```

---

## State Management

### Global State
- `PRODUCTS`: Static list of all products (defined at startup)
- `SHOPPING_CART`: Session-based list of cart items (in-memory)
- `ORDERS_FILE`: Path to `orders.json` for persistence

### Session Lifecycle
1. Agent starts → Empty cart
2. User browses and adds items → Cart populates
3. User places order → Order saved, cart clears
4. Connection ends → Cart data lost (session-based)

**Note:** Only orders are persisted. Cart data is ephemeral per session.

---

## Error Handling

The agent gracefully handles:
- Empty cart checkout attempts
- Invalid product IDs
- Unavailable variants (size/color combinations)
- Out-of-stock items
- Malformed requests

All errors are communicated naturally to the user via voice.

---

## Future Enhancements (Beyond MVP)

Potential improvements following full ACP specification:
- User authentication and account management
- Order history (multiple orders)
- Payment provider integration
- Inventory management with stock updates
- Product recommendations based on browsing history
- Multi-language support
- Price calculations with taxes and shipping

---

**Murf AI Voice Agents Challenge - Day 9/10**
