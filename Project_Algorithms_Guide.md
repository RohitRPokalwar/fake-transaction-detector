# 🚨 Project Algorithms & Rules Guide

This guide explains every detection method used in the **Fake Transaction Detector Project**.

## 1. Static Rule Engine (DDIE)
*Deterministic Data Integrity Engine*

### ⚡ High Velocity (Burst)
*   **What it is:** A single user sending multiple transactions within **less than 2 seconds**.
*   **Why it's suspicious:** No human can type and send money that fast. This is a clear sign of a **Bot Script**, **Automated Attack**, or **API Abuse**.
*   **Real World Example:** A hacker using a script to drain an account by sending ₹1000 fifty times in one minute.

### 👯 Transaction Duplicate (Replay Attack)
*   **What it is:** The exact same transaction (same ID/User) appearing twice.
*   **Why it's suspicious:** Could be a system error, or a **Replay Attack** where a hacker intercepts a valid request and resends it to get paid twice.

### 📍 Impossible Travel (Location Conflict)
*   **What it is:** A user transacting from **Mumbai** and then **London** 5 minutes later.
*   **Why it's suspicious:** Users cannot physically travel that fast. Indicates **Account Compromise** (hacking) where two people are using the same account in different places.

### 🔮 Future Timestamp
*   **What it is:** A transaction date set in the future (e.g., Year 2035).
*   **Why it's suspicious:** Indicates a system bug or an attempt to manipulate ledger order to hide funds.

### 🛑 Negative/Zero Amount
*   **What it is:** Sending -5000 or 0.
*   **Why it's suspicious:** Breaks basic accounting rules. Likely a **Data Integrity Violation** or an attempt to exploit integer overflow bugs in the database.

### 🧩 Incomplete Data (Missing Fields)
*   **What it is:** A transaction missing a User ID, Amount, or Recipient.
*   **Why it's suspicious:** Banking systems are strict. Missing data usually means a **Malicious Payload** trying to bypass validation filters.

---

## 2. Graph Neural Analysis
*Network Structure & Relationship Detection*

### 🔄 Money Laundering Loop
*   **What it is:** Money moving in a circle (A -> B -> C -> A).
*   **Why it's suspicious:** Genuine payments usually go one way. Circular flow is used to "layer" or "wash" dirty money to make it look like legitimate business turnover without money actually leaving the group.

### 🌐 Cross-Community Transaction
*   **What it is:** A web of transactions between two completely unrelated groups of users (Clusters).
*   **Why it's suspicious:** Normal users stay within their "community" (friends/local merchants). Sudden, dense flow between totally separate groups often indicates **Smurfing** (breaking large illegal sums into small chunks to move them to a mule network).

---

## 3. Machine Learning (UAIC)
*Unsupervised Anomaly Intelligence Component*

### 🤖 Behavioral Anomaly (Statistical Outlier)
*   **What it is:** A transaction that breaks no specific rule but is statistically rare (e.g., User usually spends ₹50 at noon, but suddenly spends ₹50,000 at 3 AM).
*   **Why it's suspicious:** Our **Isolation Forest** model learns normal behavior. Extreme deviations in **Amount**, **Time**, or **Frequency** are flagged as anomalies, often catching **Account Takeovers** or **First-Time Fraud** that rules miss.
