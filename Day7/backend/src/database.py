import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("food_ordering")

# File paths
DATA_DIR = Path(__file__).parent.parent / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
ORDERS_PATH = DATA_DIR / "orders.json"
CURRENT_ORDER_PATH = DATA_DIR / "current_order.json"

def load_catalog() -> Dict[str, Any]:
    """Load the catalog from JSON file."""
    try:
        with open(CATALOG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Catalog file not found: {CATALOG_PATH}")
        return {"categories": {}, "recipes": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding catalog JSON: {e}")
        return {"categories": {}, "recipes": {}}

def get_item_by_id(item_id: str) -> Optional[Dict[str, Any]]:
    """Get an item from the catalog by its ID."""
    catalog = load_catalog()
    for category_name, items in catalog.get("categories", {}).items():
        for item in items:
            if item.get("id") == item_id:
                return item
    return None

def get_item_by_name(item_name: str) -> Optional[Dict[str, Any]]:
    """Get an item from the catalog by its name (case-insensitive search)."""
    catalog = load_catalog()
    item_name_lower = item_name.lower()
    
    for category_name, items in catalog.get("categories", {}).items():
        for item in items:
            if item.get("name", "").lower() == item_name_lower:
                return item
            # Also check if the search term is contained in the name
            if item_name_lower in item.get("name", "").lower():
                return item
    return None

def search_items(query: str) -> List[Dict[str, Any]]:
    """Search for items in the catalog by name or tags."""
    catalog = load_catalog()
    results = []
    query_lower = query.lower()
    
    for category_name, items in catalog.get("categories", {}).items():
        for item in items:
            # Search in name
            if query_lower in item.get("name", "").lower():
                results.append(item)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in item.get("tags", [])):
                results.append(item)
                continue
            
            # Search in category
            if query_lower in item.get("category", "").lower():
                results.append(item)
    
    return results

def get_recipe_items(recipe_name: str) -> Optional[Dict[str, Any]]:
    """Get the items for a recipe."""
    catalog = load_catalog()
    recipes = catalog.get("recipes", {})
    
    recipe_name_lower = recipe_name.lower()
    if recipe_name_lower in recipes:
        recipe = recipes[recipe_name_lower]
        items = []
        for item_id in recipe.get("items", []):
            item = get_item_by_id(item_id)
            if item:
                items.append(item)
        
        return {
            "recipe_name": recipe.get("name"),
            "items": items
        }
    
    return None

def save_order(order: Dict[str, Any], order_id: str = None) -> str:
    """Save an order to the orders file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate order ID if not provided
    if not order_id:
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    order["order_id"] = order_id
    order["timestamp"] = datetime.now().isoformat()
    
    # Load existing orders
    try:
        with open(ORDERS_PATH, 'r') as f:
            all_orders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_orders = []
    
    # Add new order
    all_orders.append(order)
    
    # Save all orders
    with open(ORDERS_PATH, 'w') as f:
        json.dump(all_orders, f, indent=2)
    
    # Also save as current order for easy access
    with open(CURRENT_ORDER_PATH, 'w') as f:
        json.dump(order, f, indent=2)
    
    logger.info(f"Order {order_id} saved successfully")
    return order_id

def get_all_orders() -> List[Dict[str, Any]]:
    """Get all orders from the orders file."""
    try:
        with open(ORDERS_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def calculate_cart_total(cart_items: List[Dict[str, Any]]) -> float:
    """Calculate the total price of items in the cart."""
    total = 0.0
    for cart_item in cart_items:
        item = cart_item.get("item", {})
        quantity = cart_item.get("quantity", 1)
        price = item.get("price", 0)
        total += price * quantity
    return total
