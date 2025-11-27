from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import csv
from collections import defaultdict
from flask_cors import CORS
from itertools import combinations
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for purchases
PURCHASES = []
ORDERS = {}  # Store order totals: {order_id: {date, total, items}}

def parse_date(date_string: str) -> datetime:
    """Parse date string in YYYY-MM-DD format"""
    return datetime.strptime(date_string, "%Y-%m-%d")

def load_amazon_csv(file_path: str):
    """Load Amazon order history CSV and populate PURCHASES and ORDERS"""
    global PURCHASES, ORDERS
    
    PURCHASES = []
    ORDERS = {}
    order_items = defaultdict(list)
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        purchase_id = 1
        
        for row in reader:
            # Skip empty rows or subtotal rows
            if not row.get('order id') or row['order id'].startswith('='):
                continue
            
            order_id = row['order id']
            order_date = row['order date']
            
            # Parse price - handle empty prices (free items like Audible credits)
            price_str = row['price'].replace('$', '').strip()
            price = float(price_str) if price_str and price_str != '0' else 0.0
            
            # Create individual item purchase
            purchase = {
                'id': purchase_id,
                'order_id': order_id,
                'date': order_date,
                'amount': price,
                'description': row['description'][:100],  # Truncate long descriptions
                'item_url': row.get('item url', row.get('item_url', '')),
                'order_url': row['order url'],
                'asin': row['ASIN'],
                'quantity': int(row['quantity'])
            }
            
            PURCHASES.append(purchase)
            order_items[order_id].append(purchase)
            purchase_id += 1
        
        # Calculate order totals
        for order_id, items in order_items.items():
            if items:
                order_total = sum(item['amount'] for item in items)
                ORDERS[order_id] = {
                    'order_id': order_id,
                    'date': items[0]['date'],
                    'total': order_total,
                    'item_count': len(items),
                    'items': items,
                    'order_url': items[0]['order_url']
                }

def calculate_probability_score(items: List[Dict], target_date: str, target_amount: float) -> float:
    """
    Calculate probability score for a combination of items
    Since we only show EXACT amount matches, score is based on:
    - Date proximity (50% weight): How close the dates are to target date
    - Same order bonus (50% weight): Items from same order are much more likely
    """
    if not items:
        return 0.0
    
    target_dt = parse_date(target_date)
    total_amount = sum(item['amount'] for item in items)
    
    # Amount is always exact, so no amount score needed
    
    # Date proximity score (50% weight) - closer dates = higher score
    dates = [parse_date(item['date']) for item in items]
    avg_days_diff = sum(abs((d - target_dt).days) for d in dates) / len(dates)
    # Perfect score if within 1 day, decreases as days increase
    date_score = max(0, 1 - (avg_days_diff / 14)) * 50  # 14 days max range
    
    # Same order bonus (50% weight) - items from same order are MUCH more likely
    order_ids = set(item['order_id'] for item in items)
    same_order_score = 50 if len(order_ids) == 1 else 0
    
    total_score = date_score + same_order_score
    return round(total_score, 2)

def find_item_combinations(target_date: str, target_amount: float, days_range: int = 7, max_items: int = 5) -> List[Dict]:
    """
    Find combinations of items that add up to EXACTLY the target amount
    Returns combinations sorted by probability score
    """
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)
    
    # Filter items within date range
    candidates = []
    for purchase in PURCHASES:
        purchase_date = parse_date(purchase["date"])
        if start_date <= purchase_date <= end_date and purchase["amount"] > 0:
            candidates.append(purchase)
    
    if not candidates:
        return []
    
    # Sort by date proximity to target
    candidates.sort(key=lambda p: abs((parse_date(p['date']) - target_dt).days))
    
    # Limit candidates to prevent combinatorial explosion
    candidates = candidates[:50]  # Top 50 closest items
    
    matches = []
    
    # Try combinations of different sizes (1 to max_items)
    for combo_size in range(1, min(max_items + 1, len(candidates) + 1)):
        for combo in combinations(candidates, combo_size):
            total = sum(item['amount'] for item in combo)
            
            # CRITICAL: Must match EXACTLY (within 1 cent for floating point precision)
            if abs(total - target_amount) < 0.01:
                days_diffs = [(parse_date(item['date']) - target_dt).days for item in combo]
                avg_days_diff = sum(abs(d) for d in days_diffs) / len(days_diffs)
                
                probability = calculate_probability_score(list(combo), target_date, target_amount)
                
                matches.append({
                    'items': [
                        {
                            'id': item['id'],
                            'order_id': item['order_id'],
                            'date': item['date'],
                            'amount': item['amount'],
                            'description': item['description'],
                            'days_from_target': (parse_date(item['date']) - target_dt).days
                        }
                        for item in combo
                    ],
                    'total_amount': round(total, 2),
                    'item_count': len(combo),
                    'avg_days_from_target': round(avg_days_diff, 1),
                    'probability_score': probability,
                    'same_order': len(set(item['order_id'] for item in combo)) == 1,
                    'order_ids': list(set(item['order_id'] for item in combo)),
                    'search_type': 'combination'
                })
        
        # If we found good matches (>70 probability), no need to check larger combos
        if matches and max(m['probability_score'] for m in matches) > 70:
            break
    
    # Sort by probability score (highest first)
    matches.sort(key=lambda x: x['probability_score'], reverse=True)
    
    # Return top 10 matches
    return matches[:10]

def find_matching_items(target_date: str, target_amount: float, days_range: int = 7) -> List[Dict]:
    """Find individual items matching the amount within a date range"""
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)
    
    matching_items = []
    
    for purchase in PURCHASES:
        purchase_date = parse_date(purchase["date"])
        
        # Check if date is within range and amount matches
        if start_date <= purchase_date <= end_date and abs(purchase["amount"] - target_amount) < 0.01:
            days_diff = (purchase_date - target_dt).days
            
            matching_items.append({
                **purchase,
                "days_from_target": days_diff,
                "target_date": target_date,
                "search_type": "item"
            })
    
    return matching_items

def find_matching_orders(target_date: str, target_amount: float, days_range: int = 7) -> List[Dict]:
    """Find orders where the total matches the amount within a date range"""
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)
    
    matching_orders = []
    
    for order_id, order in ORDERS.items():
        order_date = parse_date(order["date"])
        
        # Check if date is within range and order total matches
        if start_date <= order_date <= end_date and abs(order["total"] - target_amount) < 0.01:
            days_diff = (order_date - target_dt).days
            
            matching_orders.append({
                **order,
                "days_from_target": days_diff,
                "target_date": target_date,
                "search_type": "order"
            })
    
    return matching_orders

@app.route('/api/purchases/import', methods=['POST'])
def import_amazon_csv():
    """Import Amazon order history CSV"""
    try:
        # Try to get file path from request, otherwise use default
        data = request.get_json() if request.is_json else {}
        csv_filename = data.get('filename', 'amazon_order_history.csv')
        
        # Look in csv/ folder
        possible_paths = [
            os.path.join('csv', csv_filename),
            csv_filename,  # Fallback to current directory
            os.path.join(os.path.dirname(__file__), 'csv', csv_filename),
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            return jsonify({
                "error": "CSV file not found",
                "checked_paths": possible_paths
            }), 404
        
        load_amazon_csv(csv_path)
        
        return jsonify({
            "message": "Amazon order history imported successfully",
            "file_path": csv_path,
            "total_items": len(PURCHASES),
            "total_orders": len(ORDERS),
            "date_range": {
                "earliest": min(p['date'] for p in PURCHASES) if PURCHASES else None,
                "latest": max(p['date'] for p in PURCHASES) if PURCHASES else None
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/purchases/search', methods=['GET'])
def search_purchases():
    """
    Search for purchases by date and amount
    
    Query Parameters:
        date (required): Target date in YYYY-MM-DD format
        amount (required): Dollar amount to search for
        days_range (optional): Number of days before/after to search (default: 7)
        search_type (optional): 'item', 'order', 'combination', or 'all' (default: 'all')
        max_combo_items (optional): Max items in combination (default: 5)
    
    Examples:
        /api/purchases/search?date=2025-10-29&amount=31.23&search_type=all
        /api/purchases/search?date=2025-10-29&amount=31.23&search_type=combination&max_combo_items=3
    """
    try:
        # Get query parameters
        target_date = request.args.get('date')
        target_amount = request.args.get('amount')
        days_range = request.args.get('days_range', 7, type=int)
        search_type = request.args.get('search_type', 'all').lower()
        max_combo_items = request.args.get('max_combo_items', 5, type=int)
        
        # Validate required parameters
        if not target_date:
            return jsonify({"error": "Missing required parameter: date (format: YYYY-MM-DD)"}), 400
        
        if not target_amount:
            return jsonify({"error": "Missing required parameter: amount"}), 400
        
        # Convert amount to float
        try:
            target_amount = float(target_amount)
        except ValueError:
            return jsonify({"error": "Invalid amount format. Must be a number."}), 400
        
        # Validate date format
        try:
            parse_date(target_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Validate search type
        if search_type not in ['item', 'order', 'combination', 'all']:
            return jsonify({"error": "Invalid search_type. Use 'item', 'order', 'combination', or 'all'"}), 400
        
        # Find matching purchases
        results = {
            "query": {
                "target_date": target_date,
                "target_amount": target_amount,
                "search_range_days": days_range,
                "search_type": search_type,
                "max_combo_items": max_combo_items
            },
            "item_matches": [],
            "order_matches": [],
            "combination_matches": []
        }
        
        if search_type in ['item', 'all']:
            results["item_matches"] = find_matching_items(target_date, target_amount, days_range)
        
        if search_type in ['order', 'all']:
            results["order_matches"] = find_matching_orders(target_date, target_amount, days_range)
        
        if search_type in ['combination', 'all']:
            results["combination_matches"] = find_item_combinations(target_date, target_amount, days_range, max_combo_items)
        
        results["total_matches"] = len(results["item_matches"]) + len(results["order_matches"]) + len(results["combination_matches"])
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order_details(order_id):
    """Get detailed information about a specific order"""
    if order_id not in ORDERS:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify(ORDERS[order_id])

@app.route('/api/purchases', methods=['GET'])
def get_all_purchases():
    """Get all purchases with optional filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    purchases = PURCHASES
    
    if start_date:
        start_dt = parse_date(start_date)
        purchases = [p for p in purchases if parse_date(p['date']) >= start_dt]
    
    if end_date:
        end_dt = parse_date(end_date)
        purchases = [p for p in purchases if parse_date(p['date']) <= end_dt]
    
    return jsonify({
        "total_count": len(purchases),
        "purchases": purchases
    })

@app.route('/api/orders', methods=['GET'])
def get_all_orders():
    """Get all orders"""
    return jsonify({
        "total_count": len(ORDERS),
        "orders": list(ORDERS.values())
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about loaded data"""
    if not PURCHASES:
        return jsonify({"error": "No data loaded. Please import Amazon CSV first."}), 400
    
    dates = [p['date'] for p in PURCHASES]
    amounts = [p['amount'] for p in PURCHASES]
    order_totals = [o['total'] for o in ORDERS.values()]
    
    return jsonify({
        "total_items": len(PURCHASES),
        "total_orders": len(ORDERS),
        "date_range": {
            "earliest": min(dates),
            "latest": max(dates)
        },
        "amount_stats": {
            "min_item": min(amounts),
            "max_item": max(amounts),
            "avg_item": sum(amounts) / len(amounts),
            "min_order": min(order_totals) if order_totals else 0,
            "max_order": max(order_totals) if order_totals else 0,
            "avg_order": sum(order_totals) / len(order_totals) if order_totals else 0
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "data_loaded": len(PURCHASES) > 0,
        "total_items": len(PURCHASES),
        "total_orders": len(ORDERS)
    })

if __name__ == '__main__':
    # Auto-load Amazon CSV on startup
    
    # Try multiple possible locations for CSV in csv/ folder
    csv_folder = 'csv'
    possible_files = ['amazon_order_history.csv', 'order_history.csv', 'orders.csv']
    
    loaded = False
    for filename in possible_files:
        possible_paths = [
            os.path.join(csv_folder, filename),
            os.path.join(os.path.dirname(__file__), csv_folder, filename),
        ]
        
        for csv_path in possible_paths:
            if os.path.exists(csv_path):
                try:
                    load_amazon_csv(csv_path)
                    print(f"✅ Loaded {len(PURCHASES)} items from {len(ORDERS)} orders")
                    print(f"📁 Data loaded from: {csv_path}")
                    loaded = True
                    break
                except Exception as e:
                    print(f"⚠️  Could not load CSV from {csv_path}: {e}")
        
        if loaded:
            break
    
    if not loaded:
        print(f"⚠️  No CSV file found. Place 'amazon_order_history.csv' in the 'csv/' folder.")
        print(f"   Create a 'csv' folder in the same directory as this script.")
    
    print(f"\n🚀 Starting API server on port 4333...")
    app.run(debug=True, host='0.0.0.0', port=4333)