# 🧠 Technical Deep Dive: The Intelligence Engine

This document explains the core technical pillars of the **Fake Transaction Detector**. This is a hybrid architecture designed to catch what standard banking systems miss.

---

## 🏗️ 1. Multi-Layer Defense: DDIE + SSG + UAIC + Graph

We don't rely on just one method. We use a **Quad-Stack Defense** to analyze transactions from four different dimensions:

### **Layer 1: DDIE (Deterministic Data Integrity Engine)**
*   **Role:** The "Strict Border Guard."
*   **Logic:** Uses hard-coded business rules. It checks for ₹0/Negative amounts, future-dated timestamps, and ID duplicates.
*   **Why:** It catches the "easy" errors instantly without needing complex AI.

### **Layer 2: SSG (Statistical Signature Generator)**
*   **Role:** The "Profiling Baseline."
*   **Logic:** Computes the mathematical "Signature" of the data (Mean, Median, Standard Deviation, IQR).
*   **Why:** It establishes what "Normal" looks like for this specific bank so we can detect shifts in behavior.

### **Layer 3: UAIC (Unsupervised Anomaly Isolation Core)**
*   **Role:** The "Pattern Hunter."
*   **Logic:** Uses an **Isolation Forest** (Machine Learning). Instead of learning what is *normal*, it tries to *isolate* transactions.
*   **Why:** Fraud is rare. Isolation Forest is perfect because it assumes anomalies are few and different. If a transaction is "easy to isolate" in a decision tree, it's flagged as an outlier.

### **Layer 4: Graph-Based Anomaly Detection**
*   **Role:** The "Network Watcher."
*   **Logic:** Maps transactions as a Directed Graph (Accounts = Nodes, Transfers = Edges).
*   **Why:** AI and Rules often miss "Structural Fraud." If Tom sends to Dick, Dick to Harry, and Harry back to Tom, standard AI sees 3 normal transfers. Our Graph Engine sees a **Circular Laundering Loop**.

---

## 🕸️ 2. Graph-Based Anomaly Detection (Structural Intelligence)

Most fraud isn't done by one person; it's done by a network.
*   **Community Detection:** We use the **Louvain Method** to find "Islands" of users who only send money to each other. A transaction between two disconnected communities is a "Cross-Community Spike."
*   **Cycle Detection:** We use **NetworkX's Simple Cycles** algorithm. We look for money that flows in a ring (A -> B -> C -> A).
*   **WOW Feature:** We extract the raw path data to draw the **Network Topology Map**, showing investigators exactly how the money is looping.

---

## 🤖 3. Explainable AI (SHAP and LIME)

Most AI is a "Black Box"—it says "It's Fraud" but doesn't say why. This system uses **XAI (Explainable AI)** to make it a "Glass Box."

*   **SHAP (SHapley Additive exPlanations):**
    *   **Global View:** Shows which features (like `amount` or `time`) generally contribute most to the risk.
    *   **Logic:** Based on Game Theory. It treats each feature as a "Player" and calculates its contribution to the final "Win" (The Anomaly Score).
*   **LIME (Local Interpretable Model-agnostic Explanations):**
    *   **Local View:** For *this specific* transaction, LIME perturbs the data (changes the amount slightly) to see how the score changes. 
    *   **Output:** It produces the "AI Investigator" narrative you see in the dashboard.

---

## ⚖️ 4. Adaptive Thresholds

Banking data is never the same. A ₹1 Lakh transfer might be normal for a Corporate Bank but a massive anomaly for a Rural Branch.

*   **Dynamic Tuning:** Instead of a fixed 0.5 threshold, the system uses **ROC Curve Analysis** if labels are present, or **Heuristic Percentiles** if not.
*   **Sensitivity Control:** It looks at the distribution of scores across the entire batch. If it sees the "Intensity" is generally high, it tightens the threshold. 
*   **Hybrid Weighting:** It dynamically balances the influence of the Rule Engine (High weight for errors) vs the ML Core (High weight for behavioral shifts).

---

### 🛡️ Summary for Investigators:
This system doesn't just "detect." It **Validates** (DDIE), **Compares** (SSG), **Analyzes** (UAIC), and **Connects** (Graph). Each layer feeds the next, resulting in the most robust fraud detection suite in its class.
