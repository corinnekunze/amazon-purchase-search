# Amazon Purchase Search API

A Flask REST API for searching Amazon purchases by date and dollar amount. Search by individual item prices OR by order totals!

## 🎯 Key Features

- **Dual Search Modes:**

  - 🛍️ **By Item Price**: Find individual items matching an exact price (e.g., $31.23)
  - 📦 **By Order Total**: Find orders where the total matches your bank statement charge
  - 🔄 **Both**: Search for matches in both modes simultaneously

- **Date Range Search**: Find purchases within ±7 days (configurable) of any date
- **Amazon CSV Import**: Auto-loads your Amazon order history
- **Order Details**: View complete order breakdowns with all items
- **Beautiful Web Interface**: Interactive table display with color-coded date differences

## 📊 Use Cases

### Example 1: Reconcile Bank Statement

You see a charge for **$103.90** on **October 29, 2025** on your bank statement:

```
Search by Order Total: $103.90 on 2025-10-29
→ Finds the Amazon order with that exact total
→ Shows all items in that order
```

### Example 2: Find Specific Product

You remember buying something for **$31.23** around **October 29, 2025**:

```
Search by Item: $31.23 on 2025-10-29
→ Finds all items with that exact price within the date range
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install flask
```

### 2. Place Your Amazon CSV

Put your `amazon_order_history.csv` file in the `/mnt/user-data/uploads/` directory

### 3. Run the API

```bash
python amazon_purchase_api.py
```

The API will auto-load your Amazon data on startup and display:

```
✅ Loaded 120 items from 85 orders
```

### 4. Use the Web Interface

Open `amazon_search.html` in your browser for an interactive search experience!

## 📖 API Documentation

### Base URL

```
http://localhost:4333
```

### Endpoints

#### 1. Import Amazon CSV

**POST** `/api/purchases/import`

Manually trigger import of Amazon order history.

**Response:**

```json
{
  "message": "Amazon order history imported successfully",
  "total_items": 120,
  "total_orders": 85,
  "date_range": {
    "earliest": "2025-08-29",
    "latest": "2025-11-27"
  }
}
```

#### 2. Search Purchases

**GET** `/api/purchases/search`

Search for purchases by date and amount.

**Parameters:**

- `date` (required): Target date in YYYY-MM-DD format
- `amount` (required): Dollar amount to search for
- `days_range` (optional): Number of days before/after to search (default: 7)
- `search_type` (optional): `'item'`, `'order'`, or `'both'` (default: `'both'`)

**Examples:**

Search by item price:

```bash
curl "http://localhost:4333/api/purchases/search?date=2025-10-29&amount=31.23&search_type=item"
```

Search by order total:

```bash
curl "http://localhost:4333/api/purchases/search?date=2025-10-29&amount=103.90&search_type=order"
```

Search both:

```bash
curl "http://localhost:4333/api/purchases/search?date=2025-10-29&amount=31.23&search_type=both"
```

**Response:**

```json
{
  "query": {
    "target_date": "2025-10-29",
    "target_amount": 31.23,
    "search_range_days": 7,
    "search_type": "both"
  },
  "total_matches": 3,
  "item_matches": [
    {
      "id": 42,
      "order_id": "111-2345678-9012345",
      "date": "2025-10-27",
      "amount": 31.23,
      "description": "Product Name Here",
      "days_from_target": -2,
      "item_url": "https://amazon.com/...",
      "order_url": "https://amazon.com/..."
    }
  ],
  "order_matches": [
    {
      "order_id": "111-9876543-2109876",
      "date": "2025-10-29",
      "total": 31.23,
      "item_count": 2,
      "days_from_target": 0,
      "items": [
        {
          "amount": 15.99,
          "description": "Item 1"
        },
        {
          "amount": 15.24,
          "description": "Item 2"
        }
      ]
    }
  ]
}
```

#### 3. Get Order Details

**GET** `/api/orders/<order_id>`

Get detailed information about a specific order.

**Example:**

```bash
curl "http://localhost:4333/api/orders/111-2345678-9012345"
```

#### 4. Get All Purchases

**GET** `/api/purchases`

Get all purchases with optional date filtering.

**Parameters:**

- `start_date` (optional): Filter purchases after this date
- `end_date` (optional): Filter purchases before this date

**Example:**

```bash
curl "http://localhost:4333/api/purchases?start_date=2025-11-01&end_date=2025-11-30"
```

#### 5. Get All Orders

**GET** `/api/orders`

Get summary of all orders.

**Example:**

```bash
curl "http://localhost:4333/api/orders"
```

#### 6. Get Statistics

**GET** `/api/stats`

Get statistics about loaded purchase data.

**Response:**

```json
{
  "total_items": 120,
  "total_orders": 85,
  "date_range": {
    "earliest": "2025-08-29",
    "latest": "2025-11-27"
  },
  "amount_stats": {
    "min_item": 0.0,
    "max_item": 47.99,
    "avg_item": 18.45,
    "min_order": 7.64,
    "max_order": 103.9,
    "avg_order": 32.18
  }
}
```

#### 7. Health Check

**GET** `/api/health`

Check API status and data load status.

## 🖥️ Web Interface Guide

The `amazon_search.html` interface provides:

1. **Date Picker**: Select the target date from bank statement
2. **Amount Input**: Enter the dollar amount (e.g., 31.23)
3. **Search Range**: Days before/after to search (default: 7)
4. **Search Type Radio Buttons**:
   - **Both**: Recommended for most searches
   - **By Item Price**: When looking for specific products
   - **By Order Total**: When reconciling bank statements

### Search Results Display:

- **Order Total Matches**: Shows complete orders with expandable item lists
- **Individual Item Matches**: Shows specific products matching the price
- **Color-coded date indicators**:
  - 🟠 Orange: Days before target date
  - 🟢 Green: Days after target date
  - 🔵 Blue: Same day as target date

## 📝 Amazon CSV Format

Your Amazon order history CSV should have these columns:

- `order id`: Unique order identifier
- `order date`: Date in YYYY-MM-DD format
- `quantity`: Number of items
- `description`: Product description
- `price`: Dollar amount (e.g., $31.23)
- `item url`: Link to product page
- `order url`: Link to order details
- `ASIN`: Amazon product identifier

### How to Get Your Amazon CSV

1. Go to Amazon.com → **Returns & Orders**
2. Look for **"Download Order Reports"** or **"Order History Reports"**
3. Select date range and download as CSV
4. Place file at `/mnt/user-data/uploads/amazon_order_history.csv`

## 🧪 Testing

Run the test suite:

```bash
python test_amazon_api.py
```

This will:

- Import your Amazon data
- Display statistics
- Run example searches
- Show results in formatted tables

## 💡 Tips

1. **Bank Statement Reconciliation**: Use "By Order Total" mode with the exact charge amount
2. **Finding Products**: Use "By Item" mode with the product price
3. **Date Uncertainty**: Increase the `days_range` if you're not sure of the exact date
4. **Multiple Matches**: When you get multiple results, use the description and date to identify the correct one

## 🔧 Customization

### Connect to a Database

Replace the in-memory storage with SQLite or PostgreSQL:

```python
import sqlite3

def load_amazon_csv(file_path: str):
    conn = sqlite3.connect('purchases.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY,
            order_id TEXT,
            date TEXT,
            amount REAL,
            description TEXT
        )
    ''')

    # Insert data...
    conn.commit()
    conn.close()
```

### Add Authentication

Protect your API with API keys:

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get('X-API-Key') != 'your-secret-key':
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

## 🐛 Troubleshooting

**Problem**: API says "No data loaded"

- **Solution**: Make sure `amazon_order_history.csv` is in the uploads folder

**Problem**: Can't find order total match

- **Solution**: Amazon may charge tax/shipping separately. Try "By Item" search instead

**Problem**: Too many results

- **Solution**: Reduce the `days_range` parameter to narrow the search window

## 📄 Files Included

- `amazon_purchase_api.py` - Main Flask API server
- `amazon_search.html` - Web interface
- `test_amazon_api.py` - Test suite
- `requirements.txt` - Python dependencies
- `README.md` - This file

## 🎉 Example Workflow

1. Check bank statement: **$103.90 charged on October 29, 2025**
2. Open `amazon_search.html`
3. Enter:
   - Date: `2025-10-29`
   - Amount: `103.90`
   - Search Type: `By Order Total`
4. Click **Search Purchases**
5. View matching order with complete item breakdown
6. Click **View on Amazon** to see full order details

## 📜 License

MIT
