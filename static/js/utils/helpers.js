/**
 * Utility functions for data formatting and transformation
 */

/**
 * Format a number to 2 decimal places
 * @param {number|*} amount - The amount to format
 * @returns {string|*} Formatted amount or original value if not a number
 */
export function formatAmount(amount) {
  return typeof amount === 'number' ? amount.toFixed(2) : amount;
}

/**
 * Format days from target date as human-readable text
 * @param {number} days_from_target - Number of days from target (negative = before, positive = after)
 * @returns {string} Formatted text like "Same day", "3d before", "5d after"
 */
export function formatDaysText(days_from_target) {
  if (days_from_target === 0) return "Same day";
  if (days_from_target < 0) return `${Math.abs(days_from_target)}d before`;
  return `${days_from_target}d after`;
}

/**
 * Get CSS class based on probability score
 * @param {number} probability_score - Probability score (0-100)
 * @returns {string} CSS class name or empty string
 */
export function addProbabilityClass(probability_score) {
  return probability_score >= 70 ? "high-probability" : "";
}

/**
 * Get probability badge class based on score
 * @param {number} probability_score - Probability score (0-100)
 * @returns {string} Badge class name
 */
export function addProbabilityBadge(probability_score) {
  return probability_score >= 70 ? "probability-high" : "probability-medium";
}

/**
 * Enrich an item with formatted values
 * @param {Object} item - Item object with amount and optional days_from_target
 * @returns {Object} Enriched item with formatted amount and daysText
 */
export function enrichItem(item) {
  return {
    ...item,
    amount: formatAmount(item.amount),
    daysText: item.days_from_target !== undefined ? formatDaysText(item.days_from_target) : null
  };
}

/**
 * Enrich a match with display properties
 * @param {Object} match - Match object (item, order, or combination)
 * @param {number} index - Index in the results array
 * @returns {Object} Enriched match with display properties
 */
export function enrichMatch(match, index) {
  const enriched = {
    ...match,
    index: index + 1
  };

  // Add display amount (handles both 'amount' and 'total' fields)
  enriched.displayAmount = formatAmount(match.total || match.total_amount || match.amount);

  // Add days text if available
  if (match.days_from_target !== undefined) {
    enriched.daysText = formatDaysText(match.days_from_target);
  }

  // Add probability classes for combinations
  if (match.probability_score !== undefined) {
    enriched.probClass = addProbabilityClass(match.probability_score);
    enriched.probBadge = addProbabilityBadge(match.probability_score);
  }

  // Enrich nested items if present
  if (match.items) {
    enriched.items = match.items.map(enrichItem);
  }

  return enriched;
}
