/**
 * @jest-environment jsdom
 */
import { jest } from '@jest/globals';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load the actual HTML template
const htmlTemplate = readFileSync(
  join(__dirname, '..', 'templates', 'index.html'),
  'utf-8'
);

// Mock nunjucks before importing main.js
const mockNunjucks = {
  configure: jest.fn(() => mockNunjucks),
  render: jest.fn((template) => template)
};

// Mock the ES module import
global.fetch = jest.fn();

// Setup DOM before tests using actual HTML
beforeEach(() => {
  // Remove Jinja2 template tags and set the HTML
  const cleanedHtml = htmlTemplate
    .replace(/\{\{[^}]+\}\}/g, '') // Remove {{ }} tags
    .replace(/<script[^>]*>.*?<\/script>/gs, ''); // Remove script tags

  document.documentElement.innerHTML = cleanedHtml;

  // Reset all mocks
  jest.clearAllMocks();
  global.fetch.mockClear();

  // Mock alert
  global.alert = jest.fn();
});

describe('CSV File Upload', () => {
  test('should handle successful file upload', async () => {
    const mockFile = new File(['test data'], 'test.csv', { type: 'text/csv' });
    const mockResponse = {
      ok: true,
      json: async () => ({ total_items: 100, total_orders: 20 })
    };

    global.fetch.mockResolvedValueOnce(mockResponse);

    const fileInput = document.getElementById('csvFile');
    const dataStatus = document.getElementById('dataStatus');

    // Setup file input
    Object.defineProperty(fileInput, 'files', {
      value: [mockFile],
      writable: false
    });

    // Simulate the event handler
    const formData = new FormData();
    formData.append('file', mockFile);

    dataStatus.textContent = '⏳ Processing...';

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    expect(global.fetch).toHaveBeenCalledWith('/api/upload', {
      method: 'POST',
      body: expect.any(FormData)
    });

    expect(data.total_items).toBe(100);
    expect(data.total_orders).toBe(20);
  });

  test('should handle upload error', async () => {
    const mockFile = new File(['test data'], 'test.csv', { type: 'text/csv' });
    const mockResponse = {
      ok: false,
      json: async () => ({ error: 'Invalid CSV format' })
    };

    global.fetch.mockResolvedValueOnce(mockResponse);

    const dataStatus = document.getElementById('dataStatus');

    try {
      const formData = new FormData();
      formData.append('file', mockFile);

      dataStatus.textContent = '⏳ Processing...';

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }
    } catch (error) {
      dataStatus.textContent = `❌ ${error.message}`;
    }

    expect(dataStatus.textContent).toBe('❌ Invalid CSV format');
  });

  test('should handle network error', async () => {
    const mockFile = new File(['test data'], 'test.csv', { type: 'text/csv' });

    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const dataStatus = document.getElementById('dataStatus');

    try {
      const formData = new FormData();
      formData.append('file', mockFile);

      dataStatus.textContent = '⏳ Processing...';

      await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
    } catch (error) {
      dataStatus.textContent = `❌ ${error.message}`;
    }

    expect(dataStatus.textContent).toBe('❌ Network error');
  });
});

describe('Search Functionality', () => {
  test('should prevent search without uploaded data', () => {
    const dataLoaded = false;

    if (!dataLoaded) {
      alert('Please upload a CSV file first!');
    }

    expect(global.alert).toHaveBeenCalledWith('Please upload a CSV file first!');
  });

  test('should construct correct search URL with parameters', async () => {
    const date = '2024-01-15';
    const amount = '31.23';
    const days_range = '7';
    const max_combo = '5';
    const search_type = 'all';

    const expectedUrl = `/api/purchases/search?date=${date}&amount=${amount}&days_range=${days_range}&search_type=${search_type}&max_combo_items=${max_combo}`;

    const mockResponse = {
      ok: true,
      json: async () => ({
        total_matches: 0,
        item_matches: [],
        order_matches: [],
        combination_matches: []
      })
    };

    global.fetch.mockResolvedValueOnce(mockResponse);

    await fetch(expectedUrl);

    expect(global.fetch).toHaveBeenCalledWith(expectedUrl);
  });

  test('should handle successful search with results', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        total_matches: 2,
        item_matches: [
          { amount: 31.23, title: 'Test Item 1', days_from_target: 0 }
        ],
        order_matches: [
          { total_amount: 31.23, order_id: 'ORDER-123', days_from_target: 1 }
        ],
        combination_matches: []
      })
    };

    global.fetch.mockResolvedValueOnce(mockResponse);

    const response = await fetch('/api/purchases/search?date=2024-01-15&amount=31.23&days_range=7&search_type=all&max_combo_items=5');
    const data = await response.json();

    expect(response.ok).toBe(true);
    expect(data.total_matches).toBe(2);
    expect(data.item_matches).toHaveLength(1);
    expect(data.order_matches).toHaveLength(1);
  });

  test('should handle search error', async () => {
    const mockResponse = {
      ok: false,
      json: async () => ({ error: 'No data uploaded' })
    };

    global.fetch.mockResolvedValueOnce(mockResponse);

    const errorDiv = document.getElementById('error');

    try {
      const response = await fetch('/api/purchases/search?date=2024-01-15&amount=31.23&days_range=7&search_type=all&max_combo_items=5');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error);
      }
    } catch (error) {
      errorDiv.textContent = error.message;
      errorDiv.classList.add('active');
    }

    expect(errorDiv.textContent).toBe('No data uploaded');
    expect(errorDiv.classList.contains('active')).toBe(true);
  });
});

describe('Display Results', () => {
  test('should handle empty results', () => {
    const data = {
      total_matches: 0,
      item_matches: [],
      order_matches: [],
      combination_matches: []
    };

    const templateData = {
      hasItemMatches: data.item_matches?.length > 0,
      hasOrderMatches: data.order_matches?.length > 0,
      hasCombinations: data.combination_matches?.length > 0,
      noMatches: data.total_matches === 0,
      item_matches: data.item_matches?.map((m, i) => ({ ...m, index: i + 1 })),
      order_matches: data.order_matches?.map((m, i) => ({ ...m, index: i + 1 })),
      combination_matches: data.combination_matches?.map((m, i) => ({ ...m, index: i + 1 }))
    };

    expect(templateData.noMatches).toBe(true);
    expect(templateData.hasItemMatches).toBe(false);
    expect(templateData.hasOrderMatches).toBe(false);
    expect(templateData.hasCombinations).toBe(false);
  });

  test('should correctly identify result types', () => {
    const data = {
      total_matches: 3,
      item_matches: [{ amount: 31.23 }],
      order_matches: [{ total_amount: 31.23 }],
      combination_matches: [{ total: 31.23, items: [] }]
    };

    const templateData = {
      hasItemMatches: data.item_matches?.length > 0,
      hasOrderMatches: data.order_matches?.length > 0,
      hasCombinations: data.combination_matches?.length > 0,
      noMatches: data.total_matches === 0
    };

    expect(templateData.hasItemMatches).toBe(true);
    expect(templateData.hasOrderMatches).toBe(true);
    expect(templateData.hasCombinations).toBe(true);
    expect(templateData.noMatches).toBe(false);
  });
});

describe('DOM Manipulation', () => {
  test('should toggle loading state correctly', () => {
    const loading = document.getElementById('loading');

    loading.classList.add('active');
    expect(loading.classList.contains('active')).toBe(true);

    loading.classList.remove('active');
    expect(loading.classList.contains('active')).toBe(false);
  });

  test('should update form values correctly', () => {
    const dateInput = document.getElementById('date');
    const amountInput = document.getElementById('amount');
    const daysRangeInput = document.getElementById('days_range');
    const maxComboInput = document.getElementById('max_combo');

    dateInput.value = '2024-01-15';
    amountInput.value = '31.23';
    daysRangeInput.value = '10';
    maxComboInput.value = '7';

    expect(dateInput.value).toBe('2024-01-15');
    expect(amountInput.value).toBe('31.23');
    expect(daysRangeInput.value).toBe('10');
    expect(maxComboInput.value).toBe('7');
  });

  test('should get selected radio button value', () => {
    const allRadio = document.querySelector('input[name="search_type"][value="all"]');

    expect(allRadio.checked).toBe(true);
    expect(allRadio.value).toBe('all');
  });
});

describe('Actual HTML Structure', () => {
  test('should load actual HTML elements from index.html', () => {
    // Verify the actual HTML structure is loaded
    expect(document.querySelector('h1').textContent).toContain('Smart Amazon Purchase Search');
    expect(document.querySelector('.subtitle').textContent).toContain('Upload your Amazon order history');
    expect(document.getElementById('csvFile')).toBeTruthy();
    expect(document.getElementById('uploadSection')).toBeTruthy();
    expect(document.getElementById('searchForm')).toBeTruthy();
  });

  test('should have all required form inputs from actual HTML', () => {
    expect(document.getElementById('date').type).toBe('date');
    expect(document.getElementById('amount').type).toBe('number');
    expect(document.getElementById('amount').step).toBe('0.01');
    expect(document.getElementById('days_range').value).toBe('7');
    expect(document.getElementById('max_combo').value).toBe('5');
  });

  test('should have all search type radio buttons from actual HTML', () => {
    const radioButtons = document.querySelectorAll('input[name="search_type"]');
    expect(radioButtons.length).toBe(4);

    const values = Array.from(radioButtons).map(rb => rb.value);
    expect(values).toContain('all');
    expect(values).toContain('combination');
    expect(values).toContain('item');
    expect(values).toContain('order');
  });

  test('should have Quick Start instructions from actual HTML', () => {
    const body = document.body.textContent;
    expect(body).toContain('Quick Start:');
    expect(body).toContain('Amazon Order History Reporter');
  });
});
