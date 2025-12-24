# 🚀 TechFiesta - Project Submission Report

**Project Name:** Fake Transaction Detector (FTD)
**Theme:** Fintech / Security & Surveillance
**Domain:** AI/ML & Cybersecurity

---

## 1. 🎯 Problem Statement
**Title:** Detection of Fraudulent Financial Transactions in Real-Time.
**Description:**
With the exponential rise in digital payments (UPI, Wallets, NetBanking), financial fraud has become sophisticated. Traditional rule-based systems fail to catch novel fraud patterns, while "Black Box" AI models lack transparency, making it hard for investigators to trust the flags. There is a critical need for a **Hybrid, Explainable, and Real-time** fraud detection system.

---

## 2. 💡 Proposed Solution
**"Fake Transaction Detector"** is a Next-Gen Fraud Intelligence Platform that combines the speed of **Deterministic Rules** with the adaptability of **Unsupervised Machine Learning** and **Graph Network Analysis**.

### 🔑 Key Innovations (USP):
1.  **Hybrid Scoring Engine:** Fuses scores from three independent analyzing agents (Rules + ML + Graph) for maximum accuracy.
2.  **Glass-Box Explainability:** Unlike standard AI, our system tells you *WHY* a transaction is fraud using **SHAP/LIME** (e.g., "Transaction amount is 500% higher than user's daily average").
3.  **Graph Anomaly Detection:** Detects complex money laundering rings (Cycles) that individual transaction analysis misses.
4.  **Dark Neo-Fintech Dashboard:** A high-performance, judge-friendly UI designed for security analysts.

---

## 3. 🏗️ System Architecture

### 📐 Visual Architecture Diagram
```mermaid
graph TD
    subgraph Client_Side [💻 Frontend Layer]
        UI[React/Flask UI<br/>(Dark Neo-Fintech Dashboard)]
        Judge[Judge Mode Interface]
    end

    subgraph Server_Side [⚙️ Backend & Processing]
        API[Flask API Server]
        Auth[Auth Middleware]
        
        subgraph Analysis_Engine [🧠 The Triple-Engine Brain]
            direction TB
            DDIE[DDIE Agent<br/>(Deterministic Rules)]
            UAIC[UAIC Agent<br/>(Isolation Forest ML)]
            Graph[Graph Agent<br/>(NetworkX Cycles)]
        end
        
        Scorer[⚖️ HybridScorer<br/>(Weighted Consensus)]
        Explain[💡 Explainability Module<br/>(SHAP/LIME)]
    end

    subgraph Data_Layer [💾 Data Persistence]
        CSV[(CSV Transaction Logs)]
        Cache[(In-Memory Cache)]
    end

    %% Data Flow
    UI -->|Upload CSV| API
    Judge -->|Verify Txn| API
    
    API -->|Raw Data| Analysis_Engine
    API -->|Fetch Data| Data_Layer
    
    DDIE -->|Rule Score| Scorer
    UAIC -->|Anomaly Score| Scorer
    Graph -->|Graph Score| Scorer
    
    Scorer -->|Final Score| Explain
    Analysis_Engine -->|Ctx| Explain
    
    Explain -->|JSON Result| UI
    
    style Client_Side fill:#1a1a2a,stroke:#00d4ff,stroke-width:2px,color:#fff
    style Analysis_Engine fill:#2d1b4e,stroke:#bd00ff,stroke-width:2px,color:#fff
    style Scorer fill:#ff9100,stroke:#ff9100,stroke-width:2px,color:#000
    style UI fill:#0b0b14,stroke:#00d4ff,color:#fff
```

The system follows a micro-modular approach:
1.  **Input Layer:** Transaction Logs (CSV) or Real-time Stream representing UPI/Banking gateways.
2.  **Processing Layer (The Brain):**
    *   **DDIE (Deterministic Data Integrity Engine):** Checks strict constraints (e.g., "Amount < 0").
    *   **UAIC (User Anomaly Intelligence Component):** An Isolation Forest model that learns user behavior profiles.
    *   **NetworkX Graph Engine:** Maps User-to-User flows to find suspicious loops.
3.  **Decision Layer:** A `HybridScorer` aggregates weights dynamically based on data confidence.
4.  **Presentation Layer:** React/Flask dashboard with real-time alerts.

---

## 4. 🛠️ Technology Stack
| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Robust data processing, easy ML integration. |
| **Frontend** | HTML5, Vanilla CSS, JS | High-performance, custom "Neo-Fintech" UI. |
| **ML Models** | Scikit-Learn (Isolation Forest) | Unsupervised learning (no labeled fraud data needed). |
| **Graph Logic** | NetworkX | Efficient cycle detection for money laundering. |
| **Explainability**| SHAP, LIME | Industry standard for model interpretability. |
| **Data Processing**| Pandas, NumPy | High-speed vector operations. |

---

## 5. 📊 Methodology / Process Flow
1.  **Data Ingestion:** User uploads a CSV of transactions.
2.  **Preprocessing:** System cleans data, handles missing values, and normalizes amounts.
3.  **Parallel Analysis:**
    *   *Agent 1 (Rules):* Flags impossible scenarios.
    *   *Agent 2 (ML):* Compares current txn vs history.
    *   *Agent 3 (Graph):* Checks connectivity patterns.
4.  **Consensus Voting:** The `HybridScorer` calculates a weighted `final_score`.
5.  **Reporting:** Dashboard displays the "Fraud Probability" with a natural language explanation.

---

## 6. 🔮 Future Scope
*   **Blockchain Integration:** To create an immutable ledger of flagged fraudsters.
*   **Real-time UPI API Hook:** Direct integration with payment gateways for sub-second blocking.
*   **Federated Learning:** To learn from fraud patterns across multiple banks without sharing user privacy data.

---

## 7. 📸 Use Cases
1.  **Bank Backend Ops:** Batch processing of daily logs to flag suspicious accounts.
2.  **Live Monitoring:** Real-time dashboard for security operations centers (SOC).
3.  **Forensic Audit:** Investigators using the "Judge Mode" to explain past fraud.

---
