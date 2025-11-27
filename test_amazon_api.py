#!/usr/bin/env python3
"""
Test script for Amazon Purchase Search API
Demonstrates searching by item price and order total
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:4333"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_table(headers, rows):
    """Print a formatted table"""
    col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    
    def print_row(row):
        print(" | ".join(str(item).ljust(width) for item, width in zip(row, col_widths)))
    
    print_row(headers)
    print("-" * sum(col_widths + [3 * (len(headers) - 1)]))
    for row in rows:
        print_row(row)

def test_import():
    print_section("Import Amazon CSV")
    response = requests.post(f"{BASE_URL}/api/purchases/import")
    data = response.json()
    print(json.dumps(data, indent=2))
    return data

def test_stats():
    print_section("Database Statistics")
    response = requests.get(f"{BASE_URL}/api/stats")
    data = response.json()
    print(json.dumps(data, indent=2))

def test_search_by_item(date, amount):
    print_section(f"Search by Item Price: ${amount} on {date}")
    response = requests.get(
        f"{BASE_URL}/api/purchases/search",
        params={
            "date": date,
            "amount": amount,
            "search_type": "item"
        }
    )
    data = response.json()
    
    print(f"\n📊 Query: {data['query']}")
    print(f"✅ Found {len(data['item_matches'])} matching items\n")
    
    if data['item_matches']:
        headers = ["Order ID", "Date", "Amount", "Days Diff", "Description"]
        rows = []
        for item in data['item_matches']:
            rows.append([
                item['order_id'][:15] + "...",
                item['date'],
                f"${item['amount']:.2f}",
                f"{item['days_from_target']:+d}",
                item['description'][:40] + "..."
            ])
        print_table(headers, rows)
    
    return data

def test_search_by_order(date, amount):
    print_section(f"Search by Order Total: ${amount} on {date}")
    response = requests.get(
        f"{BASE_URL}/api/purchases/search",
        params={
            "date": date,
            "amount": amount,
            "search_type": "order"
        }
    )
    data = response.json()
    
    print(f"\n📊 Query: {data['query']}")
    print(f"✅ Found {len(data['order_matches'])} matching orders\n")
    
    if data['order_matches']:
        for order in data['order_matches']:
            print(f"\n📦 Order: {order['order_id']}")
            print(f"   Date: {order['date']}")
            print(f"   Total: ${order['total']:.2f}")
            print(f"   Days from target: {order['days_from_target']:+d}")
            print(f"   Items ({order['item_count']}):")
            for item in order['items']:
                print(f"      • ${item['amount']:.2f} - {item['description'][:50]}")
    
    return data

def test_search_both(date, amount):
    print_section(f"Search Both: ${amount} on {date}")
    response = requests.get(
        f"{BASE_URL}/api/purchases/search",
        params={
            "date": date,
            "amount": amount,
            "search_type": "both"
        }
    )
    data = response.json()
    
    print(f"\n📊 Query: {data['query']}")
    print(f"✅ Total matches: {data['total_matches']}")
    print(f"   • Item matches: {len(data['item_matches'])}")
    print(f"   • Order matches: {len(data['order_matches'])}\n")
    
    return data

def find_example_searches(stats):
    """Find some good example searches from the data"""
    print_section("Finding Example Searches")
    
    # Get some orders
    response = requests.get(f"{BASE_URL}/api/orders")
    orders = response.json()['orders']
    
    if len(orders) >= 2:
        example1 = orders[0]
        example2 = orders[1]
        
        print(f"\n📌 Example 1 - Order Total Search:")
        print(f"   Date: {example1['date']}")
        print(f"   Amount: ${example1['total']:.2f}")
        print(f"   Command: Search for ${example1['total']:.2f} on {example1['date']}")
        
        print(f"\n📌 Example 2 - Order Total Search:")
        print(f"   Date: {example2['date']}")
        print(f"   Amount: ${example2['total']:.2f}")
        print(f"   Command: Search for ${example2['total']:.2f} on {example2['date']}")
        
        return example1, example2
    
    return None, None

def main():
    print("\n🚀 Amazon Purchase Search API Test Suite")
    print("Make sure the API server is running on http://localhost:4333\n")
    
    try:
        # Import data
        import_result = test_import()
        
        # Show stats
        stats = test_stats()
        
        # Find example searches
        ex1, ex2 = find_example_searches(stats)
        
        # Example 1: Search by item price
        print("\n" + "🔍 EXAMPLE SEARCHES".center(70, "="))
        test_search_by_item("2025-11-26", 7.99)
        
        # Example 2: Search by order total
        if ex1:
            test_search_by_order(ex1['date'], ex1['total'])
        
        # Example 3: Search both
        test_search_both("2025-11-27", 25.63)
        
        print("\n" + "="*70)
        print("✅ All tests completed!")
        print("="*70)
        
        print("\n💡 Try these searches in the web interface:")
        print(f"   • Open amazon_search.html in your browser")
        print(f"   • Search for $7.99 on 2025-11-26 (multiple items)")
        if ex1:
            print(f"   • Search for ${ex1['total']:.2f} on {ex1['date']} (order total)")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("Please start the API server first with: python amazon_purchase_api.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
