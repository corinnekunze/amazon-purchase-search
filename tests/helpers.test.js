/**
 * Tests for utility helper functions
 */
import { describe, test, expect } from '@jest/globals';
import {
  formatAmount,
  formatDaysText,
  addProbabilityClass,
  addProbabilityBadge,
  enrichItem,
  enrichMatch
} from '../static/js/utils/helpers.js';

describe('formatAmount', () => {
  test('should format number to 2 decimal places', () => {
    expect(formatAmount(10)).toBe('10.00');
    expect(formatAmount(10.5)).toBe('10.50');
    expect(formatAmount(10.555)).toBe('10.55');
    expect(formatAmount(0)).toBe('0.00');
  });

  test('should return non-number values as-is', () => {
    expect(formatAmount('10.00')).toBe('10.00');
    expect(formatAmount(null)).toBe(null);
    expect(formatAmount(undefined)).toBe(undefined);
  });

  test('should handle negative numbers', () => {
    expect(formatAmount(-10.5)).toBe('-10.50');
    expect(formatAmount(-0.01)).toBe('-0.01');
  });

  test('should handle very large numbers', () => {
    expect(formatAmount(1234567.89)).toBe('1234567.89');
    expect(formatAmount(999999.999)).toBe('1000000.00');
  });
});

describe('formatDaysText', () => {
  test('should format same day correctly', () => {
    expect(formatDaysText(0)).toBe('Same day');
  });

  test('should format days before correctly', () => {
    expect(formatDaysText(-1)).toBe('1d before');
    expect(formatDaysText(-5)).toBe('5d before');
    expect(formatDaysText(-10)).toBe('10d before');
  });

  test('should format days after correctly', () => {
    expect(formatDaysText(1)).toBe('1d after');
    expect(formatDaysText(5)).toBe('5d after');
    expect(formatDaysText(10)).toBe('10d after');
  });

  test('should handle large day differences', () => {
    expect(formatDaysText(-365)).toBe('365d before');
    expect(formatDaysText(365)).toBe('365d after');
  });
});

describe('addProbabilityClass', () => {
  test('should return "high-probability" for scores >= 70', () => {
    expect(addProbabilityClass(70)).toBe('high-probability');
    expect(addProbabilityClass(80)).toBe('high-probability');
    expect(addProbabilityClass(100)).toBe('high-probability');
  });

  test('should return empty string for scores < 70', () => {
    expect(addProbabilityClass(69)).toBe('');
    expect(addProbabilityClass(50)).toBe('');
    expect(addProbabilityClass(0)).toBe('');
  });

  test('should handle edge cases', () => {
    expect(addProbabilityClass(69.9)).toBe('');
    expect(addProbabilityClass(70.0)).toBe('high-probability');
  });
});

describe('addProbabilityBadge', () => {
  test('should return "probability-high" for scores >= 70', () => {
    expect(addProbabilityBadge(70)).toBe('probability-high');
    expect(addProbabilityBadge(90)).toBe('probability-high');
    expect(addProbabilityBadge(100)).toBe('probability-high');
  });

  test('should return "probability-medium" for scores < 70', () => {
    expect(addProbabilityBadge(69)).toBe('probability-medium');
    expect(addProbabilityBadge(50)).toBe('probability-medium');
    expect(addProbabilityBadge(0)).toBe('probability-medium');
  });

  test('should handle boundary values', () => {
    expect(addProbabilityBadge(69.99)).toBe('probability-medium');
    expect(addProbabilityBadge(70.01)).toBe('probability-high');
  });
});

describe('enrichItem', () => {
  test('should enrich item with formatted amount', () => {
    const item = { amount: 25.5, title: 'Test Item' };
    const enriched = enrichItem(item);

    expect(enriched.amount).toBe('25.50');
    expect(enriched.title).toBe('Test Item');
  });

  test('should add daysText if days_from_target is present', () => {
    const item = { amount: 25.5, days_from_target: -2 };
    const enriched = enrichItem(item);

    expect(enriched.daysText).toBe('2d before');
    expect(enriched.amount).toBe('25.50');
  });

  test('should set daysText to null if days_from_target is not present', () => {
    const item = { amount: 25.5 };
    const enriched = enrichItem(item);

    expect(enriched.daysText).toBe(null);
  });

  test('should preserve all original properties', () => {
    const item = {
      amount: 10,
      title: 'Item',
      category: 'Electronics',
      days_from_target: 0
    };
    const enriched = enrichItem(item);

    expect(enriched.title).toBe('Item');
    expect(enriched.category).toBe('Electronics');
    expect(enriched.daysText).toBe('Same day');
  });
});

describe('enrichMatch', () => {
  test('should add index to match', () => {
    const match = { total: 50.00 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.index).toBe(1);
  });

  test('should format displayAmount from total field', () => {
    const match = { total: 50.5 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.displayAmount).toBe('50.50');
  });

  test('should format displayAmount from total_amount field', () => {
    const match = { total_amount: 50.5 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.displayAmount).toBe('50.50');
  });

  test('should format displayAmount from amount field', () => {
    const match = { amount: 50.5 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.displayAmount).toBe('50.50');
  });

  test('should prioritize total over total_amount and amount', () => {
    const match = { total: 50.5, total_amount: 40.0, amount: 30.0 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.displayAmount).toBe('50.50');
  });

  test('should add daysText if days_from_target is present', () => {
    const match = { total: 50.00, days_from_target: 3 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.daysText).toBe('3d after');
  });

  test('should add probability classes for combinations', () => {
    const match = { total: 50.00, probability_score: 85 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.probClass).toBe('high-probability');
    expect(enriched.probBadge).toBe('probability-high');
  });

  test('should add medium probability classes for low scores', () => {
    const match = { total: 50.00, probability_score: 55 };
    const enriched = enrichMatch(match, 0);

    expect(enriched.probClass).toBe('');
    expect(enriched.probBadge).toBe('probability-medium');
  });

  test('should enrich nested items if present', () => {
    const match = {
      total: 50.00,
      items: [
        { amount: 25.5, title: 'Item 1' },
        { amount: 24.5, title: 'Item 2' }
      ]
    };
    const enriched = enrichMatch(match, 0);

    expect(enriched.items).toHaveLength(2);
    expect(enriched.items[0].amount).toBe('25.50');
    expect(enriched.items[1].amount).toBe('24.50');
  });

  test('should handle complex match with all properties', () => {
    const match = {
      total: 100.50,
      days_from_target: -5,
      probability_score: 75,
      items: [
        { amount: 50.25, title: 'Item 1', days_from_target: -5 },
        { amount: 50.25, title: 'Item 2', days_from_target: -4 }
      ]
    };
    const enriched = enrichMatch(match, 2);

    expect(enriched.index).toBe(3);
    expect(enriched.displayAmount).toBe('100.50');
    expect(enriched.daysText).toBe('5d before');
    expect(enriched.probClass).toBe('high-probability');
    expect(enriched.probBadge).toBe('probability-high');
    expect(enriched.items[0].daysText).toBe('5d before');
    expect(enriched.items[1].daysText).toBe('4d before');
  });
});
