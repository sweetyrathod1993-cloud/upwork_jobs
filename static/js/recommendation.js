// Client logic for Task 5: Personalized Job Recommendation Engine
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("recommendation-form");
  const resultsContainer = document.getElementById("recommendations-list");
  const loadingIndicator = document.getElementById("loading-state");
  const emptyIndicator = document.getElementById("empty-state");
  const resultsCount = document.getElementById("results-count");

  // Skill suggestion pills
  const skillPills = document.querySelectorAll(".skill-pill");
  const queryInput = document.getElementById("query-input");

  skillPills.forEach(pill => {
    pill.addEventListener("click", () => {
      const skill = pill.getAttribute("data-skill");
      let currentVal = queryInput.value.trim();
      if (!currentVal.toLowerCase().includes(skill.toLowerCase())) {
        queryInput.value = currentVal ? `${currentVal} ${skill}` : skill;
        triggerRecommendation();
      }
    });
  });

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      triggerRecommendation();
    });
  }

  // Filter triggers
  const filterInputs = ["category-select", "country-select", "seniority-select", "hourly-toggle", "min-rate-input"];
  filterInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => triggerRecommendation());
    }
  });

  function triggerRecommendation() {
    const query = queryInput.value.trim();
    const category = document.getElementById("category-select").value;
    const country = document.getElementById("country-select").value;
    const seniority = document.getElementById("seniority-select").value;
    const hourlyVal = document.getElementById("hourly-toggle").value;
    const minRateVal = document.getElementById("min-rate-input").value;

    let isHourly = null;
    if (hourlyVal === "hourly") isHourly = true;
    if (hourlyVal === "fixed") isHourly = false;

    const payload = {
      query: query || "Software Developer",
      category: category,
      country: country,
      seniority: seniority,
      is_hourly: isHourly,
      min_rate: minRateVal ? parseFloat(minRateVal) : null,
      top_k: 12
    };

    if (loadingIndicator) loadingIndicator.classList.remove("hidden");
    if (emptyIndicator) emptyIndicator.classList.add("hidden");
    if (resultsContainer) resultsContainer.innerHTML = "";

    fetch("/api/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");

      if (!data.recommendations || data.recommendations.length === 0) {
        if (emptyIndicator) emptyIndicator.classList.remove("hidden");
        if (resultsCount) resultsCount.textContent = "0 jobs matched";
        return;
      }

      if (resultsCount) {
        resultsCount.textContent = `${data.recommendations.length} top recommended matches (Query: "${data.query_echo}")`;
      }

      renderJobCards(data.recommendations);
    })
    .catch(err => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");
      console.error("Error fetching recommendations:", err);
      if (resultsContainer) {
        resultsContainer.innerHTML = `<div class="p-4 bg-red-50 text-red-700 rounded-xl">Error fetching recommendations. Please try again.</div>`;
      }
    });
  }

  function renderJobCards(jobs) {
    resultsContainer.innerHTML = "";

    jobs.forEach(job => {
      const card = document.createElement("div");
      card.className = "bg-white p-5 rounded-2xl border border-slate-200 card-hover flex flex-col justify-between shadow-sm";

      // Match score badge color
      let scoreClass = "bg-emerald-100 text-emerald-800 border-emerald-300";
      if (job.match_score < 70) scoreClass = "bg-blue-100 text-blue-800 border-blue-300";
      if (job.match_score < 40) scoreClass = "bg-amber-100 text-amber-800 border-amber-300";

      // Matched keywords tags
      let matchedHtml = "";
      if (job.matched_keywords && job.matched_keywords.length > 0) {
        matchedHtml = `
          <div class="mt-3 flex flex-wrap gap-1.5 items-center">
            <span class="text-xs text-slate-400 font-medium mr-1">Matched:</span>
            ${job.matched_keywords.map(kw => `<span class="badge-tag bg-emerald-50 text-emerald-700 border border-emerald-200">${kw}</span>`).join("")}
          </div>
        `;
      }

      card.innerHTML = `
        <div>
          <div class="flex items-start justify-between gap-3 mb-2">
            <span class="badge-tag border ${scoreClass} font-mono font-bold text-xs">
              ⚡ ${job.match_score}% Match
            </span>
            <span class="text-xs text-slate-400 font-medium">${job.published_date || 'Recent'}</span>
          </div>

          <h3 class="font-bold text-slate-900 text-base leading-snug line-clamp-2 hover:text-blue-600 transition">
            <a href="${job.link}" target="_blank" rel="noopener noreferrer">${job.title}</a>
          </h3>

          <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
            <span class="flex items-center gap-1 font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded-md">
              💰 ${job.compensation}
            </span>
            <span class="flex items-center gap-1 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
              🌍 ${job.country || 'Global'}
            </span>
            <span class="flex items-center gap-1 bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md">
              🏷️ ${job.category}
            </span>
            <span class="flex items-center gap-1 bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md">
              👔 ${job.seniority}
            </span>
          </div>

          ${matchedHtml}
        </div>

        <div class="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
          <span class="text-xs text-slate-400 font-mono">ID: #${job.id}</span>
          <a href="${job.link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition">
            View on Upwork
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
          </a>
        </div>
      `;

      resultsContainer.appendChild(card);
    });
  }

  // Initial load recommendation
  triggerRecommendation();
});
