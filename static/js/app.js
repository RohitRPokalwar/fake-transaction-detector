// Fake Transaction Detector Frontend Logic

document.addEventListener("DOMContentLoaded", function () {
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const loader = document.getElementById("terminalLoader");
  const initialLoader = document.getElementById("initialLoader");
  const errorDiv = document.getElementById("error");
  const resultsDiv = document.getElementById("results");
  const downloadBtn = document.getElementById("downloadBtn");
  const showAnomalousOnly = document.getElementById("showAnomalousOnly");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");
  const detailsModal = document.getElementById("detailsModal");
  const modalBody = document.getElementById("modalBody");
  const closeModal = document.querySelector(".close");

  // New Elements
  const downloadReportBtn = document.getElementById("downloadReportBtn");
  const userProfileModal = document.getElementById("userProfileModal");
  const userProfileBody = document.getElementById("userProfileBody");
  const closeProfileModal = document.querySelector(".close-profile");
  const userRiskBadge = document.getElementById("userRiskBadge");

  // CSV Requirements & Terminal Error Elements
  const requirementsBtn = document.getElementById("requirementsBtn");
  const requirementsModal = document.getElementById("requirementsModal");
  const closeRequirements = document.querySelectorAll(".close-requirements");
  const terminalErrorModal = document.getElementById("terminalErrorModal");
  const closeTerminalBtn = document.getElementById("closeTerminalBtn");
  const terminalErrorList = document.getElementById("terminalErrorList");

  // Progress elements
  const progressText = document.getElementById("progressText");
  const progressFill = document.getElementById("progressFill");
  let streamingIndicator = document.getElementById("streamingIndicator");

  // Global Data
  let selectedFile = null;
  let currentFileId = null;
  let allResults = [];
  let scoreChart = null;
  let anomalyChart = null;
  let stats = null;
  let hasAlertedForCSV = false;

  // Initialize
  setupEventListeners();
  runInitialLoader();

  function runInitialLoader() {
    const initialLoader = document.getElementById("initialLoader");
    const textDiv = document.getElementById("bootText");

    if (!initialLoader || !textDiv) {
      if (initialLoader) initialLoader.style.display = "none";
      return;
    }

    const steps = [
      "> Initializing VIGILO Intelligence Engine...",
      "> Loading Transaction Behavior Models...",
      "> Deploying Anomaly Detection Pipeline...",
      "> VIGILO SYSTEM READY.",
    ];

    let stepIndex = 0;

    // Clear previous text (important if re-run)
    textDiv.textContent = "";

    // Print first line immediately
    textDiv.textContent += steps[stepIndex] + "\n";
    stepIndex++;

    const interval = setInterval(() => {
      if (stepIndex < steps.length) {
        textDiv.textContent += steps[stepIndex] + "\n";
        stepIndex++;
      } else {
        clearInterval(interval);

        setTimeout(() => {
          initialLoader.style.opacity = "0";
          initialLoader.style.transition = "opacity 0.5s ease";

          setTimeout(() => {
            initialLoader.style.display = "none";
          }, 500);
        }, 800);
      }
    }, 2000);
  }

  function setupEventListeners() {
    // File upload handling
    uploadArea.addEventListener("click", () => fileInput.click());

    uploadArea.querySelector(".upload-link").addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.click();
    });

    fileInput.addEventListener("change", handleFileSelect);
    uploadArea.addEventListener("dragover", handleDragOver);
    uploadArea.addEventListener("dragleave", handleDragLeave);
    uploadArea.addEventListener("drop", handleDrop);

    // Analysis
    analyzeBtn.addEventListener("click", analyzeFile);

    // Filters and Sorting
    showAnomalousOnly.addEventListener("change", applyFiltersAndSort);
    searchInput.addEventListener("input", applyFiltersAndSort);
    sortSelect.addEventListener("change", applyFiltersAndSort);

    // Downloads
    downloadBtn.addEventListener("click", downloadCSV);
    downloadReportBtn.addEventListener("click", generateAndDownloadReport);

    // Transaction Details Modal
    if (closeModal) {
      closeModal.addEventListener("click", () => {
        detailsModal.style.display = "none";
      });
    }

    window.addEventListener("click", (e) => {
      if (e.target === detailsModal) {
        detailsModal.style.display = "none";
      }
    });

    // User Profile Modal
    if (closeProfileModal) {
      closeProfileModal.addEventListener("click", () => {
        userProfileModal.style.display = "none";
      });
    }

    window.addEventListener("click", (e) => {
      if (e.target === userProfileModal) {
        userProfileModal.style.display = "none";
      }
    });

    // CSV Requirements Modal
    if (requirementsBtn) {
      requirementsBtn.addEventListener("click", () => {
        requirementsModal.style.display = "block";
      });
    }

    if (closeRequirements) {
      closeRequirements.forEach((el) => {
        el.addEventListener("click", () => {
          requirementsModal.style.display = "none";
        });
      });
    }

    window.addEventListener("click", (e) => {
      if (e.target === requirementsModal) {
        requirementsModal.style.display = "none";
      }
    });

    // Terminal Error Modal
    if (closeTerminalBtn) {
      closeTerminalBtn.addEventListener("click", () => {
        terminalErrorModal.style.display = "none";
      });
    }

    window.addEventListener("click", (e) => {
      if (e.target === terminalErrorModal) {
        terminalErrorModal.style.display = "none";
      }
    });

    // --- Judge Mode Listeners ---
    const judgeBtn = document.getElementById("judgeBtn");
    const judgeModal = document.getElementById("judgeModal");
    const closeJudge = document.querySelector(".close-judge");
    const judgeScanBtn = document.getElementById("judgeScanBtn");

    if (judgeBtn) {
      judgeBtn.addEventListener("click", () => {
        judgeModal.style.display = "flex";
        // Reset previous results
        document.getElementById("judgeResult").style.display = "none";
        document.getElementById("judgeResultContent").style.display = "none";
        document.getElementById("judgeAmount").value = "";
        document.getElementById("judgeLocation").value = "";
      });
    }

    if (closeJudge) {
      closeJudge.addEventListener("click", () => {
        judgeModal.style.display = "none";
      });
    }

    window.addEventListener("click", (e) => {
      if (e.target === judgeModal) {
        judgeModal.style.display = "none";
      }
    });

    if (judgeScanBtn) {
      judgeScanBtn.addEventListener("click", handleJudgeScan);
    }
  }

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      validateAndSetFile(file);
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add("dragover");
  }

  function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
  }

  function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) {
      validateAndSetFile(file);
    }
  }

  async function validateAndSetFile(file) {
    if (!file.name.endsWith(".csv")) {
      showError("Please select a CSV file");
      return;
    }

    try {
      await validateCSV(file);
    } catch (errors) {
      showTerminalError(errors);
      fileInput.value = ""; // Reset input
      return;
    }

    selectedFile = file;
    uploadArea.querySelector(
      "p"
    ).innerHTML = `File selected: <strong>${file.name}</strong>`;
    analyzeBtn.disabled = false;
    hideError();
  }

  function validateCSV(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function (e) {
        const text = e.target.result;
        const lines = text.split("\n");
        if (lines.length < 1) {
          reject(["Empty file"]);
          return;
        }

        const header = lines[0].trim().split(",");
        const requiredColumns = [
          "transaction_id",
          "user_id",
          "recipient_id",
          "amount",
          "timestamp",
          "location",
        ];
        // Simple check: ensure all required columns are present in the header
        const headerTrimmed = header.map((h) => h.trim());
        const missingColumns = requiredColumns.filter(
          (col) => !headerTrimmed.includes(col)
        );

        if (missingColumns.length > 0) {
          reject(missingColumns);
        } else {
          resolve(true);
        }
      };
      reader.onerror = function () {
        reject(["Error reading file"]);
      };
      reader.readAsText(file);
    });
  }

  function showTerminalError(errors) {
    if (terminalErrorList && terminalErrorModal) {
      terminalErrorList.innerHTML = errors
        .map((err) => `> MISSING_COLUMN: ${err}`)
        .join("<br>");
      terminalErrorModal.style.display = "block";
    }
  }

  async function analyzeFile() {
    if (!selectedFile) return;

    showLoader();
    hideError();
    resultsDiv.style.display = "block";

    allResults = [];
    destroyCharts();
    initCharts(); // Re-initialize charts for new analysis

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // 1. Upload
      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const uploadData = await uploadResponse.json();
      if (!uploadResponse.ok)
        throw new Error(uploadData.error || "Upload failed");

      const fileId = uploadData.file_id;
      currentFileId = fileId;

      // 2. Analyze (Non-streaming)
      const analyzeResponse = await fetch(`/api/analyze/${fileId}`);
      const analyzeData = await analyzeResponse.json();

      if (!analyzeResponse.ok)
        throw new Error(analyzeData.error || "Analysis failed");

      allResults = analyzeData.results || [];
      const stats = analyzeData.stats;

      // 3. UI Update
      updateStatsUI(stats);

      // Populate Charts
      if (scoreChart) {
        scoreChart.data.labels = allResults.map((_, i) => i + 1);
        scoreChart.data.datasets[0].data = allResults.map(
          (row) => row.final_score
        );
        scoreChart.update();
      }

      if (anomalyChart) {
        const anomCount = allResults.filter((r) => r.is_anomalous).length;
        const normCount = allResults.length - anomCount;
        anomalyChart.data.datasets[0].data = [normCount, anomCount];
        anomalyChart.update();
      }

      if (progressText) {
        progressText.innerHTML = `✅ Analysis Complete: ${allResults.length} transactions processed.`;
      }
      if (progressFill) progressFill.style.width = "100%";

      applyFiltersAndSort();
      hideLoader();
    } catch (error) {
      hideLoader();
      showError(error.message);
    }
  }

  function initCharts() {
    const scoreCanvas = document.getElementById("scoreChart");
    const anomalyCanvas = document.getElementById("anomalyChart");

    if (scoreCanvas) {
      scoreChart = new Chart(scoreCanvas.getContext("2d"), {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "Final Scores",
              data: [],
              backgroundColor: "rgba(0, 242, 234, 0.6)",
              borderColor: "#00f2ea",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: "Distribution of Anomaly Scores" },
            legend: { display: false },
          },
          scales: { x: { display: false }, y: { beginAtZero: true, max: 1 } },
        },
      });
    }

    if (anomalyCanvas) {
      anomalyChart = new Chart(anomalyCanvas.getContext("2d"), {
        type: "doughnut",
        data: {
          labels: ["Normal", "Anomalous"],
          datasets: [
            {
              data: [0, 0],
              backgroundColor: ["#00ff9d", "#ff3b3b"],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: "Transaction Classification" },
            legend: { position: "bottom" },
          },
        },
      });
    }
  }

  function updateStatsUI(stats) {
    if (!stats) return;

    const totalTxnsEl = document.getElementById("totalTxns");
    const anomalousTxnsEl = document.getElementById("anomalousTxns");
    const anomalyRateEl = document.getElementById("anomalyRate");
    const avgAmountEl = document.getElementById("avgAmount");
    const activeUserEl = document.getElementById("activeUser");

    if (totalTxnsEl) totalTxnsEl.textContent = stats.total_transactions || 0;
    if (anomalousTxnsEl)
      anomalousTxnsEl.textContent = stats.anomalous_count || 0;
    if (anomalyRateEl) anomalyRateEl.textContent = stats.anomaly_rate || "0%";

    if (avgAmountEl && stats.mean_amount !== undefined) {
      avgAmountEl.textContent = `₹${parseFloat(
        stats.mean_amount
      ).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    }
    if (activeUserEl && stats.most_active_user_id) {
      activeUserEl.textContent = stats.most_active_user_id;
    }
  }

  function createRowElement(row) {
    const tr = document.createElement("tr");
    if (row.is_anomalous) tr.classList.add("anomalous");

    const amount = parseFloat(row.amount || 0);
    let statusText = row.is_anomalous ? "Anomalous" : "Normal";
    let statusStyle = row.is_anomalous
      ? "color: #ff3b3b; font-weight: bold;"
      : "color: #00ff9d;";

    tr.innerHTML = `
            <td>${row.transaction_id || "N/A"}</td>
            <td>${row.user_id || "N/A"}</td>
            <td>₹${isNaN(amount) ? "0" : amount.toLocaleString("en-IN")}</td>
            <td>${row.timestamp || "N/A"}</td>
            <td>${
              typeof row.final_score === "number"
                ? row.final_score.toFixed(3)
                : "N/A"
            }</td>
            <td><span style="${statusStyle}">${statusText}</span></td>
        `;

    tr.addEventListener("click", (e) => {
      const colIndex = e.target.cellIndex;
      if (colIndex === 1) {
        e.stopPropagation();
        showUserProfile(row.user_id);
      } else if (colIndex === 4) {
        showTransactionDetails(row, true);
      } else if (colIndex === 5) {
        showTransactionDetails(row, false);
        setTimeout(() => {
          document.getElementById("askAgentBtn")?.click();
        }, 300);
      } else {
        showTransactionDetails(row, false);
      }
    });

    return tr;
  }

  function applyFiltersAndSort() {
    let filteredResults = [...allResults];

    // Apply anomalous filter
    if (showAnomalousOnly.checked) {
      filteredResults = filteredResults.filter((r) => r.is_anomalous);
    }

    // Apply search filter
    const searchTerm = searchInput.value.toLowerCase();
    if (searchTerm) {
      filteredResults = filteredResults.filter((r) =>
        (r.user_id || "").toString().toLowerCase().includes(searchTerm)
      );
    }

    // Apply sorting
    const sortBy = sortSelect.value;
    if (sortBy) {
      filteredResults.sort((a, b) => {
        let aVal = a[sortBy];
        let bVal = b[sortBy];

        if (sortBy === "status") {
          aVal = a.is_anomalous ? "Anomalous" : "Normal";
          bVal = b.is_anomalous ? "Anomalous" : "Normal";
        }

        if (typeof aVal === "string") {
          return aVal.localeCompare(bVal);
        }
        return (aVal || 0) - (bVal || 0);
      });
    }

    // Update table
    const tbody = document.querySelector("#resultsTable tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    // Limit display to 500 rows max
    const displayResults = filteredResults.slice(0, 500);

    displayResults.forEach((row) => {
      const tr = createRowElement(row);
      tbody.appendChild(tr);
    });
  }

  async function showUserProfile(userId) {
    if (!currentFileId || !userId) return;

    userProfileModal.style.display = "flex";
    userProfileBody.innerHTML =
      '<div class="loader-small">Loading profile...</div>';
    userRiskBadge.innerHTML = "";

    try {
      const response = await fetch(
        `/api/user_profile/${currentFileId}/${encodeURIComponent(userId)}`
      );
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      // Render Profile
      const riskClass =
        data.risk_score > 0.7
          ? "high-risk"
          : data.risk_score > 0.3
          ? "medium-risk"
          : "low-risk";
      const riskLabel =
        data.risk_score > 0.7
          ? "CRITICAL"
          : data.risk_score > 0.3
          ? "SUSPICIOUS"
          : "LOW RISK";

      userRiskBadge.innerHTML = `<span class="badge ${riskClass}">${riskLabel}</span>`;

      let historyHtml = "";
      if (data.history && data.history.length > 0) {
        historyHtml = `
          <h3>Suspicious Activity History</h3>
          <div class="history-list">
            ${data.history
              .map(
                (h) => `
                <div class="history-item">
                  <div class="history-header">
                    <span class="history-id">#${h.transaction_id}</span>
                    <span class="history-amount">₹${parseFloat(
                      h.amount
                    ).toLocaleString("en-IN")}</span>
                  </div>
                  <div class="history-reason">${h.explanation}</div>
                </div>
              `
              )
              .join("")}
          </div>
        `;
      } else {
        historyHtml =
          '<p class="clean-record">No suspicious activity recorded.</p>';
      }

      userProfileBody.innerHTML = `
        <div class="profile-stats">
          <div class="stat-box">
            <label>Risk Score</label>
            <div class="stat-value">${data.risk_score.toFixed(3)}</div>
          </div>
          <div class="stat-box">
            <label>Total Volume</label>
            <div class="stat-value">₹${data.total_volume.toLocaleString(
              "en-IN",
              { minimumFractionDigits: 2, maximumFractionDigits: 2 }
            )}</div>
          </div>
          <div class="stat-box">
            <label>Transactions</label>
            <div class="stat-value">${data.transaction_count}</div>
          </div>
          <div class="stat-box">
            <label>Anomalies</label>
            <div class="stat-value text-danger">${data.suspicious_count}</div>
          </div>
        </div>
        ${historyHtml}

        <div style="text-align: center; margin-top: 20px;">
            <button id="filterUserBtn" class="btn-primary">Show All Transactions</button>
        </div>
      `;

      // Add event listener for the filter button
      const filterBtn = document.getElementById("filterUserBtn");
      if (filterBtn) {
        filterBtn.addEventListener("click", () => {
          // Set search input to user ID
          if (searchInput) {
            searchInput.value = userId;
            // Trigger input event to update filters
            searchInput.dispatchEvent(new Event("input"));
          }
          // Close the modal
          userProfileModal.style.display = "none";
        });
      }
    } catch (error) {
      userProfileBody.innerHTML = `<p class="error-text">Failed to load profile: ${error.message}</p>`;
    }
  }
  function downloadCSV() {
    if (!allResults || allResults.length === 0) return;

    // Filter only Anomalous based on `is_anomalous` flag
    const anomalousRows = allResults.filter((r) => r.is_anomalous);

    if (anomalousRows.length === 0) {
      alert("No anomalous transactions found in the analysis results.");
      return;
    }

    // CSV Header
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent +=
      "Transaction ID,User ID,Recipient ID,Amount,Timestamp,Location,Final Score,Status,Reason\n";

    anomalousRows.forEach((row) => {
      // Logic to strip HTML from explanation to get plain text reason
      let reason = "Anomalous";
      if (row.explanation) {
        // Simple regex to strip HTML tags and clean up text
        let temp = row.explanation.replace(/<[^>]*>/g, " "); // Replace tags with space
        temp = temp.replace(/&nbsp;/g, " ");
        temp = temp.replace(/[\r\n]+/g, " "); // Remove newlines
        temp = temp.replace(/\s+/g, " ").trim(); // Collapse spaces
        reason = temp.replace(/,/g, ";"); // Replace commas to avoid breaking CSV
      }

      // CSV Row
      // Try common variations for Recipient ID
      const rId =
        row.recipient_id ||
        row.receiver_id ||
        row.recipient ||
        row["Receiver ID"] ||
        row["Recipient ID"] ||
        "N/A";
      csvContent += `${row.transaction_id},${row.user_id},${rId},${
        row.amount
      },${row.timestamp},${row.location},${(row.final_score || 0).toFixed(
        3
      )},Anomalous,${reason}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "Detected_Anomalies_Only.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  async function generateAndDownloadReport() {
    if (!currentFileId) return;

    const originalText = downloadReportBtn.innerHTML;
    downloadReportBtn.innerHTML = "Compiling Intelligence…";
    downloadReportBtn.disabled = true;

    try {
      const response = await fetch(`/api/generate_report/${currentFileId}`);
      const data = await response.json();

      if (data.error) throw new Error(data.error);

      // Trigger download
      const a = document.createElement("a");
      a.href = data.report_url;
      a.download = `Intelligence_Briefing_${currentFileId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      // Success Message
      alert("Intelligence report downloaded successfully");
    } catch (error) {
      showError(`Report generation failed: ${error.message}`);
    } finally {
      downloadReportBtn.innerHTML = originalText;
      downloadReportBtn.disabled = false;
    }
  }

  function showTransactionDetails(row, showBreakdown = false) {
    const finalScore =
      typeof row.final_score === "number" ? row.final_score.toFixed(3) : "N/A";

    const modalTitle = document.querySelector("#detailsModal h2");
    if (modalTitle) {
      modalTitle.innerText = showBreakdown
        ? "🛡️ Algorithm Transparency Report"
        : "🔍 Transaction Intelligence Dossier";
    }

    modalBody.innerHTML = `
      <div id="fullDossierGrid" class="detail-grid" style="display: ${
        showBreakdown ? "none" : "grid"
      }">
        <div class="detail-item">
          <label>Transaction ID</label>
          <span>${row.transaction_id || "N/A"}</span>
        </div>
        <div class="detail-item">
          <label>User ID</label>
          <span>${row.user_id || "N/A"}</span>
        </div>
        <div class="detail-item">
          <label>Recipient ID</label>
          <span>${row.recipient_id || row.receiver_id || "N/A"}</span>
        </div>
        <div class="detail-item">
          <label>Amount</label>
          <span>₹${parseFloat(row.amount || 0).toLocaleString("en-IN")}</span>
        </div>
        <div class="detail-item">
          <label>Timestamp</label>
          <span>${row.timestamp || "N/A"}</span>
        </div>
        <div class="detail-item">
          <label>Final Score</label>
          <span class="${
            row.is_anomalous ? "text-danger" : "text-success"
          }">${finalScore}</span>
        </div>
        <div class="detail-item">
          <label>Status</label>
          <span class="status-badge ${
            row.is_anomalous ? "status-anomalous" : "status-normal"
          }">
            ${row.is_anomalous ? "ANOMALOUS" : "NORMAL"}
          </span>
        </div>
      </div>

      <div class="agent-section">
        <div class="breakdown-header" style="display: ${
          showBreakdown ? "block" : "none"
        }">📊 SCORING DECOMPOSITION (INTERNAL BREAKDOWN)</div>
        <div id="scoreDetails" class="score-details-container" style="display: ${
          showBreakdown ? "block" : "none"
        }">
          ${
            row.details
              ? `
            <div class="score-row">
              <span class="score-label">Rule Engine Risk:</span>
              <div class="score-value-group">
                <span class="score-value">${(
                  row.details.rule_score * 100
                ).toFixed(0)}%</span>
                <span class="score-weight">(Weight: ${
                  row.details.weights.rule
                })</span>
              </div>
            </div>
            <div class="score-row">
              <span class="score-label">AI Behavioral Risk:</span>
              <div class="score-value-group">
                <span class="score-value">${(
                  row.details.ml_score * 100
                ).toFixed(0)}%</span>
                <span class="score-weight">(Weight: ${
                  row.details.weights.ml
                })</span>
              </div>
            </div>
            <div class="score-row">
              <span class="score-label">Graph Structural Risk:</span>
              <div class="score-value-group">
                <span class="score-value">${(
                  row.details.graph_score * 100
                ).toFixed(0)}%</span>
                <span class="score-weight">(Weight: ${
                  row.details.weights.graph
                })</span>
              </div>
            </div>
            <div class="score-divider"></div>
            <div class="score-row total">
              <span class="score-label">Calculated Final Intensity:</span>
              <div class="score-value-group">
                <span class="score-value">${(row.final_score * 100).toFixed(
                  1
                )}%</span>
              </div>
            </div>
            <p style="margin-top: 15px; font-size: 0.75rem; color: #888; font-style: italic;">
              * The final score is a weighted combination of deterministic rules, ML behavior models, and graph structural analysis.
            </p>
          `
              : '<p style="color: #666; font-size: 0.8rem;">Historical data: Calculation weights not captured.</p>'
          }
        </div>
        
        <div class="modal-action-buttons" style="display: flex; gap: 10px;">
            ${
              showBreakdown
                ? `<button id="btnShowDossier" class="btn-secondary" style="flex: 1;">VIEW TRANSACTION DOSSIER</button>`
                : ""
            }
            <button id="askAgentBtn" class="btn-agent" style="flex: ${
              showBreakdown ? "2" : "1"
            };">
              <span class="icon">🤖</span> AI INVESTIGATOR: EXPLAIN WHY
            </button>
        </div>

        <div id="agentResponse" class="agent-response" style="display: none;">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
          <div class="response-text"></div>
        </div>

        <!-- NEW: Network Topology Map for Graph Anomalies -->
        <div id="topologyContainer" class="topology-container" style="display: none;">
            <div class="topology-header">🕸️ NETWORK TOPOLOGY MAP (LAUNDERING CYCLE)</div>
            <div id="topologyMap" class="topology-map"></div>
        </div>

        ${
          row.is_anomalous
            ? `
        <div class="protocol-section">
            <div class="protocol-header">🛡️ BANK MANAGER RESPONSE PROTOCOLS</div>
            <div class="protocol-actions">
                <button class="btn-protocol freeze" onclick="simulateAction('FREEZE', '${row.user_id}')">
                    <span class="icon">❄️</span> FREEZE ACCOUNT
                </button>
                <button class="btn-protocol approve" onclick="simulateAction('APPROVE', '${row.transaction_id}')">
                    <span class="icon">✅</span> ALLOW EXCEPTION
                </button>
                <button class="btn-protocol report" onclick="simulateAction('FINCEN', '${row.transaction_id}')">
                    <span class="icon">🏛️</span> REPORT TO FINCEN
                </button>
            </div>
            <div id="protocolFeedback" class="protocol-feedback" style="display: none;"></div>
        </div>
        `
            : ""
        }
      </div>
    `;

    detailsModal.style.display = "flex";

    // Listeners for new buttons
    const btnDossier = document.getElementById("btnShowDossier");
    if (btnDossier) {
      btnDossier.addEventListener("click", () =>
        showTransactionDetails(row, false)
      );
    }

    const btnAgent = document.getElementById("askAgentBtn");
    const responseDiv = document.getElementById("agentResponse");
    const typingDiv = responseDiv.querySelector(".typing-indicator");
    const textDiv = responseDiv.querySelector(".response-text");

    btnAgent.addEventListener("click", () => {
      btnAgent.disabled = true;
      responseDiv.style.display = "block";
      setTimeout(() => {
        typingDiv.style.display = "none";
        textDiv.innerHTML = `<strong>Agent Analysis:</strong><br>${
          row.explanation || "No explanation provided."
        }`;
        textDiv.classList.add("visible");
      }, 1000);
    });

    // Toggle Topology Map if loop data exists
    if (
      row.details &&
      row.details.node_path &&
      row.details.node_path.length > 0
    ) {
      document.getElementById("topologyContainer").style.display = "block";
      renderTopologyMap(row.details.node_path);
    }
  }

  function renderTopologyMap(nodes) {
    const container = document.getElementById("topologyMap");
    if (!container) return;

    container.innerHTML = "";
    const width = container.clientWidth || 400;
    const height = 220;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 70;

    let svg = `<svg viewBox="0 0 ${width} ${height}" class="topology-svg">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="25" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#ff3b3b" />
                </marker>
            </defs>`;

    const nodePos = nodes.map((node, i) => {
      const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
      return {
        name: node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    // Draw edges (red arrows)
    for (let i = 0; i < nodePos.length; i++) {
      const start = nodePos[i];
      const end = nodePos[(i + 1) % nodePos.length];
      svg += `<path d="M ${start.x} ${start.y} L ${end.x} ${end.y}" 
                          class="edge-path" 
                          marker-end="url(#arrowhead)" />`;
    }

    // Draw nodes (glowing circles)
    nodePos.forEach((p) => {
      svg += `
                <circle cx="${p.x}" cy="${
        p.y
      }" r="15" class="node-circle node-pulse" />
                <text x="${p.x}" y="${
        p.y + 30
      }" text-anchor="middle" class="node-text">${p.name}</text>
            `;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  // --- Action Simulations ---
  window.simulateAction = function (type, id) {
    const feedback = document.getElementById("protocolFeedback");
    if (!feedback) return;

    feedback.style.display = "block";
    feedback.className = "protocol-feedback"; // reset classes

    let message = "";
    let audioFreq = 440;

    switch (type) {
      case "FREEZE":
        message = `> 🚨 PROTOCOL_ALPHA: Account ${id} has been SUSPENDED. Assets locked pending investigation.`;
        feedback.classList.add("danger-text");
        audioFreq = 220;
        break;
      case "APPROVE":
        message = `> ✅ PROTOCOL_BETA: Transaction ${id} marked as 'Manual Override Successful'. Anomaly cleared.`;
        feedback.classList.add("success-text");
        audioFreq = 660;
        break;
      case "FINCEN":
        message = `> 🏛️ PROTOCOL_GAMMA: Intelligence report for ${id} has been uplinked to FinCEN AML Database. Case ID: ${Math.random()
          .toString(36)
          .substring(7)
          .toUpperCase()}`;
        feedback.classList.add("info-text");
        audioFreq = 880;
        break;
    }

    feedback.innerHTML = `<span class="typing-text">${message}</span>`;

    // Simple Beep
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.frequency.value = audioFreq;
      g.gain.value = 0.05;
      osc.connect(g);
      g.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    } catch (e) {}
  };

  function destroyCharts() {
    if (scoreChart && typeof scoreChart.destroy === "function") {
      scoreChart.destroy();
      scoreChart = null;
    }
    if (anomalyChart && typeof anomalyChart.destroy === "function") {
      anomalyChart.destroy();
      anomalyChart = null;
    }
  }

  let terminalInterval;

  function showLoader() {
    const loader = document.getElementById("terminalLoader");
    const textDiv = document.getElementById("terminalLoaderText");
    if (!loader || !textDiv) return;

    loader.style.display = "flex"; // Use flex for centering logic in overlay
    if (analyzeBtn) analyzeBtn.disabled = true;

    // Reset text
    textDiv.innerHTML = "";

    const steps = [
      "> INITIALIZING_CORE_SYSTEMS...",
      "> ESTABLISHING_SECURE_UPLINK...",
      "> DECRYPTING_TRANSACTION_LOGS...",
      "> RUNNING_HEURISTIC_ANALYSIS...",
      "> EXECUTING_ISOLATION_FOREST_ALGORITHM...",
      "> SCANNING_FOR_GRAPH_ANOMALIES...",
      "> COMPILING_THREAT_INTELLIGENCE...",
    ];

    let stepIndex = 0;

    // Clear any existing interval
    if (terminalInterval) clearInterval(terminalInterval);

    // Show first step immediately
    textDiv.innerHTML += `<div class="step">${steps[0]}</div>`;
    stepIndex++;

    terminalInterval = setInterval(() => {
      if (stepIndex < steps.length) {
        textDiv.innerHTML += `<div class="step">${steps[stepIndex]}</div>`;
        stepIndex++;
      } else {
        clearInterval(terminalInterval);
      }
    }, 800);
  }

  function hideLoader() {
    const loader = document.getElementById("terminalLoader");
    if (loader) loader.style.display = "none";
    if (terminalInterval) clearInterval(terminalInterval);
    analyzeBtn.disabled = false;
  }

  function showError(message) {
    console.error(message);
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
  }

  function hideError() {
    errorDiv.style.display = "none";
  }

  async function handleJudgeScan() {
    const amount = document.getElementById("judgeAmount").value;
    const location = document.getElementById("judgeLocation").value;
    const txnId = document.getElementById("judgeTxnId").value;
    const userId = document.getElementById("judgeUserId").value;
    const timestamp = document.getElementById("judgeTimestamp").value;

    if (!amount || !location || !userId) {
      alert("Please enter Amount, Location, and User ID.");
      return;
    }

    const scanBtn = document.getElementById("judgeScanBtn");
    const resultDiv = document.getElementById("judgeResult");
    const spinner = document.getElementById("judgeSpinner");
    const content = document.getElementById("judgeResultContent");

    if (scanBtn) scanBtn.disabled = true;
    if (resultDiv) resultDiv.style.display = "block";
    if (content) content.style.display = "none";
    if (spinner) spinner.style.display = "block";

    // Start Pipeline Animation
    const pipeline = document.getElementById("pipelineAnimation");
    if (pipeline) pipeline.style.display = "block";

    try {
      const body = {
        amount: parseFloat(amount),
        location: location,
        user_id: userId,
        transaction_id: txnId,
        timestamp: timestamp,
      };

      const response = await fetch("/api/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.error) throw new Error(data.error);

      // Show Result
      spinner.style.display = "none";
      content.style.display = "block";

      const statusEl = document.getElementById("judgeStatus");
      const scoreFill = document.getElementById("judgeScoreFill");
      const explanationEl = document.getElementById("judgeExplanation");

      if (data.is_anomalous) {
        statusEl.innerHTML = "❌ DETECTED: FAKE";
        statusEl.style.color = "#ff3b3b";
        scoreFill.style.width = "95%";
        scoreFill.style.backgroundColor = "#ff3b3b";
      } else {
        statusEl.innerHTML = "✅ VERIFIED: LEGIT";
        statusEl.style.color = "#00ff9d";
        scoreFill.style.width = "15%";
        scoreFill.style.backgroundColor = "#00ff9d";
      }

      explanationEl.innerHTML = data.explanation || "System check complete.";

      // Transparency / Risk Calculation
      const details = data.details;
      const calcContainer = document.getElementById("judgeCalculation");
      const calcDetails = document.getElementById("judgeCalcDetails");

      if (details && details.weights && calcContainer && calcDetails) {
        calcContainer.style.display = "block";
        const r = details.rule_score;
        const m = details.ml_score;
        const g = details.graph_score || 0;
        const w = details.weights;

        calcDetails.innerHTML = `
   Rule Risk:  ${(r * 100).toFixed(0).padStart(3)}%  [Weight: ${w.rule}] <br>
   AI Risk:    ${(m * 100).toFixed(0).padStart(3)}%  [Weight: ${w.ml}] <br>
   Graph Risk: ${(g * 100).toFixed(0).padStart(3)}%  [Weight: ${w.graph}] <br>
   ---------------------------- <br>
   TOTAL RISK: ${(data.final_score * 100).toFixed(1)}%  ${
          data.is_anomalous ? "(> THRESHOLD)" : "(SAFE)"
        }
                `;
      }

      // --- Real-Time Visuals ---
      if (data.is_anomalous) {
        // 1. Red Flashing Border
        const overlay = document.getElementById("flashOverlay");
        if (overlay) {
          overlay.style.animation = "flash-red 0.5s ease-in-out 3";
          setTimeout(() => {
            overlay.style.animation = "";
          }, 1500);
        }

        // 2. Warning Sound (Oscillator)
        playWarningSound();

        // 3. Fake Bank Alert
        showBankAlert();
      }
    } catch (e) {
      if (spinner) spinner.style.display = "none";
      alert("Scan failed: " + e.message);
      if (resultDiv) resultDiv.style.display = "none";
    } finally {
      if (scanBtn) scanBtn.disabled = false;
      // Stop Pipeline
      const pipeline = document.getElementById("pipelineAnimation");
      if (pipeline) pipeline.style.display = "none";
    }
  }

  // --- Interactive Control Logic ---
  const btnSwitchDevice = document.getElementById("btnSwitchDevice");
  const btnChangeLocation = document.getElementById("btnChangeLocation");
  const btnIncreaseAmount = document.getElementById("btnIncreaseAmount");

  if (btnSwitchDevice) {
    btnSwitchDevice.addEventListener("click", () => {
      // Simulate device switch by keeping amount/loc but adding a 'New Device' flag to UX or just re-scanning
      // For fun, we can append a device ID to the txn ID input to look "techy"
      const txnInput = document.getElementById("judgeTxnId");
      if (txnInput)
        txnInput.value = `DEV-${Math.floor(Math.random() * 9000) + 1000}`;
      handleJudgeScan();
    });
  }

  if (btnChangeLocation) {
    btnChangeLocation.addEventListener("click", () => {
      const locs = [
        "Lagos",
        "New York",
        "London",
        "Tokyo",
        "Mumbai",
        "Moscow",
        "Dubai",
      ];
      const locInput = document.getElementById("judgeLocation");
      if (locInput)
        locInput.value = locs[Math.floor(Math.random() * locs.length)];
      handleJudgeScan();
    });
  }

  if (btnIncreaseAmount) {
    btnIncreaseAmount.addEventListener("click", () => {
      const amtInput = document.getElementById("judgeAmount");
      if (amtInput) {
        let val = parseFloat(amtInput.value) || 1000;
        amtInput.value = val * 10;
      }
      handleJudgeScan();
    });
  }

  // --- Sound & Alert Helpers ---
  function playWarningSound() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sawtooth"; // Harsh sound
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.1);
      osc.frequency.linearRampToValueAtTime(440, ctx.currentTime + 0.2);
      osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.3);

      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
      console.log("Audio not supported");
    }
  }

  function showBankAlert() {
    const alertBox = document.getElementById("bankAlert");
    if (!alertBox) return;

    alertBox.classList.remove("hide");
    alertBox.classList.add("show");

    // Auto-hide after 6 seconds
    setTimeout(() => {
      alertBox.classList.remove("show");
      alertBox.classList.add("hide");
    }, 5500);

    // Fully remove after animation
    setTimeout(() => {
      alertBox.style.display = "none";
      alertBox.classList.remove("hide");
    }, 6000);
  }
});
