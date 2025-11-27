### Amazon Purchases

An app that tries to find what the purchase was for your price paid to itemize for budgeting software

## How To Run Locally

- Install deps: `pip install -r requirements_deploy.txt`
- Run app `python app.py`

## Running Tests

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_search.py
```

### Run specific test class

```bash
pytest tests/test_search.py::TestItemSearch
```

### Run specific test

```bash
pytest tests/test_search.py::TestItemSearch::test_find_exact_price_match_36_65
```

## Adding New Tests

1. Create a new test file named `test_*.py`
2. Use pytest fixtures for reusable test data
3. Use `@pytest.mark.parametrize` for testing multiple inputs
4. Follow the existing test structure and naming conventions
