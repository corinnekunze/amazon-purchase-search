# 🚀 QUICK START GUIDE

## Your Amazon Purchase Search API is Ready!

### ✅ What You Have

- **120 items** from **89 orders** (Aug 29 - Nov 27, 2025)
- API that searches by **item price** OR **order total**
- Beautiful web interface with color-coded results

---

## 📦 Files You Need

1. **amazon_purchase_api.py** - The API server
2. **amazon_search.html** - Web interface (easiest to use!)
3. **amazon_order_history.csv** - Your data (already uploaded)

---

## 🎯 3-Step Setup

### Step 1: Install Flask

```bash
pip install flask
```

### Step 2: Start the API

```bash
python amazon_purchase_api.py
```

You should see:

```
✅ Loaded 120 items from 89 orders
 * Running on http://127.0.0.1:4333
```

### Step 3: Open the Web Interface

Open `amazon_search.html` in your web browser

---

## 💡 How to Use

### Example: "What was that $31.23 charge on October 29?"

**In the Web Interface:**

1. Date: `2025-10-29`
2. Amount: `31.23`
3. Search Type: `Both`
4. Click **Search Purchases**

**Result:** Shows any items OR orders matching $31.23 near that date!

---

## 🔍 Search Modes Explained

### 🛍️ By Item

Find individual products matching the price

- Use when: "I bought something for about $15..."

### 📦 By Order Total

Find orders where the total matches (best for bank statements)

- Use when: "My card was charged $44.20..."

### 🔄 Both

Searches items AND order totals (recommended!)

---

## 📊 Real Examples From Your Data

### Example 1: $14.20 on Oct 30

**Result:** 2 Amazon Essentials Fleece Joggers (you bought 2!)

### Example 2: $44.20 on Oct 30

**Result:** Order with Jogger ($14.20) + Bra ($30.00) = $44.20

### Example 3: $51.22 on Oct 27

**Result:** Order with 3 items (gloves for the kids!)

---

## 🎨 Web Interface Features

- **Color-coded date differences:**

  - 🟠 Orange = Before target date
  - 🟢 Green = After target date
  - 🔵 Blue = Same day

- **Expandable order details** - Click to see all items in an order

- **Direct Amazon links** - Click to view on Amazon.com

---

## 🐛 Troubleshooting

**"Connection refused"**
→ Make sure the API is running: `python amazon_purchase_api.py`

**"No matches found"**
→ Try increasing the date range to 14 days
→ Check if you have the exact amount right

**Wrong results?**
→ Remember Amazon may charge tax separately
→ Try searching by individual item price instead

---

## 🎯 Your Question Answered

> "I want to say: $31.23 October 29, 2025 and have it find matching products"

**YES!** This API does exactly that:

- Searches **7 days** before/after Oct 29 (adjustable)
- Finds **all items** priced at $31.23
- Finds **all orders** totaling $31.23
- Shows how many days away from Oct 29 each match is

---

## 📞 Next Steps

1. **Start the API** - Run `python amazon_purchase_api.py`
2. **Open the web interface** - Double-click `amazon_search.html`
3. **Try the examples** - Search for $14.20, $44.20, or $51.22 on Oct 27-30
4. **Use with your bank statement** - Enter any Amazon charge to find it!

---

## 🎉 You're All Set!

The API is pre-loaded with your Amazon data. Just start it up and search!

**Quick test:**

```bash
curl "http://localhost:4333/api/stats"
```

Should show your 120 items and 89 orders.

Happy searching! 🔍
