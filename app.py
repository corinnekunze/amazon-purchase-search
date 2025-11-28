from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
from typing import List, Dict
import csv
from collections import defaultdict
from flask_cors import CORS
from itertools import combinations
import os
import io

app = Flask(__name__)
CORS(app)

# In-memory storage
PURCHASES = []
ORDERS = {}

def parse_date(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%d")

def load_amazon_csv_from_string(csv_content: str):
    global PURCHASES, ORDERS
    
    PURCHASES = []
    ORDERS = {}
    order_items = defaultdict(list)
    
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    purchase_id = 1
    
    rows_processed = 0
    rows_skipped = 0
    
    for row in reader:
        rows_processed += 1
        
        # Skip empty rows or subtotal rows
        if not row.get('order id') or row['order id'].startswith('='):
            rows_skipped += 1
            continue
        
        try:
            order_id = row['order id']
            order_date = row['order date']
            
            # Parse price - handle empty prices
            price_str = row['price'].replace('$', '').strip()
            price = round(float(price_str), 2) if price_str and price_str != '0' else 0.0
            
            # Get description - handle missing column
            description = row.get('description', '')[:100]
            
            # Get URLs - handle both possible column names
            item_url = row.get('item url', row.get('item_url', ''))
            order_url = row.get('order url', row.get('order_url', ''))
            
            # Get ASIN
            asin = row.get('ASIN', '')
            
            # Get quantity
            quantity_str = row.get('quantity', '1')
            quantity = int(quantity_str) if quantity_str else 1
            
            purchase = {
                'id': purchase_id,
                'order_id': order_id,
                'date': order_date,
                'amount': price,
                'description': description,
                'item_url': item_url,
                'order_url': order_url,
                'asin': asin,
                'quantity': quantity
            }
            
            PURCHASES.append(purchase)
            order_items[order_id].append(purchase)
            purchase_id += 1
            
        except Exception as e:
            print(f"Error processing row {rows_processed}: {e}")
            print(f"Row data: {row}")
            rows_skipped += 1
            continue
    
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
    
    print(f"CSV Processing Summary:")
    print(f"  Total rows processed: {rows_processed}")
    print(f"  Rows skipped: {rows_skipped}")
    print(f"  Items loaded: {len(PURCHASES)}")
    print(f"  Orders created: {len(ORDERS)}")

def calculate_probability_score(items: List[Dict], target_date: str, target_amount: float) -> float:
    if not items:
        return 0.0
    
    target_dt = parse_date(target_date)
    
    dates = [parse_date(item['date']) for item in items]
    avg_days_diff = sum(abs((d - target_dt).days) for d in dates) / len(dates)
    date_score = max(0, 1 - (avg_days_diff / 14)) * 50
    
    order_ids = set(item['order_id'] for item in items)
    same_order_score = 50 if len(order_ids) == 1 else 0
    
    return round(date_score + same_order_score, 2)

def find_item_combinations(target_date: str, target_amount: float, days_range: int = 7, max_items: int = 5) -> List[Dict]:
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)
    
    candidates = []
    for purchase in PURCHASES:
        purchase_date = parse_date(purchase["date"])
        if start_date <= purchase_date <= end_date and purchase["amount"] > 0:
            candidates.append(purchase)
    
    if not candidates:
        return []
    
    candidates.sort(key=lambda p: abs((parse_date(p['date']) - target_dt).days))
    candidates = candidates[:50]
    
    matches = []
    
    for combo_size in range(1, min(max_items + 1, len(candidates) + 1)):
        for combo in combinations(candidates, combo_size):
            total = sum(item['amount'] for item in combo)
            
            if abs(total - target_amount) == 0:
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
        
        if matches and max(m['probability_score'] for m in matches) > 70:
            break
    
    matches.sort(key=lambda x: x['probability_score'], reverse=True)
    return matches[:10]

def find_matching_items(target_date: str, target_amount: float, days_range: int = 7) -> List[Dict]:
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)

    # Round target amount to 2 decimal places for consistent comparison
    target_amount = round(target_amount, 2)

    matching_items = []

    for purchase in PURCHASES:
        purchase_date = parse_date(purchase["date"])

        # Round purchase amount to 2 decimal places for consistent comparison
        purchase_amount = round(purchase["amount"], 2)

        if start_date <= purchase_date <= end_date and purchase_amount == target_amount:
            days_diff = (purchase_date - target_dt).days

            matching_items.append({
                **purchase,
                "days_from_target": days_diff,
                "target_date": target_date,
                "search_type": "item"
            })

    return matching_items

def find_matching_orders(target_date: str, target_amount: float, days_range: int = 7) -> List[Dict]:
    target_dt = parse_date(target_date)
    start_date = target_dt - timedelta(days=days_range)
    end_date = target_dt + timedelta(days=days_range)

    # Round target amount to 2 decimal places for consistent comparison
    target_amount = round(target_amount, 2)

    matching_orders = []

    for order_id, order in ORDERS.items():
        order_date = parse_date(order["date"])

        # Round order total to 2 decimal places for consistent comparison
        order_total = round(order["total"], 2)

        if start_date <= order_date <= end_date and order_total == target_amount:
            days_diff = (order_date - target_dt).days

            matching_orders.append({
                **order,
                "days_from_target": days_diff,
                "target_date": target_date,
                "search_type": "order"
            })

    return matching_orders

# Routes
@app.route('/')
def index():
    """Serve the main page from templates/index.html"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    """Handle CSV file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400
        
        # Read file content - try different encodings
        try:
            csv_content = file.read().decode('utf-8-sig')  # Handles BOM
        except UnicodeDecodeError:
            file.seek(0)
            csv_content = file.read().decode('latin-1')  # Fallback
        
        # Remove BOM if present
        if csv_content.startswith('\ufeff'):
            csv_content = csv_content[1:]
        
        # Check if file is empty
        if not csv_content.strip():
            return jsonify({"error": "CSV file is empty"}), 400
        
        # Load the CSV
        load_amazon_csv_from_string(csv_content)
        
        if len(PURCHASES) == 0:
            return jsonify({
                "error": "No valid data found in CSV. Please check the file format.",
                "hint": "Make sure your CSV has columns: order id, order date, price, description, etc."
            }), 400
        
        return jsonify({
            "message": "CSV uploaded successfully",
            "total_items": len(PURCHASES),
            "total_orders": len(ORDERS),
            "date_range": {
                "earliest": min(p['date'] for p in PURCHASES) if PURCHASES else None,
                "latest": max(p['date'] for p in PURCHASES) if PURCHASES else None
            }
        })
    
    except Exception as e:
        import traceback
        print("Upload error:")
        print(traceback.format_exc())
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/api/purchases/search', methods=['GET'])
def search_purchases():
    """Search for purchases"""
    try:
        target_date = request.args.get('date')
        target_amount = request.args.get('amount')
        days_range = request.args.get('days_range', 7, type=int)
        search_type = request.args.get('search_type', 'all').lower()
        max_combo_items = request.args.get('max_combo_items', 5, type=int)
        
        if not target_date or not target_amount:
            return jsonify({"error": "Missing parameters"}), 400
        
        target_amount = float(target_amount)
        parse_date(target_date)
        
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
    port = int(os.environ.get('PORT', 4333))
    app.run(host='0.0.0.0', port=port, debug=True)