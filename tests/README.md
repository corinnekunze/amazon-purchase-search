# Amazon Purchases Tests

This directory contains tests for the Amazon Purchase Search application.

## Python Tests

### Running Python Tests

#### Run all Python tests
```bash
pytest
```

#### Run with verbose output
```bash
pytest -v
```

#### Run specific test file
```bash
pytest tests/test_search.py
```

#### Run specific test class
```bash
pytest tests/test_search.py::TestItemSearch
```

#### Run specific test
```bash
pytest tests/test_search.py::TestItemSearch::test_find_exact_price_match_36_65
```

### Adding New Python Tests

1. Create a new test file named `test_*.py`
2. Use pytest fixtures for reusable test data
3. Use `@pytest.mark.parametrize` for testing multiple inputs
4. Follow the existing test structure and naming conventions

## JavaScript/UI Tests

### Setup

Install the required Node.js dependencies:

```bash
npm install
```

### Running JavaScript Tests

#### Run all tests
```bash
npm test
```

#### Run tests in watch mode (for development)
```bash
npm run test:watch
```

#### Run tests with coverage report
```bash
npm run test:coverage
```

### JavaScript Test Structure

The test suite (`tests/main.test.js`) covers:

#### Helper Functions
- `formatAmount()` - Number formatting to 2 decimal places
- `formatDaysText()` - Date difference text formatting
- `addProbabilityClass()` - CSS class assignment based on probability
- `addProbabilityBadge()` - Badge styling based on probability

#### Data Transformation Functions
- `enrichItem()` - Enriches item data with formatted values
- `enrichMatch()` - Enriches match data with display properties

#### File Upload Handler
- Successful file upload with data processing
- Error handling for invalid CSV files
- Network error handling

#### Search Functionality
- Validation that data must be uploaded before searching
- URL parameter construction for API calls
- Successful search result handling
- Error handling for search failures

#### Display Results
- Empty result handling
- Result type identification (items, orders, combinations)

#### DOM Manipulation
- Loading state toggling
- Form value updates
- Radio button selection

### JavaScript Technology Stack

- **Jest**: Testing framework
- **jsdom**: DOM simulation for browser environment testing
- **@jest/globals**: Jest utilities for ES modules
