import logging
from typing import Annotated, List, Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("ecommerce_agent")

load_dotenv(".env")

# ============================================================================
# PRODUCT CATALOG
# ============================================================================

PRODUCTS = [
    # CLOTHING CATEGORY
    {
        "id": "tshirt-001",
        "name": "Classic Cotton T-Shirt",
        "description": "Comfortable 100% cotton t-shirt, perfect for everyday wear",
        "category": "clothing",
        "base_price": 799,
        "currency": "INR",
        "variants": [
            {"size": "S", "color": "black", "price": 799, "stock": 10},
            {"size": "M", "color": "black", "price": 799, "stock": 15},
            {"size": "L", "color": "black", "price": 849, "stock": 8},
            {"size": "S", "color": "white", "price": 799, "stock": 12},
            {"size": "M", "color": "white", "price": 799, "stock": 20},
            {"size": "L", "color": "white", "price": 849, "stock": 5},
            {"size": "M", "color": "blue", "price": 849, "stock": 10},
        ]
    },
    {
        "id": "hoodie-001",
        "name": "Premium Fleece Hoodie",
        "description": "Warm and cozy fleece hoodie with kangaroo pocket",
        "category": "clothing",
        "base_price": 1499,
        "currency": "INR",
        "variants": [
            {"size": "M", "color": "black", "price": 1499, "stock": 8},
            {"size": "L", "color": "black", "price": 1599, "stock": 6},
            {"size": "XL", "color": "black", "price": 1699, "stock": 4},
            {"size": "M", "color": "gray", "price": 1499, "stock": 10},
            {"size": "L", "color": "gray", "price": 1599, "stock": 7},
        ]
    },
    {
        "id": "jeans-001",
        "name": "Slim Fit Denim Jeans",
        "description": "Stylish slim fit jeans with stretch fabric",
        "category": "clothing",
        "base_price": 1899,
        "currency": "INR",
        "variants": [
            {"size": "30", "color": "blue", "price": 1899, "stock": 5},
            {"size": "32", "color": "blue", "price": 1899, "stock": 8},
            {"size": "34", "color": "blue", "price": 1899, "stock": 6},
            {"size": "32", "color": "black", "price": 1999, "stock": 10},
            {"size": "34", "color": "black", "price": 1999, "stock": 4},
        ]
    },
    
    # ACCESSORIES CATEGORY
    {
        "id": "backpack-001",
        "name": "Travel Backpack 25L",
        "description": "Durable water-resistant backpack with laptop compartment",
        "category": "accessories",
        "base_price": 1299,
        "currency": "INR",
        "variants": [
            {"size": "standard", "color": "black", "price": 1299, "stock": 12},
            {"size": "standard", "color": "navy", "price": 1299, "stock": 8},
            {"size": "standard", "color": "gray", "price": 1349, "stock": 6},
        ]
    },
    {
        "id": "cap-001",
        "name": "Baseball Cap",
        "description": "Classic baseball cap with adjustable strap",
        "category": "accessories",
        "base_price": 499,
        "currency": "INR",
        "variants": [
            {"size": "adjustable", "color": "black", "price": 499, "stock": 20},
            {"size": "adjustable", "color": "white", "price": 499, "stock": 15},
            {"size": "adjustable", "color": "red", "price": 549, "stock": 10},
        ]
    },
    {
        "id": "wallet-001",
        "name": "Leather Wallet",
        "description": "Genuine leather bifold wallet with RFID protection",
        "category": "accessories",
        "base_price": 899,
        "currency": "INR",
        "variants": [
            {"size": "standard", "color": "brown", "price": 899, "stock": 15},
            {"size": "standard", "color": "black", "price": 899, "stock": 12},
        ]
    },
    
    # HOME & KITCHEN CATEGORY
    {
        "id": "mug-001",
        "name": "Ceramic Coffee Mug",
        "description": "Handcrafted ceramic mug, perfect for coffee or tea",
        "category": "home_kitchen",
        "base_price": 349,
        "currency": "INR",
        "variants": [
            {"size": "350ml", "color": "white", "price": 349, "stock": 25},
            {"size": "350ml", "color": "black", "price": 349, "stock": 20},
            {"size": "350ml", "color": "blue", "price": 399, "stock": 15},
            {"size": "500ml", "color": "white", "price": 449, "stock": 10},
        ]
    },
    {
        "id": "bottle-001",
        "name": "Stainless Steel Water Bottle",
        "description": "Insulated water bottle keeps drinks cold for 24 hours",
        "category": "home_kitchen",
        "base_price": 799,
        "currency": "INR",
        "variants": [
            {"size": "750ml", "color": "silver", "price": 799, "stock": 18},
            {"size": "750ml", "color": "black", "price": 799, "stock": 14},
            {"size": "1L", "color": "silver", "price": 899, "stock": 10},
            {"size": "1L", "color": "blue", "price": 949, "stock": 8},
        ]
    },
    {
        "id": "lunchbox-001",
        "name": "Premium Lunch Box Set",
        "description": "3-compartment stainless steel lunch box with bag",
        "category": "home_kitchen",
        "base_price": 1199,
        "currency": "INR",
        "variants": [
            {"size": "standard", "color": "silver", "price": 1199, "stock": 10},
            {"size": "standard", "color": "black", "price": 1249, "stock": 8},
        ]
    },
]

# ============================================================================
# GLOBAL STATE
# ============================================================================

SHOPPING_CART: List[Dict[str, Any]] = []
ORDERS_FILE = Path("orders.json")

# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

ECOMMERCE_AGENT_INSTRUCTIONS = """You are a friendly shopping assistant for an online store. Your goal is to help customers browse products, manage their shopping cart, and place orders.

YOUR PERSONA:
- You are helpful, enthusiastic, and knowledgeable about all products.
- You provide clear product recommendations based on customer needs.
- You're patient and happy to answer questions about products, pricing, and features.
- You keep the conversation natural and engaging.

PRODUCT CATALOG:
Our store has 3 main categories:
1. **Clothing**: T-shirts, hoodies, jeans (various sizes and colors)
2. **Accessories**: Backpacks, caps, wallets
3. **Home & Kitchen**: Mugs, water bottles, lunch boxes

Price range: ₹349 to ₹1999 INR

YOUR TOOLS:
You have access to several tools to help customers:
- `browse_catalog_tool`: Search products by category, price, color, or size
- `get_product_details_tool`: Get full details about a specific product
- `add_to_cart_tool`: Add items to the shopping cart
- `view_cart_tool`: Show what's currently in the cart
- `remove_from_cart_tool`: Remove items from the cart
- `clear_cart_tool`: Empty the entire cart
- `place_order_tool`: Complete the purchase
- `get_last_order_tool`: Show the most recent order

HOW TO HELP CUSTOMERS:

1. **Browsing & Discovery**:
   - When customers ask to see products, use `browse_catalog_tool` with appropriate filters
   - Example: "Show me t-shirts under 1000" → filter by category="clothing" and max_price=1000
   - Mention 2-3 relevant products with names and prices
   - Highlight key features

2. **Product Details**:
   - When customers ask about a specific product, use `get_product_details_tool`
   - Share available sizes, colors, and price variations
   - Be specific about what's in stock

3. **Adding to Cart**:
   - When customers want to buy something, use `add_to_cart_tool`
   - Always confirm the variant (size/color) before adding
   - If they don't specify, ask: "What size and color would you like?"
   - Confirm what was added and show the updated cart total

4. **Cart Management**:
   - Use `view_cart_tool` when customers ask "What's in my cart?"
   - Help remove items with `remove_from_cart_tool` if they change their mind
   - Summarize the cart clearly: item names, quantities, and total price

5. **Checkout**:
   - When customers are ready to buy, use `place_order_tool`
   - Share the order ID and total amount
   - Confirm that the cart has been cleared
   - Thank them for their purchase!

CONVERSATION STYLE:
- Start by greeting customers warmly (only on first interaction)
- Ask clarifying questions when needed (size, color, quantity)
- Provide helpful suggestions based on their needs
- Be concise but friendly
- Use natural language, not robotic responses

EXAMPLES:

Customer: "Show me some t-shirts"
You: "Sure! Let me show you our t-shirt collection." [calls browse_catalog_tool with category="clothing"]
Then: "We have a great Classic Cotton T-Shirt available in various sizes and colors for just ₹799. It's comfortable and perfect for everyday wear. Would you like to know more about it or see other options?"

Customer: "Add a black t-shirt size M to my cart"
You: [calls add_to_cart_tool with appropriate parameters]
Then: "Perfect! I've added one black Classic Cotton T-Shirt in size M (₹799) to your cart. Your cart total is now ₹799. Would you like to continue shopping or check out?"

Customer: "What's in my cart?"
You: [calls view_cart_tool]
Then: "You currently have 2 items in your cart: 1x Black T-Shirt (M) - ₹799 and 1x Coffee Mug (White, 350ml) - ₹349. Your total is ₹1,148. Would you like to proceed to checkout or keep shopping?"

IMPORTANT RULES:
- Always use tools to get accurate product information
- Never make up product details or prices
- Confirm variant details before adding to cart
- Keep track of the cart state by using view_cart_tool when needed
- Be helpful if customers want to modify their cart
- Make the shopping experience smooth and enjoyable!

Remember: Your goal is to help customers find what they need and complete their purchase successfully!
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_orders() -> List[Dict[str, Any]]:
    """Load existing orders from JSON file."""
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_order(order: Dict[str, Any]):
    """Save a new order to JSON file."""
    orders = load_orders()
    orders.append(order)
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

def generate_order_id() -> str:
    """Generate a unique order ID."""
    timestamp = int(datetime.now().timestamp() * 1000)
    return f"ORD-{timestamp}"

def find_product(product_id: str) -> Optional[Dict[str, Any]]:
    """Find a product by ID."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None

def filter_products(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    color: Optional[str] = None,
    size: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter products based on criteria."""
    filtered = PRODUCTS.copy()
    
    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]
    
    if max_price:
        filtered = [p for p in filtered if p["base_price"] <= max_price]
    
    if color:
        filtered = [
            p for p in filtered 
            if any(v["color"].lower() == color.lower() for v in p["variants"])
        ]
    
    if size:
        filtered = [
            p for p in filtered 
            if any(v["size"].lower() == size.lower() for v in p["variants"])
        ]
    
    return filtered

def calculate_cart_total() -> int:
    """Calculate total cart value."""
    return sum(item["total_price"] for item in SHOPPING_CART)

# ============================================================================
# PREWARM
# ============================================================================

def prewarm(proc: JobProcess):
    """Prewarm function to load models."""
    logger.info("🔥 Prewarming E-commerce Agent...")
    
    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")

# ============================================================================
# MAIN AGENT
# ============================================================================

async def entrypoint(ctx: JobContext):
    """Main entry point for the E-commerce Agent."""
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    class EcommerceAgent(Agent):
        """Voice Shopping Assistant Agent"""
        
        def __init__(self):
            super().__init__(instructions=ECOMMERCE_AGENT_INSTRUCTIONS)
        
        @function_tool
        async def browse_catalog_tool(
            self,
            category: Annotated[Optional[str], "Filter by category: 'clothing', 'accessories', or 'home_kitchen'"] = None,
            max_price: Annotated[Optional[int], "Maximum price in INR"] = None,
            color: Annotated[Optional[str], "Filter by color (e.g., 'black', 'white', 'blue')"] = None,
            size: Annotated[Optional[str], "Filter by size (e.g., 'M', 'L', 'standard')"] = None
        ) -> str:
            """Browse the product catalog with optional filters."""
            logger.info(f"Browsing catalog: category={category}, max_price={max_price}, color={color}, size={size}")
            
            filtered_products = filter_products(category, max_price, color, size)
            
            if not filtered_products:
                return "No products found matching your criteria. Try adjusting your filters."
            
            result = f"Found {len(filtered_products)} product(s):\n\n"
            for product in filtered_products[:10]:  # Limit to 10 results
                result += f"- {product['name']} ({product['id']})\n"
                result += f"  Category: {product['category'].replace('_', ' ').title()}\n"
                result += f"  Price: ₹{product['base_price']} {product['currency']}\n"
                result += f"  Description: {product['description']}\n"
                result += f"  Available colors: {', '.join(set(v['color'] for v in product['variants']))}\n\n"
            
            return result
        
        @function_tool
        async def get_product_details_tool(
            self,
            product_id: Annotated[str, "The product ID to get details for"]
        ) -> str:
            """Get detailed information about a specific product including all variants."""
            logger.info(f"Getting details for product: {product_id}")
            
            product = find_product(product_id)
            if not product:
                return f"Product '{product_id}' not found."
            
            result = f"📦 {product['name']} ({product['id']})\n\n"
            result += f"Description: {product['description']}\n"
            result += f"Category: {product['category'].replace('_', ' ').title()}\n"
            result += f"Base Price: ₹{product['base_price']} {product['currency']}\n\n"
            result += "Available Variants:\n"
            
            for variant in product['variants']:
                result += f"- Size: {variant['size']}, Color: {variant['color']}, "
                result += f"Price: ₹{variant['price']}, Stock: {variant['stock']}\n"
            
            return result
        
        @function_tool
        async def add_to_cart_tool(
            self,
            product_id: Annotated[str, "The product ID to add"],
            size: Annotated[str, "The size variant (e.g., 'M', 'L', 'standard')"],
            color: Annotated[str, "The color variant (e.g., 'black', 'white')"],
            quantity: Annotated[int, "Quantity to add (default: 1)"] = 1
        ) -> str:
            """Add a product to the shopping cart."""
            logger.info(f"Adding to cart: {product_id}, size={size}, color={color}, qty={quantity}")
            
            product = find_product(product_id)
            if not product:
                return f"Product '{product_id}' not found."
            
            # Find matching variant
            variant = None
            for v in product['variants']:
                if v['size'].lower() == size.lower() and v['color'].lower() == color.lower():
                    variant = v
                    break
            
            if not variant:
                return f"Variant not found. {product['name']} is not available in size {size} and color {color}."
            
            if variant['stock'] < quantity:
                return f"Sorry, only {variant['stock']} units available in stock."
            
            # Add to cart
            cart_item = {
                "product_id": product_id,
                "product_name": product['name'],
                "variant": {"size": size, "color": color},
                "quantity": quantity,
                "unit_price": variant['price'],
                "total_price": variant['price'] * quantity
            }
            
            SHOPPING_CART.append(cart_item)
            
            cart_total = calculate_cart_total()
            return (f"✅ Added {quantity}x {product['name']} ({size}, {color}) to your cart.\n"
                   f"Item price: ₹{cart_item['total_price']}\n"
                   f"Cart total: ₹{cart_total} INR\n"
                   f"Total items in cart: {len(SHOPPING_CART)}")
        
        @function_tool
        async def view_cart_tool(self) -> str:
            """View the current shopping cart contents."""
            logger.info("Viewing cart")
            
            if not SHOPPING_CART:
                return "Your shopping cart is empty. Browse our products to add items!"
            
            result = f"🛒 Your Shopping Cart ({len(SHOPPING_CART)} item(s)):\n\n"
            
            for i, item in enumerate(SHOPPING_CART, 1):
                result += f"{i}. {item['product_name']}\n"
                result += f"   Size: {item['variant']['size']}, Color: {item['variant']['color']}\n"
                result += f"   Quantity: {item['quantity']}, Price: ₹{item['total_price']}\n\n"
            
            total = calculate_cart_total()
            result += f"💰 Total: ₹{total} INR"
            
            return result
        
        @function_tool
        async def remove_from_cart_tool(
            self,
            product_id: Annotated[str, "The product ID to remove"]
        ) -> str:
            """Remove a product from the shopping cart."""
            logger.info(f"Removing from cart: {product_id}")
            
            initial_count = len(SHOPPING_CART)
            # Filter out items with matching product_id
            filtered_cart = [item for item in SHOPPING_CART if item['product_id'] != product_id]
            removed_count = initial_count - len(filtered_cart)
            
            # Clear and repopulate the cart
            SHOPPING_CART.clear()
            SHOPPING_CART.extend(filtered_cart)
            
            if removed_count == 0:
                return f"Product '{product_id}' not found in cart."
            
            cart_total = calculate_cart_total()
            return (f"✅ Removed {removed_count} item(s) from cart.\n"
                   f"Cart total: ₹{cart_total} INR\n"
                   f"Items remaining: {len(SHOPPING_CART)}")
        
        @function_tool
        async def clear_cart_tool(self) -> str:
            """Clear all items from the shopping cart."""
            logger.info("Clearing cart")
            
            item_count = len(SHOPPING_CART)
            SHOPPING_CART.clear()
            
            return f"✅ Cart cleared. Removed {item_count} item(s)."
        
        @function_tool
        async def place_order_tool(self) -> str:
            """Place an order with the current cart contents."""
            logger.info("Placing order")
            
            if not SHOPPING_CART:
                return "Your cart is empty. Add some products before placing an order!"
            
            # Create order object
            order = {
                "order_id": generate_order_id(),
                "items": SHOPPING_CART.copy(),
                "total_amount": calculate_cart_total(),
                "currency": "INR",
                "created_at": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            # Save order
            save_order(order)
            
            # Clear cart
            item_count = len(SHOPPING_CART)
            SHOPPING_CART.clear()
            
            result = f"🎉 Order Placed Successfully!\n\n"
            result += f"Order ID: {order['order_id']}\n"
            result += f"Items: {item_count}\n"
            result += f"Total Amount: ₹{order['total_amount']} INR\n"
            result += f"Status: {order['status'].title()}\n\n"
            result += f"Thank you for your purchase! Your order has been confirmed."
            
            return result
        
        @function_tool
        async def get_last_order_tool(self) -> str:
            """Get details of the most recent order."""
            logger.info("Getting last order")
            
            orders = load_orders()
            if not orders:
                return "No orders found. You haven't placed any orders yet."
            
            last_order = orders[-1]
            
            result = f"📦 Your Last Order\n\n"
            result += f"Order ID: {last_order['order_id']}\n"
            result += f"Date: {last_order['created_at']}\n"
            result += f"Status: {last_order['status'].title()}\n\n"
            result += f"Items ({len(last_order['items'])}):\n"
            
            for i, item in enumerate(last_order['items'], 1):
                result += f"{i}. {item['product_name']} "
                result += f"({item['variant']['size']}, {item['variant']['color']}) "
                result += f"x{item['quantity']} - ₹{item['total_price']}\n"
            
            result += f"\n💰 Total: ₹{last_order['total_amount']} INR"
            
            return result
    
    # Create agent instance
    shopping_agent = EcommerceAgent()
    
    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-alicia", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )
    
    # Metrics collection
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"📊 Usage: {summary}")
    
    ctx.add_shutdown_callback(log_usage)
    
    # Start the session
    await session.start(
        agent=shopping_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🛒 E-commerce Agent is live! Ready to help customers shop...")
    
    # Send initial greeting
    greeting = (
        "Welcome to our store! I'm your shopping assistant. "
        "We have a great selection of clothing, accessories, and home & kitchen items. "
        "How can I help you find something today?"
    )
    await session.say(greeting, add_to_chat_ctx=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
