import nunjucks from "https://esm.sh/nunjucks@3.2.4";
import { enrichMatch } from "./utils/helpers.js";

// Configure nunjucks to load templates from /static/templates/
const env = nunjucks.configure("/static/templates", {
  autoescape: true,
  web: {
    async: false,
  },
});

let dataLoaded = false;

document
  .getElementById("csvFile")
  .addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("dataStatus").textContent = "⏳ Processing...";

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        dataLoaded = true;
        document.getElementById("uploadSection").classList.add("loaded");
        document.getElementById("dataStatus").textContent =
          `✅ Loaded ${data.total_items} items from ${data.total_orders} orders`;
        document.getElementById("searchForm").classList.add("active");
        document.getElementById("date").valueAsDate = new Date();
      } else {
        throw new Error(data.error || "Upload failed");
      }
    } catch (error) {
      document.getElementById("dataStatus").textContent = `❌ ${error.message}`;
    }
  });

async function searchPurchases() {
  if (!dataLoaded) {
    alert("Please upload a CSV file first!");
    return;
  }

  const date = document.getElementById("date").value;
  const amount = document.getElementById("amount").value;
  const days_range = document.getElementById("days_range").value;
  const max_combo = document.getElementById("max_combo").value;
  const search_type = document.querySelector(
    'input[name="search_type"]:checked'
  ).value;

  document.getElementById("loading").classList.add("active");
  document.getElementById("results").classList.remove("active");
  document.getElementById("error").classList.remove("active");

  try {
    const response = await fetch(
      `/api/purchases/search?date=${date}&amount=${amount}&days_range=${days_range}&search_type=${search_type}&max_combo_items=${max_combo}`
    );

    const data = await response.json();
    document.getElementById("loading").classList.remove("active");

    if (!response.ok) throw new Error(data.error);

    displayResults(data);
  } catch (error) {
    document.getElementById("loading").classList.remove("active");
    const errorDiv = document.getElementById("error");
    errorDiv.textContent = error.message;
    errorDiv.classList.add("active");
  }
}

// Make searchPurchases available globally for the onclick handler
window.searchPurchases = searchPurchases;

function displayResults(data) {
  const resultsDiv = document.getElementById("results");

  // Prepare data for template using DRY helper functions
  const templateData = {
    hasItemMatches: data.item_matches?.length > 0,
    hasOrderMatches: data.order_matches?.length > 0,
    hasCombinations: data.combination_matches?.length > 0,
    noMatches: data.total_matches === 0,
    item_matches: data.item_matches?.map(enrichMatch),
    order_matches: data.order_matches?.map(enrichMatch),
    combination_matches: data.combination_matches?.map(enrichMatch)
  };

  // Render template
  resultsDiv.innerHTML = nunjucks.render("results.html", templateData);
  resultsDiv.classList.add("active");
}
