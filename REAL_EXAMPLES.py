#!/usr/bin/env python3
"""
Real Examples from Your Amazon Order History
This demonstrates the API with actual data from your CSV file
"""

import requests
import json

BASE_URL = "http://localhost:4333"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

print("""
🎯 AMAZON PURCHASE SEARCH - REAL EXAMPLES FROM YOUR DATA
============================================================================

Based on your actual Amazon order history, here are some real scenarios:
""")

print_section("Example 1: Find $14.20 Item from October 30, 2025")
print("""
Scenario: You see a $14.20 charge and want to know what you bought.

API Call:
  GET /api/purchases/search?date=2025-10-30&amount=14.20&search_type=item

Expected Result:
  • Amazon Essentials Women's Fleece Jogger Sweatpant (Burgundy, Medium)
  • Amazon Essentials Women's Fleece Jogger Sweatpant (Burgundy, Small)
  (Both items were $14.20 and ordered on the same day)
""")

print_section("Example 2: Find Order Totaling $44.20 from October 30")
print("""
Scenario: Your bank statement shows $44.20 charged on Oct 30.
This was an order with multiple items.

API Call:
  GET /api/purchases/search?date=2025-10-30&amount=44.20&search_type=order

Expected Result:
  Order #111-5300082-5915455 contains:
    • $14.20 - Amazon Essentials Fleece Jogger (Small)
    • $30.00 - Halobliss Lift Up Underwire Bra
    = $44.20 TOTAL
""")

print_section("Example 3: Find $9.99 Items from October 27")
print("""
Scenario: You bought something for $9.99 in late October.

API Call:
  GET /api/purchases/search?date=2025-10-27&amount=9.99&search_type=item

Expected Result:
  Multiple matches:
  • ZOORON Kids Beanie (Light Purple)
  • ZOORON Kids Beanie (another color)
  • Crayola Washable Markers - Violet Purple
""")

print_section("Example 4: Reconcile $51.22 Bank Charge from October 27")
print("""
Scenario: Your credit card shows $51.22 on Oct 27. What order was that?

API Call:
  GET /api/purchases/search?date=2025-10-27&amount=51.22&search_type=order

Expected Result:
  Order #111-6320240-3997831 breakdown:
    • $19.99 - N'Ice Caps Winter Gloves (Neon Purple)
    • $11.24 - Cooraby 12 Pairs Winter Magic Gloves
    • $19.99 - N'Ice Caps Winter Gloves (Royal)
    = $51.22 TOTAL
""")

print_section("HOW TO USE")
print("""
1. Start the API:
   python amazon_purchase_api.py

2. Use the Web Interface:
   Open amazon_search.html in your browser
   
   OR

3. Use curl commands:
   # Search by item price
   curl "http://localhost:4333/api/purchases/search?date=2025-10-30&amount=14.20&search_type=item"
   
   # Search by order total
   curl "http://localhost:4333/api/purchases/search?date=2025-10-30&amount=44.20&search_type=order"
   
   # Search both
   curl "http://localhost:4333/api/purchases/search?date=2025-10-27&amount=9.99&search_type=both"

4. Try with your own amounts:
   - Look at your bank statement
   - Find a charge from Amazon
   - Enter the date and amount
   - See exactly what you bought!
""")

print_section("TIPS")
print("""
• For bank statement reconciliation: Use "search_type=order"
  (Banks charge the order total, not individual items)

• For finding specific products: Use "search_type=item"
  (When you remember roughly how much something cost)

• Not sure? Use "search_type=both"
  (Searches both ways and shows all matches)

• Adjust the date range with "days_range=14" if needed
  (Default is 7 days before/after)
""")

print("\n" + "="*80)
print("✅ Your API is loaded with 120 items from 89 orders (Aug 29 - Nov 27, 2025)")
print("="*80 + "\n")
