# 🛡️ Fake Transaction Detector (FTD)

> **A Next-Gen Hybrid Fraud Detection System powered by Rules, Machine Learning, and Graph Analysis.**  
> *Built for TechFiesta 2026*

---

## 🌟 Overview
**Fake Transaction Detector** is a financial intelligence tool capable of identifying fraudulent patterns in real-time. Unlike traditional systems that FTD uses a **Triple-Engine Architecture**:
1.  **Deterministic Rules (DDIE):** Catch obvious violations instantly (Burst, Future Date, Negative Amount).
2.  **Graph Network Analysis:** Uncover hidden Money Laundering rings and Loops.
3.  **Unsupervised ML (UAIC):** Detect subtle behavioral anomalies (Isolation Forest).

Most importantly, it provides **Explainable AI (XAI)**—telling you *exactly why* a transaction was flagged (e.g., "Money Laundering Loop Detected").

---

## 🚀 Key Features
*   **🕷️ Hybrid Scoring Engine:** Combines Hard Rules + Graph Logic + ML Scores.
*   **📊 Dark Neo-Fintech Dashboard:** Professional, high-contrast UI for SOC analysts.
*   **🔄 Advanced Loop Detection:** Identifies A -> B -> C -> A washing schemes using NetworkX.
*   **⚡ High Velocity Detection:** Flags "Burst" attacks (bot scripts) in <2ms.
*   **🌍 Impossible Travel:** Detects geospatial conflicts (e.g., Mumbai -> London in 5 mins).

---

## 🚨 Detectable Anomalies
The system successfully identifies:
*   **Transaction Duplicate:** Replay attacks.
*   **Timestamp Violation:** Future dates (Year 2035).
*   **Amount Anomalies:** Negative or Zero values.
*   **High Velocity (Burst):** < 2s between transactions.
*   **Location Conflict:** Impossible travel speed.
*   **Money Laundering Loop:** Circular flow of funds.

---

## 📂 Project Structure
```text
ProJ/
├── app.py                     # Main Flask Application
├── generate_final_demo.py     # Script to generate diverse Test Data
├── utils/                     # The "Brain" of the system
│   ├── ddie.py                # Rule Engine (Static checks)
│   ├── uaic.py                # ML Engine (Isolation Forest)
│   ├── graph_anomaly.py       # Graph Logic (Loops/Communities)
│   ├── scoring.py             # Hybrid Scorer
│   └── explain.py             # Explanation Generator
├── static/                    # CSS, JS, and Assets
├── templates/                 # HTML Templates
├── Final_Presentation_Demo.csv # 📄 PRE-GENERATED DEMO FILE
├── Project_Algorithms_Guide.md # 📘 Full Algorithm Documentation
└── TechFiesta_PRESENTATION_SCRIPT.md # 🎙️ Pitch Script
```

---

## 🛠️ Tech Stack
*   **Frontend:** HTML5, CSS3 (Custom Neo-Fintech Theme), JavaScript
*   **Backend:** Python 3.x, Flask
*   **Data Science:** Pandas, NumPy, Scikit-Learn
*   **Graph:** NetworkX
*   **Visualization:** Chart.js

---

## 🏃‍♂️ How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Demo Data (Optional)
Create a fresh, diverse dataset with 100+ transactions and 11 guaranteed anomalies.
```bash
python generate_final_demo.py
```
*This creates `Final_Presentation_Demo.csv`.*

### 3. Run the Server
```bash
python app.py
```

### 4. Access the Dashboard
Open `http://localhost:5000` in your browser.

### 5. Start Analysis
Upload `Final_Presentation_Demo.csv` to see the engine in action!

---

## 🏆 Hackathon Context
This project addresses the **Fintech/Security** problem statement.
*   **Algorithm Guide:** [View Guide](./Project_Algorithms_Guide.md)
*   **Pitch Script:** [View Script](./TechFiesta_PRESENTATION_SCRIPT.md)

---
