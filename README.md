# 🛡️ Fake Transaction Detector (FTD)

> **A Next-Gen Hybrid Fraud Detection System powered by Rules, Machine Learning, and Graph Analysis.**  
> *Built for TechFiesta 2026*

---

## 🌟 Overview
**Fake Transaction Detector** is a financial intelligence tool capable of identifying fraudulent patterns in real-time. Unlike traditional systems that rely solely on static rules or "black-box" AI, FTD uses a **Triple-Engine Architecture**:
1.  **Deterministic Rules (DDIE):** Catch obvious violations instantly.
2.  **Unsupervised ML (UAIC):** Detect subtle behavioral anomalies (Isolation Forest).
3.  **Graph Network Analysis:** Uncover hidden Money Laundering rings.

Most importantly, it provides **Explainable AI (XAI)**—telling you *why* a transaction was flagged (e.g., "Amount > 5x Daily Avg").

---

## 🚀 Key Features
*   **🕷️ Hybrid Scoring Engine:** Auto-tunes thresholds based on data distribution.
*   **📊 Dark Neo-Fintech Dashboard:** Professional, high-contrast UI for SOC analysts.
*   **🧠 Glass-Box Explainability:** SHAP/LIME integration for transparent decision-making.
*   **🔄 Graph Cycle Detection:** Identifies circular transaction loops common in washing schemes.
*   **⚡ Real-Time Streaming:** Simulates live transaction processing.

---

## 📂 Project Structure
```text
ProJ/
├── app.py                 # Main Flask Application
├── utils/                 # The "Brain" of the system
│   ├── ddie.py            # Rule Engine
│   ├── uaic.py            # ML Engine (Isolation Forest)
│   ├── graph_anomaly.py   # NetworkX Graph Logic
│   ├── scoring.py         # Hybrid Scorer
│   └── ...
├── static/                # CSS, JS, and Report Assets
├── templates/             # HTML Templates
├── TechFiesta_SUBMISSION_DOC.md  # 📄 Detailed Project Report for Judges
└── TechFiesta_PRESENTATION_SCRIPT.md # 🎙️ Pitch Script for Presentation
```

---

## 🛠️ Tech Stack
*   **Frontend:** HTML5, CSS3 (Custom Neo-Fintech Theme), JavaScript
*   **Backend:** Python 3.x, Flask
*   **Data Science:** Pandas, NumPy, Scikit-Learn (Isolation Forest)
*   **Graph/Network:** NetworkX
*   **Visualization:** Chart.js, Vis.js

---

## 🏃‍♂️ How to Run
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Server:**
    ```bash
    python app.py
    ```
3.  **Access the Dashboard:**
    Open `http://localhost:5000` in your browser.
4.  **Analyze Data:**
    Upload `sample_transactions.csv` to see the magic happen!

---

## 🏆 Hackathon Context
This project addresses the **Fintech/Security** problem statement.
*   **Submission Doc:** [View Report](./TechFiesta_SUBMISSION_DOC.md)
*   **Pitch Script:** [View Script](./TechFiesta_PRESENTATION_SCRIPT.md)

---
*Created by Team Antigravity*
