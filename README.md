# Amazon Purchase Search

A hobby project for cross-referencing Amazon purchases with dollar amounts to help itemize Amazon transactions in budgeting software like YNAB (You Need A Budget).

## About

This tool was generated using [Claude Code](https://claude.com/claude-code) to solve a common budgeting problem: when you see a charge from Amazon on your credit card statement, it's often difficult to figure out which specific items or orders that charge corresponds to. This app allows you to upload your Amazon order history and search by date and amount to identify the exact purchases.

## Features

- Upload Amazon order history CSV files
- Search for purchases by date and amount
- Multiple search modes:
  - **Individual items** - Find single items matching the amount
  - **Complete orders** - Find orders matching the total amount
  - **Combinations** - Find combinations of items from the same timeframe that add up to the amount
- Probability scoring to rank match likelihood
- Adjustable date range for flexible searching

## Use Case

Perfect for users of budgeting software like YNAB who want to:

- Categorize Amazon purchases accurately
- Split Amazon orders into proper budget categories
- Track what specific items were purchased in a given transaction
- Reconcile credit card statements with Amazon order history

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd amazon-purchases
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements_deploy.txt
```

3. Run the application:

```bash
python app.py
```

4. Open your browser to `http://localhost:4333`

### Getting Your Amazon Order History

#### Recommended Method: Browser Extension (Fast)

1. Install the [Amazon Order History Reporter](https://chromewebstore.google.com/detail/amazon-order-history-repo/mgkilgclilajckgnedgjgnfdokkgnibi) Chrome extension
2. Go to your [Amazon Order History](https://www.amazon.com/gp/your-account/order-history) page
3. Click the extension icon and select "Get Report"
4. Choose the past 3 months (or your desired timeframe)
5. Download the generated CSV file
6. Upload it to this app

This method is instant, unlike Amazon's official order reports which can take hours or days to generate.

#### Alternative Method: Official Amazon Reports (Slow)

1. Go to Amazon → Your Account → Download order reports
2. Request a report with columns: `order id`, `order date`, `price`, `description`, `item url`, `order url`, `ASIN`, `quantity`
3. Wait for Amazon to email you the report (can take several hours to days)
4. Download the CSV file
5. Upload it to the app

## How It Works

1. **Upload** your Amazon order history CSV
2. **Search** by entering a date and dollar amount from your bank statement
3. **Review** the matches, ranked by probability
4. **Identify** which specific items or orders correspond to your bank charge

The app provides three types of matches:

- Single items that match the amount
- Complete orders that match the total
- Combinations of items purchased around the same time that add up to the amount

## Deployment

This app is configured for deployment on [Render](https://render.com). Simply connect your GitHub repository to Render and it will automatically deploy using the included `render.yaml` configuration.

**Note:** The app uses in-memory storage, so uploaded data will be cleared when the server restarts. This is intentional for privacy - your Amazon purchase history is never persisted to disk.

## Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** Vanilla JavaScript with modern CSS
- **Deployment:** Gunicorn + Render
- **Template Engine:** Jinja2

## Development

Run tests - SEE [README](/tests/README.md)

## Privacy

All data is stored in memory only and is never written to disk or shared externally. When you close the app or it restarts, all uploaded data is cleared.

## License

This is a hobby project - feel free to use, modify, and distribute as needed.

## Credits

Generated with [Claude Code](https://claude.com/claude-code) - an AI-powered coding assistant by Anthropic.
