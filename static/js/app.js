/**
 * Master Frontend Controller - TruthGuard AI
 * Orchestrates API calls, tab switching, token heatmaps,
 * batch CSV parsing, live news feed, and export certificates.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Current analysis cache
  let currentAnalysis = null;
  let activeHighlightFilter = "all";
  let sampleArticles = [];

  // DOM Elements
  const headlineInput = document.getElementById("headline-input");
  const articleTextInput = document.getElementById("article-text-input");
  const domainInput = document.getElementById("domain-input");
  const urlInput = document.getElementById("url-input");
  const headlineCounter = document.getElementById("headline-counter");
  const textCounter = document.getElementById("text-counter");

  // Tab Navigation
  const navTabs = document.querySelectorAll(".nav-tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.target;
      navTabs.forEach((t) => t.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");

      // Auto-trigger tab-specific updates
      if (targetId === "tab-analytics" && currentAnalysis) {
        window.AppCharts.updateRadarChart(currentAnalysis.radar_dimensions);
      } else if (targetId === "tab-wire") {
        fetchLiveWire();
      } else if (targetId === "tab-model") {
        fetchModelMetrics();
      } else if (targetId === "tab-history") {
        fetchScanHistory();
      }
    });
  });

  // Input Mode Switching (Text vs URL)
  const modeTabs = document.querySelectorAll(".mode-tab-btn");
  const textInputContainer = document.getElementById("text-input-mode-container");
  const urlInputContainer = document.getElementById("url-input-mode-container");

  modeTabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      modeTabs.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      if (btn.dataset.mode === "url") {
        textInputContainer.style.display = "none";
        urlInputContainer.style.display = "block";
      } else {
        textInputContainer.style.display = "block";
        urlInputContainer.style.display = "none";
      }
    });
  });

  // Character and Word Counters
  if (headlineInput && headlineCounter) {
    headlineInput.addEventListener("input", () => {
      headlineCounter.textContent = `${headlineInput.value.length} chars`;
    });
  }

  if (articleTextInput && textCounter) {
    articleTextInput.addEventListener("input", () => {
      const words = articleTextInput.value.trim().split(/\s+/).filter(Boolean);
      textCounter.textContent = `${words.length} words`;
    });
  }

  // Load Presets
  fetchPresets();

  async function fetchPresets() {
    try {
      const res = await fetch("/api/samples");
      sampleArticles = await res.json();
      renderPresetChips(sampleArticles);
    } catch (err) {
      console.warn("Could not fetch samples:", err);
    }
  }

  function renderPresetChips(samples) {
    const container = document.getElementById("presets-container");
    if (!container) return;
    container.innerHTML = "";

    samples.forEach((sample) => {
      const chip = document.createElement("button");
      chip.className = "preset-chip";
      const icon = sample.type === "REAL" ? "📰" : "🚨";
      chip.innerHTML = `<span>${icon}</span> ${sample.category}`;
      chip.addEventListener("click", () => loadSample(sample));
      container.appendChild(chip);
    });
  }

  function loadSample(sample) {
    headlineInput.value = sample.title || "";
    articleTextInput.value = sample.text || "";
    domainInput.value = sample.domain || "";

    // Trigger counters
    headlineInput.dispatchEvent(new Event("input"));
    articleTextInput.dispatchEvent(new Event("input"));

    // Switch back to text mode if on URL mode
    const textTab = document.querySelector('.mode-tab-btn[data-mode="text"]');
    if (textTab) textTab.click();

    // Auto-trigger analysis
    analyzeContent();
  }

  // Action: Analyze Button
  const btnAnalyze = document.getElementById("btn-analyze");
  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", analyzeContent);
  }

  // Action: Clear Button
  const btnClear = document.getElementById("btn-clear");
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      headlineInput.value = "";
      articleTextInput.value = "";
      domainInput.value = "";
      urlInput.value = "";
      headlineCounter.textContent = "0 chars";
      textCounter.textContent = "0 words";
    });
  }

  // Action: Scrape & Analyze Button
  const btnScrape = document.getElementById("btn-scrape");
  if (btnScrape) {
    btnScrape.addEventListener("click", async () => {
      const url = urlInput.value.trim();
      if (!url) {
        showToast("Please enter a valid news article URL.", "warning");
        return;
      }

      setLoading(btnScrape, true, "Scraping & Analyzing...");
      try {
        const resp = await fetch("/api/scrape", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url })
        });
        const data = await resp.json();

        if (!data.success) {
          showToast(data.error || "Failed to scrape URL.", "danger");
          return;
        }

        // Fill fields with extracted content
        headlineInput.value = data.scraped_meta.title || "";
        articleTextInput.value = data.analysis ? headlineInput.value + "\n\n" : "";
        domainInput.value = data.scraped_meta.domain || "";

        // Switch to text view to review
        const textTab = document.querySelector('.mode-tab-btn[data-mode="text"]');
        if (textTab) textTab.click();

        // Render analysis
        renderAnalysisResults(data.analysis);
        showToast("URL successfully analyzed!", "success");
      } catch (err) {
        showToast("Scraper error: " + err.message, "danger");
      } finally {
        setLoading(btnScrape, false, "Scrape & Verify");
      }
    });
  }

  async function analyzeContent() {
    const title = headlineInput.value.trim();
    const text = articleTextInput.value.trim();
    const domain = domainInput.value.trim();

    if (!title && !text) {
      showToast("Please provide an article headline or body text.", "warning");
      return;
    }

    setLoading(btnAnalyze, true, "Verifying...");
    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, text, domain })
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Server analysis error.");
      }

      const result = await resp.json();
      currentAnalysis = result;
      renderAnalysisResults(result);
    } catch (err) {
      showToast(err.message, "danger");
    } finally {
      setLoading(btnAnalyze, false, "Scan & Verify Authenticity");
    }
  }

  // Render Full Results
  function renderAnalysisResults(data) {
    if (!data) return;

    // 1. Truth Gauge
    window.AppCharts.updateTruthGauge(data.veracity_score);

    // 2. Verdict Badge & Summary
    const badgeElem = document.getElementById("verdict-badge");
    if (badgeElem) {
      badgeElem.className = `verdict-badge ${data.verdict_badge}`;
      badgeElem.innerHTML = `<span>🛡️</span> ${data.verdict}`;
    }

    const summaryElem = document.getElementById("verdict-summary");
    if (summaryElem) {
      summaryElem.textContent = data.summary_desc;
    }

    const riskLevelElem = document.getElementById("risk-level-badge");
    if (riskLevelElem) {
      riskLevelElem.textContent = data.risk_level;
      riskLevelElem.className = `badge-${data.verdict_badge}`;
    }

    // 3. Flags
    renderFlagsList("green-flags-list", data.green_flags, "green");
    renderFlagsList("red-flags-list", data.red_flags, "red");

    // 4. Model Consensus Cards
    document.getElementById("consensus-pac").textContent = data.model_breakdown.passive_aggressive_label;
    document.getElementById("consensus-lr").textContent = `${data.model_breakdown.logistic_regression_real_prob}% Real`;
    document.getElementById("consensus-ling").textContent = `${data.model_breakdown.linguistic_score}%`;

    // 5. Token Explainability Heatmap
    renderTokenHeatmap(data.token_highlights);

    // 6. Deep Analytics Details
    renderAnalyticsTab(data);

    // 7. Update breakdown charts
    window.AppCharts.updateBreakdownChart(
      data.model_breakdown.logistic_regression_real_prob,
      data.model_breakdown.logistic_regression_fake_prob
    );
  }

  function renderFlagsList(elemId, items, color) {
    const list = document.getElementById(elemId);
    if (!list) return;
    list.innerHTML = "";

    if (!items || items.length === 0) {
      list.innerHTML = `<li style="color: var(--text-dim);">No specific ${color === "green" ? "credibility" : "deceptive"} flags detected.</li>`;
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      const icon = color === "green" ? "✅" : "⚠️";
      li.innerHTML = `<span>${icon}</span> <span>${item}</span>`;
      list.appendChild(li);
    });
  }

  // Token Heatmap Rendering
  function renderTokenHeatmap(tokens) {
    const container = document.getElementById("heatmap-viewer");
    if (!container || !tokens) return;
    container.innerHTML = "";

    tokens.forEach((t) => {
      if (t.type === "neutral") {
        const span = document.createElement("span");
        span.textContent = t.text;
        container.appendChild(span);
      } else if (t.type === "deceptive") {
        if (activeHighlightFilter === "credible") {
          const span = document.createElement("span");
          span.textContent = t.text;
          container.appendChild(span);
        } else {
          const span = document.createElement("span");
          span.className = "tok-deceptive";
          span.textContent = t.text;
          span.title = `Deceptive Trigger: ${t.reason} (Weight: ${t.weight})`;
          container.appendChild(span);
        }
      } else if (t.type === "credible") {
        if (activeHighlightFilter === "deceptive") {
          const span = document.createElement("span");
          span.textContent = t.text;
          container.appendChild(span);
        } else {
          const span = document.createElement("span");
          span.className = "tok-credible";
          span.textContent = t.text;
          span.title = `Credibility Marker: ${t.reason} (Weight: +${t.weight})`;
          container.appendChild(span);
        }
      }
    });
  }

  // Heatmap Filter buttons
  const heatmapFilterBtns = document.querySelectorAll(".heatmap-filter-btn");
  heatmapFilterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      heatmapFilterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeHighlightFilter = btn.dataset.filter;
      if (currentAnalysis) {
        renderTokenHeatmap(currentAnalysis.token_highlights);
      }
    });
  });

  // Render Analytics Tab
  function renderAnalyticsTab(data) {
    const ling = data.linguistic_analysis;
    if (!ling) return;

    document.getElementById("metric-sensationalism").textContent = `${Math.round(ling.sensationalism_score * 100)}%`;
    document.getElementById("metric-readability").textContent = `${ling.flesch_reading_ease} / 100`;
    document.getElementById("metric-diversity").textContent = `${Math.round(ling.lexical_diversity * 100)}%`;
    document.getElementById("metric-words").textContent = ling.word_count;
    document.getElementById("metric-sentences").textContent = ling.sentence_count;
    document.getElementById("metric-uppercase").textContent = `${Math.round(ling.uppercase_ratio * 100)}%`;
    document.getElementById("metric-attributions").textContent = ling.attributions_found;
    document.getElementById("metric-hearsay").textContent = ling.hearsay_signals;

    // Domain Trust Card
    const dInfo = ling.domain_info;
    document.getElementById("domain-badge-name").textContent = dInfo.domain;
    document.getElementById("domain-badge-type").textContent = dInfo.category;
    document.getElementById("domain-badge-trust").textContent = `${Math.round(dInfo.trust * 100)}% Trust`;
  }

  // Batch CSV Upload Handler
  const dropzone = document.getElementById("csv-dropzone");
  const fileInput = document.getElementById("csv-file-input");

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files.length) {
        handleBatchFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) {
        handleBatchFile(fileInput.files[0]);
      }
    });
  }

  let batchExportData = [];

  async function handleBatchFile(file) {
    if (!file.name.endsWith(".csv")) {
      showToast("Please upload a .csv file.", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const progressBox = document.getElementById("batch-progress-box");
    if (progressBox) progressBox.style.display = "block";

    try {
      const resp = await fetch("/api/batch", {
        method: "POST",
        body: formData
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Batch processing error.");
      }

      const result = await resp.json();
      batchExportData = result.items;

      // Update Summary Cards
      document.getElementById("batch-stat-total").textContent = result.total_processed;
      document.getElementById("batch-stat-real").textContent = result.real_count;
      document.getElementById("batch-stat-fake").textContent = result.fake_count;
      document.getElementById("batch-stat-avg").textContent = `${result.average_veracity_score}%`;

      // Render Table Rows
      renderBatchTable(result.items);
      showToast(`Batch completed: ${result.total_processed} items processed!`, "success");
    } catch (err) {
      showToast(err.message, "danger");
    } finally {
      if (progressBox) progressBox.style.display = "none";
    }
  }

  function renderBatchTable(items) {
    const tbody = document.getElementById("batch-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    items.forEach((item) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>#${item.row_id}</td>
        <td style="font-weight: 600;">${escapeHtml(item.title)}</td>
        <td>${escapeHtml(item.domain)}</td>
        <td><strong style="font-family: var(--font-mono);">${item.veracity_score}%</strong></td>
        <td><span class="verdict-badge ${item.verdict_badge}" style="font-size: 0.72rem; padding: 2px 8px;">${item.verdict}</span></td>
        <td>${item.risk_level}</td>
      `;
      tbody.appendChild(tr);
    });

    const exportBtn = document.getElementById("btn-export-csv");
    if (exportBtn) exportBtn.style.display = "inline-flex";
  }

  // Export Batch CSV
  const btnExportCsv = document.getElementById("btn-export-csv");
  if (btnExportCsv) {
    btnExportCsv.addEventListener("click", () => {
      if (!batchExportData.length) return;
      const headers = ["Row", "Title", "Domain", "Veracity_Score", "Verdict", "Risk_Level"];
      const rows = batchExportData.map((d) => [
        d.row_id,
        `"${d.title.replace(/"/g, '""')}"`,
        `"${d.domain}"`,
        d.veracity_score,
        `"${d.verdict}"`,
        `"${d.risk_level}"`
      ]);

      const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `TruthGuard_Batch_Audit_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // Live Wire Scanner
  async function fetchLiveWire() {
    const list = document.getElementById("wire-list");
    if (!list) return;

    try {
      const resp = await fetch("/api/live-feed");
      const items = await resp.json();
      list.innerHTML = "";

      items.forEach((item) => {
        const div = document.createElement("div");
        div.className = "wire-item";
        div.innerHTML = `
          <div class="wire-left">
            <div class="wire-meta-row">
              <span class="wire-source-tag">${item.source} (${item.domain})</span>
              <span>•</span>
              <span>${item.time}</span>
              <span>•</span>
              <span style="color: var(--text-dim);">${item.category}</span>
            </div>
            <div class="wire-headline">${escapeHtml(item.headline)}</div>
          </div>
          <div class="wire-right">
            <div style="text-align: right;">
              <div style="font-family: var(--font-mono); font-weight: 700; font-size: 1.1rem;">${item.veracity_score}%</div>
              <span class="verdict-badge ${item.badge}" style="font-size: 0.68rem; padding: 2px 7px;">${item.verdict}</span>
            </div>
            <button class="btn btn-outline btn-sm wire-inspect-btn">Inspect</button>
          </div>
        `;

        div.querySelector(".wire-inspect-btn").addEventListener("click", () => {
          headlineInput.value = item.headline;
          articleTextInput.value = item.headline + " - Reporting as verified by network feeds.";
          domainInput.value = item.domain;
          // Switch to studio tab
          document.querySelector('.nav-tab-btn[data-target="tab-studio"]').click();
          analyzeContent();
        });

        list.appendChild(div);
      });
    } catch (err) {
      console.warn("Could not fetch wire items:", err);
    }
  }

  // Model Transparency Metrics
  async function fetchModelMetrics() {
    try {
      const resp = await fetch("/api/metrics");
      const m = await resp.json();

      document.getElementById("metric-accuracy-pac").textContent = `${m.accuracy_pac}%`;
      document.getElementById("metric-accuracy-lr").textContent = `${m.accuracy_lr}%`;
      document.getElementById("metric-precision").textContent = `${m.precision}%`;
      document.getElementById("metric-recall").textContent = `${m.recall}%`;
      document.getElementById("metric-f1").textContent = `${m.f1_score}%`;

      // Confusion Matrix
      const cm = m.confusion_matrix;
      document.getElementById("cm-tp").textContent = cm.true_positive;
      document.getElementById("cm-tn").textContent = cm.true_negative;
      document.getElementById("cm-fp").textContent = cm.false_positive;
      document.getElementById("cm-fn").textContent = cm.false_negative;

      // Render Top Predictive N-grams
      renderPredictiveWords("top-fake-words-list", m.top_fake_words, "fake");
      renderPredictiveWords("top-real-words-list", m.top_real_words, "real");
    } catch (err) {
      console.warn("Could not fetch model metrics:", err);
    }
  }

  function renderPredictiveWords(elemId, items, type) {
    const list = document.getElementById(elemId);
    if (!list || !items) return;
    list.innerHTML = "";

    const maxWeight = Math.max(...items.map((i) => i.weight)) || 1.0;

    items.slice(0, 10).forEach((item) => {
      const pct = Math.round((item.weight / maxWeight) * 100);
      const row = document.createElement("div");
      row.style.marginBottom = "0.45rem";
      const color = type === "real" ? "#10b981" : "#ef4444";

      row.innerHTML = `
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 2px;">
          <span>${escapeHtml(item.term)}</span>
          <span style="font-family: var(--font-mono); color: var(--text-dim);">${item.weight}</span>
        </div>
        <div style="background: rgba(255,255,255,0.06); height: 5px; border-radius: 99px; overflow: hidden;">
          <div style="width: ${pct}%; height: 100%; background: ${color}; border-radius: 99px;"></div>
        </div>
      `;
      list.appendChild(row);
    });
  }

  // Audit History
  async function fetchScanHistory() {
    try {
      const resp = await fetch("/api/history");
      const history = await resp.json();
      const tbody = document.getElementById("history-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      if (!history.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 2rem;">No scans performed yet in this session.</td></tr>`;
        return;
      }

      history.forEach((h) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><span style="font-family: var(--font-mono); color: var(--text-dim);">${h.id}</span></td>
          <td>${h.timestamp}</td>
          <td style="font-weight: 600;">${escapeHtml(h.title)}</td>
          <td>${escapeHtml(h.domain)}</td>
          <td><strong>${h.veracity_score}%</strong></td>
          <td><span class="verdict-badge ${h.verdict_badge}" style="font-size: 0.7rem; padding: 2px 7px;">${h.verdict}</span></td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.warn("Could not fetch history:", err);
    }
  }

  // Clear History Action
  const btnClearHistory = document.getElementById("btn-clear-history");
  if (btnClearHistory) {
    btnClearHistory.addEventListener("click", async () => {
      await fetch("/api/history", { method: "DELETE" });
      fetchScanHistory();
      showToast("Scan audit history cleared.", "info");
    });
  }

  // Certificate Modal Actions
  const btnExportCert = document.getElementById("btn-export-certificate");
  const certModal = document.getElementById("cert-modal");
  const btnCloseCert = document.getElementById("btn-close-cert");
  const btnPrintCert = document.getElementById("btn-print-cert");

  if (btnExportCert) {
    btnExportCert.addEventListener("click", () => {
      if (!currentAnalysis) {
        showToast("Please run an analysis first before generating a certificate.", "warning");
        return;
      }
      populateCertificate(currentAnalysis);
      if (certModal) certModal.classList.add("active");
    });
  }

  if (btnCloseCert && certModal) {
    btnCloseCert.addEventListener("click", () => {
      certModal.classList.remove("active");
    });
  }

  if (btnPrintCert) {
    btnPrintCert.addEventListener("click", () => {
      window.print();
    });
  }

  function populateCertificate(data) {
    document.getElementById("cert-id").textContent = data.id || "TG-" + Math.floor(100000 + Math.random() * 900000);
    document.getElementById("cert-date").textContent = data.timestamp || new Date().toLocaleString();
    document.getElementById("cert-headline").textContent = headlineInput.value || "Untitled Verified Content";
    document.getElementById("cert-score").textContent = `${data.veracity_score}%`;
    document.getElementById("cert-verdict").textContent = data.verdict;
    document.getElementById("cert-risk").textContent = data.risk_level;
  }

  // Dark/Light Theme Switcher
  const themeToggle = document.getElementById("btn-theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("light-mode");
      const isLight = document.body.classList.contains("light-mode");
      themeToggle.textContent = isLight ? "🌙" : "☀️";
    });
  }

  // Helper Utilities
  function setLoading(btn, loading, text) {
    if (!btn) return;
    if (loading) {
      btn.disabled = true;
      btn.dataset.prevHtml = btn.innerHTML;
      btn.innerHTML = `<span class="spinner"></span> <span>${text}</span>`;
    } else {
      btn.disabled = false;
      btn.innerHTML = text || btn.dataset.prevHtml;
    }
  }

  function showToast(msg, type = "info") {
    const toast = document.createElement("div");
    toast.style.position = "fixed";
    toast.style.bottom = "24px";
    toast.style.right = "24px";
    toast.style.zIndex = "9999";
    toast.style.padding = "0.75rem 1.25rem";
    toast.style.borderRadius = "8px";
    toast.style.fontSize = "0.85rem";
    toast.style.fontWeight = "600";
    toast.style.color = "#fff";
    toast.style.boxShadow = "0 8px 25px rgba(0,0,0,0.5)";
    toast.style.animation = "fadeIn 0.25s ease";

    if (type === "success") toast.style.background = "#059669";
    else if (type === "danger") toast.style.background = "#dc2626";
    else if (type === "warning") toast.style.background = "#d97706";
    else toast.style.background = "#2563eb";

    toast.textContent = msg;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Auto-analyze first sample on startup for immediate "wow" effect!
  setTimeout(() => {
    if (sampleArticles.length > 0) {
      loadSample(sampleArticles[0]);
    }
  }, 400);
});
