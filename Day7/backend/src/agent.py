import logging
import os
from pathlib import Path
from typing import Annotated, List, Dict, Any

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

# Import our custom modules
import database

logger = logging.getLogger("food_ordering_agent")

load_dotenv(".env")

FOOD_ORDERING_INSTRUCTIONS = """You are a friendly Food & Grocery Ordering Assistant for "FreshCart Express".
Your job is to help customers order food and groceries from our catalog.

YOUR PERSONA:
- Warm, friendly, and helpful.
- You make ordering easy and enjoyable.
- You're knowledgeable about products and can suggest recipes.
- You confirm all actions clearly so customers know what's happening.

CONVERSATION FLOW:
1. **Greeting**:
   - Greet the customer warmly.
   - Introduce yourself: "Welcome to FreshCart Express! I can help you order groceries, snacks, prepared meals, and even ingredients for recipes."
   - Ask: "What would you like to order today?"

2. **Taking Orders**:
   - Listen to what the customer wants to order.
   - For specific items (e.g., "bread", "milk", "pizza"):
     - Use `search_items_tool` to find matching items.
     - If multiple matches, ask for clarification (brand, size, type).
     - Once identified, use `add_to_cart_tool` with item_id and quantity.
     - Confirm: "I've added [quantity] [item name] to your cart."
   
   - For recipe/meal requests (e.g., "ingredients for a peanut butter sandwich", "pasta for two"):
     - Use `get_recipe_items_tool` with the recipe name.
     - If found, add all recipe items to cart and confirm:
       "I've added [list of items] to your cart for your [recipe name]."
     - If not found, say you don't have that recipe but offer to help them add individual items.

3. **Cart Management**:
   - When asked "What's in my cart?", use `view_cart_tool`.
   - If customer wants to remove items, use `remove_from_cart_tool`.
   - If customer wants to change quantity, use `update_cart_quantity_tool`.
   - Always confirm changes: "I've removed [item]" or "Updated [item] to [quantity]".

4. **Order Completion**:
   - When customer says they're done (e.g., "That's all", "Place my order", "Checkout"):
     - Use `view_cart_tool` to show final cart.
     - Read the total price.
     - Ask for customer name and delivery address for the order.
     - Once you have name and address, use `place_order_tool`.
     - Confirm: "Your order has been placed! Order ID: [id]. Total: ₹[amount]. It will be delivered to [address] soon. Thank you for shopping with FreshCart Express!"

IMPORTANT RULES:
- Always use tools to manage cart and search items.
- Be conversational and natural.
- Confirm every cart action verbally.
- If you can't find an item, apologize and ask if they'd like something else.
- Always calculate and mention the total when placing an order.
- For recipe requests, be intelligent - use the get_recipe_items_tool first.
"""

def prewarm(proc: JobProcess):
    """Prewarm function to load models."""
    logger.info("🔥 Prewarming Food Ordering Agent...")
    
    # Load catalog to verify it exists
    try:
        catalog = database.load_catalog()
        num_items = sum(len(items) for items in catalog.get("categories", {}).values())
        logger.info(f"✅ Catalog loaded with {num_items} items")
    except Exception as e:
        logger.error(f"❌ Failed to load catalog: {e}")

    # Load VAD model
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ VAD loaded")


async def entrypoint(ctx: JobContext):
    """Main entry point for the Food Ordering Agent."""
    
    ctx.log_context_fields = {"room": ctx.room.name}
    
    class FoodOrderingAgent(Agent):
        """Food Ordering Agent with cart management"""
        
        def __init__(self):
            super().__init__(instructions=FOOD_ORDERING_INSTRUCTIONS)
            self.cart: List[Dict[str, Any]] = []
            self.customer_info: Dict[str, str] = {}
        
        @function_tool
        async def search_items_tool(
            self,
            query: Annotated[str, "The item name or search term (e.g., 'bread', 'milk', 'chocolate')"]
        ) -> str:
            """Search for items in the catalog."""
            logger.info(f"Searching for: {query}")
            
            # First try exact name match
            item = database.get_item_by_name(query)
            if item:
                return f"Found: {item['name']} ({item['brand']}, {item['size']}) - ₹{item['price']}. Item ID: {item['id']}"
            
            # Then try broader search
            items = database.search_items(query)
            if not items:
                return f"Sorry, I couldn't find any items matching '{query}'. Could you try a different search term?"
            
            if len(items) == 1:
                item = items[0]
                return f"Found: {item['name']} ({item['brand']}, {item['size']}) - ₹{item['price']}. Item ID: {item['id']}"
            
            # Multiple items found
            result = f"I found {len(items)} items matching '{query}':\n"
            for item in items[:5]:  # Limit to 5 items
                result += f"- {item['name']} ({item['brand']}, {item['size']}) - ₹{item['price']} (ID: {item['id']})\n"
            result += "Which one would you like?"
            return result
        
        @function_tool
        async def get_recipe_items_tool(
            self,
            recipe_name: Annotated[str, "The recipe or meal name (e.g., 'peanut butter sandwich', 'pasta')"]
        ) -> str:
            """Get items needed for a recipe or meal."""
            logger.info(f"Getting recipe items for: {recipe_name}")
            
            recipe_data = database.get_recipe_items(recipe_name)
            if not recipe_data:
                return f"I don't have a recipe for '{recipe_name}' in my database. Would you like to add individual items instead?"
            
            items = recipe_data.get("items", [])
            if not items:
                return "Recipe found but no items available."
            
            # Add all items to cart
            for item in items:
                # Check if item already in cart
                existing = next((ci for ci in self.cart if ci["item"]["id"] == item["id"]), None)
                if existing:
                    existing["quantity"] += 1
                else:
                    self.cart.append({
                        "item": item,
                        "quantity": 1
                    })
            
            item_names = [f"{item['name']}" for item in items]
            return f"I've added the following items to your cart for '{recipe_data['recipe_name']}': {', '.join(item_names)}."
        
        @function_tool
        async def add_to_cart_tool(
            self,
            item_id: Annotated[str, "The ID of the item to add (from search results)"],
            quantity: Annotated[int, "The quantity to add"] = 1
        ) -> str:
            """Add an item to the cart."""
            logger.info(f"Adding to cart: {item_id} x {quantity}")
            
            item = database.get_item_by_id(item_id)
            if not item:
                return f"Item with ID {item_id} not found. Please search for the item first."
            
            # Check if item already in cart
            existing = next((ci for ci in self.cart if ci["item"]["id"] == item_id), None)
            if existing:
                existing["quantity"] += quantity
                return f"Updated {item['name']} quantity to {existing['quantity']} in your cart."
            else:
                self.cart.append({
                    "item": item,
                    "quantity": quantity
                })
                return f"Added {quantity} {item['name']} to your cart."
        
        @function_tool
        async def remove_from_cart_tool(
            self,
            item_id: Annotated[str, "The ID of the item to remove"]
        ) -> str:
            """Remove an item from the cart."""
            logger.info(f"Removing from cart: {item_id}")
            
            initial_len = len(self.cart)
            self.cart = [ci for ci in self.cart if ci["item"]["id"] != item_id]
            
            if len(self.cart) < initial_len:
                return "Item removed from cart."
            else:
                return "Item not found in cart."
        
        @function_tool
        async def update_cart_quantity_tool(
            self,
            item_id: Annotated[str, "The ID of the item to update"],
            quantity: Annotated[int, "The new quantity (use 0 to remove)"]
        ) -> str:
            """Update the quantity of an item in the cart."""
            logger.info(f"Updating cart quantity: {item_id} to {quantity}")
            
            if quantity == 0:
                return await self.remove_from_cart_tool(item_id)
            
            cart_item = next((ci for ci in self.cart if ci["item"]["id"] == item_id), None)
            if cart_item:
                cart_item["quantity"] = quantity
                return f"Updated {cart_item['item']['name']} quantity to {quantity}."
            else:
                return "Item not found in cart."
        
        @function_tool
        async def view_cart_tool(self) -> str:
            """View all items currently in the cart."""
            logger.info("Viewing cart")
            
            if not self.cart:
                return "Your cart is empty."
            
            result = "Your cart:\n"
            for cart_item in self.cart:
                item = cart_item["item"]
                qty = cart_item["quantity"]
                subtotal = item["price"] * qty
                result += f"- {item['name']} x {qty} = ₹{subtotal}\n"
            
            total = database.calculate_cart_total(self.cart)
            result += f"\nTotal: ₹{total:.2f}"
            return result
        
        @function_tool
        async def place_order_tool(
            self,
            customer_name: Annotated[str, "The customer's name"],
            delivery_address: Annotated[str, "The delivery address"]
        ) -> str:
            """Place the order and save it to file."""
            logger.info(f"Placing order for: {customer_name}")
            
            if not self.cart:
                return "Cannot place order - cart is empty."
            
            # Prepare order data
            order_items = []
            for cart_item in self.cart:
                item = cart_item["item"]
                order_items.append({
                    "item_id": item["id"],
                    "name": item["name"],
                    "brand": item.get("brand"),
                    "quantity": cart_item["quantity"],
                    "unit_price": item["price"],
                    "subtotal": item["price"] * cart_item["quantity"]
                })
            
            total = database.calculate_cart_total(self.cart)
            
            order = {
                "customer_name": customer_name,
                "delivery_address": delivery_address,
                "items": order_items,
                "total": total,
                "status": "placed"
            }
            
            # Save order
            order_id = database.save_order(order)
            
            # Clear cart
            self.cart = []
            
            return f"Order placed successfully! Order ID: {order_id}. Total: ₹{total:.2f}. Thank you, {customer_name}!"

    # Create agent instance
    food_agent = FoodOrderingAgent()
    
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
        agent=food_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    await ctx.connect()
    
    logger.info("🎙️ Food Ordering Agent is live!")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
