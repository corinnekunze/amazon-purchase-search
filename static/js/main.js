let dataLoaded = false;

document
  .getElementById("csvFile")
  .addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("dataStatus").innerHTML = "⏳ Processing...";

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        dataLoaded = true;
        document.getElementById("uploadSection").classList.add("loaded");
        document.getElementById(
          "dataStatus"
        ).innerHTML = `✅ Loaded ${data.total_items} items from ${data.total_orders} orders`;
        document.getElementById("searchForm").classList.add("active");
        document.getElementById("date").valueAsDate = new Date();
      } else {
        throw new Error(data.error || "Upload failed");
      }
    } catch (error) {
      document.getElementById(
        "dataStatus"
      ).innerHTML = `❌ ${error.message}`;
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

function displayResults(data) {
  const resultsDiv = document.getElementById("results");
  let html = "<h2>Results</h2>";

  if (data.combination_matches && data.combination_matches.length > 0) {
    html +=
      '<h3 style="margin: 20px 0;">🧮 Combinations (Exact Matches)</h3>';
    data.combination_matches.forEach((combo, i) => {
      const probClass =
        combo.probability_score >= 70 ? "high-probability" : "";
      const probBadge =
        combo.probability_score >= 70
          ? "probability-high"
          : "probability-medium";

      html += `
                <div class="combo-card ${probClass}">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <div>
                            <div style="color: #666; font-size: 12px;">Match #${
                              i + 1
                            }</div>
                            <div class="combo-total">$${combo.total_amount.toFixed(
                              2
                            )}</div>
                            <div style="color: #4CAF50; margin-top: 5px; font-weight: 600;">✓ EXACT MATCH</div>
                        </div>
                        <div class="${probBadge}">${
        combo.probability_score
      }%</div>
                    </div>
                    <strong>${combo.item_count} Items:</strong>
                    ${combo.items
                      .map(
                        (item) => `
                        <div class="combo-item">
                            <div>
                                <div style="font-weight: 600;">$${item.amount.toFixed(
                                  2
                                )}</div>
                                <div style="font-size: 13px; color: #666;">${
                                  item.description
                                }</div>
                            </div>
                            <div style="text-align: right; font-size: 13px; color: #666;">
                                ${item.date}<br>
                                ${
                                  item.days_from_target === 0
                                    ? "Same day"
                                    : item.days_from_target < 0
                                    ? `${Math.abs(
                                        item.days_from_target
                                      )}d before`
                                    : `${item.days_from_target}d after`
                                }
                            </div>
                        </div>
                    `
                      )
                      .join("")}
                    <div style="margin-top: 10px; font-size: 13px; color: #666;">
                        ${combo.same_order ? "✅ SAME ORDER" : ""}
                    </div>
                </div>
            `;
    });
  }

  if (data.total_matches === 0) {
    html +=
      '<div style="text-align: center; padding: 40px; color: #999;">No exact matches found. Try increasing the date range.</div>';
  }

  resultsDiv.innerHTML = html;
  resultsDiv.classList.add("active");
}
