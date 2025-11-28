"""
Test script for Food Ordering Agent database functions
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import database

def test_catalog_loading():
    """Test catalog loading"""
    print("=" * 50)
    print("TEST 1: Load Catalog")
    print("=" * 50)
    
    catalog = database.load_catalog()
    categories = catalog.get("categories", {})
    recipes = catalog.get("recipes", {})
    
    total_items = sum(len(items) for items in categories.values())
    
    print(f"✓ Loaded {len(categories)} categories")
    print(f"✓ Total items: {total_items}")
    print(f"✓ Recipes available: {len(recipes)}")
    
    for category_name, items in categories.items():
        print(f"  - {category_name}: {len(items)} items")
    
    print()

def test_item_search():
    """Test item search functions"""
    print("=" * 50)
    print("TEST 2: Item Search")
    print("=" * 50)
    
    # Test exact name search
    bread = database.get_item_by_name("Whole Wheat Bread")
    if bread:
        print(f"✓ Found by exact name: {bread['name']} - ₹{bread['price']}")
    
    # Test partial name search
    milk = database.get_item_by_name("milk")
    if milk:
        print(f"✓ Found by partial name: {milk['name']} - ₹{milk['price']}")
    
    # Test search by query
    chocolate_items = database.search_items("chocolate")
    print(f"✓ Search 'chocolate': Found {len(chocolate_items)} items")
    for item in chocolate_items:
        print(f"  - {item['name']} (₹{item['price']})")
    
    print()

def test_recipe_lookup():
    """Test recipe item lookup"""
    print("=" * 50)
    print("TEST 3: Recipe Lookup")
    print("=" * 50)
    
    recipes_to_test = [
        "peanut butter sandwich",
        "pasta",
        "breakfast"
    ]
    
    for recipe_name in recipes_to_test:
        recipe_data = database.get_recipe_items(recipe_name)
        if recipe_data:
            items = recipe_data.get("items", [])
            print(f"✓ Recipe '{recipe_data['recipe_name']}':")
            for item in items:
                print(f"  - {item['name']} (₹{item['price']})")
        else:
            print(f"✗ Recipe '{recipe_name}' not found")
    
    print()

def test_cart_calculation():
    """Test cart total calculation"""
    print("=" * 50)
    print("TEST 4: Cart Calculation")
    print("=" * 50)
    
    # Create a mock cart
    bread = database.get_item_by_id("grocery_001")
    peanut_butter = database.get_item_by_id("grocery_005")
    milk = database.get_item_by_id("grocery_003")
    
    cart = [
        {"item": bread, "quantity": 2},
        {"item": peanut_butter, "quantity": 1},
        {"item": milk, "quantity": 3}
    ]
    
    total = database.calculate_cart_total(cart)
    
    print("Cart contents:")
    for cart_item in cart:
        item = cart_item["item"]
        qty = cart_item["quantity"]
        subtotal = item["price"] * qty
        print(f"  - {item['name']} x {qty} = ₹{subtotal}")
    
    print(f"\n✓ Total: ₹{total:.2f}")
    print()

def test_order_saving():
    """Test order saving"""
    print("=" * 50)
    print("TEST 5: Order Persistence")
    print("=" * 50)
    
    # Create a test order
    bread = database.get_item_by_id("grocery_001")
    milk = database.get_item_by_id("grocery_003")
    
    order_items = [
        {
            "item_id": bread["id"],
            "name": bread["name"],
            "brand": bread["brand"],
            "quantity": 2,
            "unit_price": bread["price"],
            "subtotal": bread["price"] * 2
        },
        {
            "item_id": milk["id"],
            "name": milk["name"],
            "brand": milk["brand"],
            "quantity": 1,
            "unit_price": milk["price"],
            "subtotal": milk["price"]
        }
    ]
    
    test_order = {
        "customer_name": "Test User",
        "delivery_address": "123 Test Street",
        "items": order_items,
        "total": 150.0,
        "status": "placed"
    }
    
    order_id = database.save_order(test_order)
    print(f"✓ Order saved with ID: {order_id}")
    
    # Verify order was saved
    all_orders = database.get_all_orders()
    print(f"✓ Total orders in database: {len(all_orders)}")
    
    print()

def main():
    print("\n" + "=" * 50)
    print("FOOD ORDERING AGENT - DATABASE TESTS")
    print("=" * 50 + "\n")
    
    try:
        test_catalog_loading()
        test_item_search()
        test_recipe_lookup()
        test_cart_calculation()
        test_order_saving()
        
        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
