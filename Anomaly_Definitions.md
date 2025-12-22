# 🚨 Anomaly Definitions Guide

This guide explains the specific fraud patterns detected by the **Fake Transaction Detector**.

### ⚡ High Velocity (Burst)
*   **What it is:** A single user sending multiple transactions within **less than 2 seconds**.
*   **Why it's suspicious:** No human can type and send money that fast. This is a clear sign of a **Bot Script**, **Automated Attack**, or **API Abuse**.
*   **Real World Example:** A hacker using a script to drain an account by sending $1000 fifty times in one minute.

### 🔄 Money Laundering Loop
*   **What it is:** Money moving in a circle (A -> B -> C -> A).
*   **Why it's suspicious:** Genuine payments usually go one way (Customer -> Merchant). Circular flow is used to "layer" or "wash" dirty money to make it look like legitimate turnover.

### 👯 Transaction Duplicate (Replay Attack)
*   **What it is:** The exact same transaction (same ID/User) appearing twice.
*   **Why it's suspicious:** Could be a system error, or a **Replay Attack** where a hacker intercepts a valid request and resends it to get paid twice.

### 📍 Impossible Travel (Location Conflict)
*   **What it is:** A user transacting from **Mumbai** and then **London** 5 minutes later.
*   **Why it's suspicious:** Users cannot physically travel that fast. Indicates **Account Compromise** (hacking) where two people are using the same account in different places.

### 🔮 Future Timestamp
*   **What it is:** A transaction date set in the future (e.g., Year 2035).
*   **Why it's suspicious:** Indicates a system bug or an attempt to manipulate ledger order.

### 🛑 Negative/Zero Amount
*   **What it is:** Sending -5000 or 0.
*   **Why it's suspicious:** Breaks basic accounting rules. Likely a **Data Integrity Violation** or an attempt to exploit integer overflow bugs.
