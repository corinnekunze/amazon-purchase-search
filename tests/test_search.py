"""
Test suite for Amazon purchase search functionality.

Tests cover item search, order search, combination search, and edge cases.
Run with: pytest tests/test_search.py -v
Or simply: pytest
"""

import pytest
from app import (
    load_amazon_csv_from_string,
    find_matching_items,
    find_matching_orders,
    find_item_combinations,
)


# Fixtures for test data
@pytest.fixture
def basic_items_csv():
    """Sample CSV data with various price points for item search tests"""
    return """order id,order url,order date,quantity,description,item url,price,subscribe & save,ASIN
112-4070994-2049014,https://www.amazon.com/test1,2025-11-26,1,Test Item 1,https://www.amazon.com/test1,$36.65,0,TEST1
112-4070994-2049014,https://www.amazon.com/test2,2025-11-26,1,Test Item 2,https://www.amazon.com/test2,$10.00,0,TEST2
112-6824467-2953041,https://www.amazon.com/test3,2025-11-27,1,Test Item 3,https://www.amazon.com/test3,$35.81,0,TEST3
113-0050582-5388212,https://www.amazon.com/test4,2025-11-20,1,Test Item 4,https://www.amazon.com/test4,$25.00,0,TEST4
113-0050582-5388212,https://www.amazon.com/test5,2025-11-20,1,Test Item 5,https://www.amazon.com/test5,$25.00,0,TEST5
111-8126022-2916205,https://www.amazon.com/test6,2025-12-01,1,Test Item 6,https://www.amazon.com/test6,$15.97,0,TEST6"""


@pytest.fixture
def multi_item_order_csv():
    """CSV with multiple items in the same order for order search tests"""
    return """order id,order url,order date,quantity,description,item url,price,subscribe & save,ASIN
112-4070994-2049014,https://www.amazon.com/test1,2025-11-26,1,Test Item 1,https://www.amazon.com/test1,$36.65,0,TEST1
112-4070994-2049014,https://www.amazon.com/test2,2025-11-26,1,Test Item 2,https://www.amazon.com/test2,$10.00,0,TEST2
112-6824467-2953041,https://www.amazon.com/test3,2025-11-27,1,Test Item 3,https://www.amazon.com/test3,$35.81,0,TEST3"""


@pytest.fixture
def combination_test_csv():
    """CSV data for combination search tests"""
    return """order id,order url,order date,quantity,description,item url,price,subscribe & save,ASIN
112-4070994-2049014,https://www.amazon.com/test1,2025-11-26,1,Test Item 1,https://www.amazon.com/test1,$36.65,0,TEST1
112-4070994-2049014,https://www.amazon.com/test2,2025-11-26,1,Test Item 2,https://www.amazon.com/test2,$10.00,0,TEST2
112-6824467-2953041,https://www.amazon.com/test3,2025-11-27,1,Test Item 3,https://www.amazon.com/test3,$35.81,0,TEST3
113-0050582-5388212,https://www.amazon.com/test4,2025-11-26,1,Test Item 4,https://www.amazon.com/test4,$25.00,0,TEST4"""


# Item Search Tests
class TestItemSearch:
    """Test suite for item search functionality"""

    def test_find_exact_price_match_36_65(self, basic_items_csv):
        """Test finding an item with price $36.65 - the reported bug"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-26", 36.65, days_range=7)

        assert len(results) == 1, "Should find exactly one item with price $36.65"
        assert results[0]['amount'] == 36.65
        assert results[0]['description'] == 'Test Item 1'
        assert results[0]['date'] == '2025-11-26'

    def test_find_exact_price_match_35_81(self, basic_items_csv):
        """Test finding an item with price $35.81"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-27", 35.81, days_range=7)

        assert len(results) == 1
        assert results[0]['amount'] == 35.81
        assert results[0]['description'] == 'Test Item 3'

    def test_find_multiple_items_same_price(self, basic_items_csv):
        """Test finding multiple items with the same price"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-20", 25.00, days_range=7)

        assert len(results) == 2, "Should find two items with price $25.00"
        for result in results:
            assert result['amount'] == 25.00

    def test_no_match_outside_date_range(self, basic_items_csv):
        """Test that items outside the date range are not found"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-12-15", 36.65, days_range=7)

        assert len(results) == 0, "Should not find items outside the date range"

    def test_no_match_wrong_price(self, basic_items_csv):
        """Test that items with different prices are not found"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-26", 99.99, days_range=7)

        assert len(results) == 0, "Should not find items with different prices"

    def test_days_from_target_calculation(self, basic_items_csv):
        """Test that days_from_target is calculated correctly"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-24", 36.65, days_range=7)

        assert len(results) == 1
        # Purchase date is 2025-11-26, target is 2025-11-24, so diff should be 2
        assert results[0]['days_from_target'] == 2

    @pytest.mark.parametrize("price", [36.65, 35.81, 15.97, 10.00, 25.00])
    def test_floating_point_precision(self, basic_items_csv, price):
        """Test various decimal prices that could have floating-point issues"""
        load_amazon_csv_from_string(basic_items_csv)
        results = find_matching_items("2025-11-26", price, days_range=10)

        # Verify we can find items with these prices
        matching_results = [r for r in results if round(r['amount'], 2) == round(price, 2)]
        assert len(matching_results) > 0, f"Should find at least one item with price ${price}"


# Order Search Tests
class TestOrderSearch:
    """Test suite for order search functionality"""

    def test_find_order_by_total(self, multi_item_order_csv):
        """Test finding an order by its total amount"""
        load_amazon_csv_from_string(multi_item_order_csv)
        # First order total: 36.65 + 10.00 = 46.65
        results = find_matching_orders("2025-11-26", 46.65, days_range=7)

        assert len(results) == 1
        assert round(results[0]['total'], 2) == 46.65
        assert results[0]['item_count'] == 2

    def test_find_single_item_order(self, multi_item_order_csv):
        """Test finding an order with a single item"""
        load_amazon_csv_from_string(multi_item_order_csv)
        # Second order total: 35.81
        results = find_matching_orders("2025-11-27", 35.81, days_range=7)

        assert len(results) == 1
        assert round(results[0]['total'], 2) == 35.81
        assert results[0]['item_count'] == 1


# Combination Search Tests
class TestCombinationSearch:
    """Test suite for combination search functionality"""

    def test_find_two_item_combination(self, combination_test_csv):
        """Test finding a combination of two items"""
        load_amazon_csv_from_string(combination_test_csv)
        # 36.65 + 10.00 = 46.65
        results = find_item_combinations("2025-11-26", 46.65, days_range=7, max_items=5)

        assert len(results) > 0, "Should find at least one combination"

        # Find the exact match
        exact_matches = [r for r in results if r['total_amount'] == 46.65]
        assert len(exact_matches) > 0, "Should find exact combination match"
        assert exact_matches[0]['item_count'] == 2

    def test_combination_same_order_bonus(self, combination_test_csv):
        """Test that combinations from the same order get a higher probability score"""
        load_amazon_csv_from_string(combination_test_csv)
        # 36.65 + 10.00 = 46.65 (same order)
        results = find_item_combinations("2025-11-26", 46.65, days_range=7, max_items=5)

        assert len(results) > 0

        # Find matches from the same order
        same_order_matches = [r for r in results if r['same_order']]
        assert len(same_order_matches) > 0, "Should find same-order combinations"
        assert same_order_matches[0]['probability_score'] >= 50, \
            "Same order combinations should have score >= 50"


# Edge Cases Tests
class TestEdgeCases:
    """Test suite for edge cases and error conditions"""

    def test_empty_database(self):
        """Test searching when no data is loaded"""
        load_amazon_csv_from_string(
            "order id,order url,order date,quantity,description,item url,price,subscribe & save,ASIN"
        )
        results = find_matching_items("2025-11-26", 36.65, days_range=7)

        assert len(results) == 0

    def test_zero_price_items(self):
        """Test handling items with zero price"""
        test_csv = """order id,order url,order date,quantity,description,item url,price,subscribe & save,ASIN
112-4070994-2049014,https://www.amazon.com/test1,2025-11-26,1,Free Item,https://www.amazon.com/test1,$0.00,0,TEST1"""

        load_amazon_csv_from_string(test_csv)
        results = find_matching_items("2025-11-26", 0.00, days_range=7)

        # Zero price items are excluded by the combination finder but should be found by item search
        assert len(results) == 1
