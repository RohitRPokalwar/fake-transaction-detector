# 🚨 Project Algorithms & Rules Guide

This guide explains every detection method used in the **Fake Transaction Detector Project**.

## 1. Static Rule Engine (DDIE)
*Deterministic Data Integrity Engine*

### ⚡ High Velocity (Burst)
*   **What it is:** A single user sending multiple transactions **within 2 seconds**.
*   **Why it's suspicious:** No human can type and send money that fast. This is a clear sign of a **Bot Script**, **Automated Attack**, or **API Abuse**.
*   **Real World Example:** A hacker using a script to drain an account by sending ₹1000 fifty times in one minute.

### 👯 Copy-Paste Fraud (Replay Attack)
*   **What it is:** The exact same transaction (same ID/User) appearing twice.
*   **Why it's suspicious:** A hacker "copy-pasts" a valid payment to get paid twice.

### 📍 Teleportation Alert (Location Conflict)
*   **What it is:** Moving between two far-away cities (like Mumbai and London) in 5 minutes.
*   **Why it's suspicious:** You can't travel that fast! It means your account is being used by someone else in a different country.

### 🔮 Time Travel (Future Date)
*   **What it is:** A transaction dated for next week or next year.
*   **Why it's suspicious:** Someone is trying to trick the bank's calendar to hide their activities.

### 🛑 Ghost Money (Invalid Amount)
*   **What it is:** Trying to send zero or negative money.
*   **Why it's suspicious:** It's an attempt to break the bank's accounting logic to "generate" money out of nowhere.

### 🧩 Broken Identity (Missing Fields)
*   **What it is:** A transaction that is missing basic info like User ID or Amount.
*   **Why it's suspicious:** Hackers send "broken" data to try and bypass security filters.

---

## 2. Graph Neural Analysis
*Network Structure & Relationship Detection*

### 🔄 Money Circle (Laundering Ring)
*   **What it is:** Money moving in a circle (A -> B -> C -> A).
*   **Why it's suspicious:** It's used to "clean" illegal money by moving it around until the original source is hidden.

### 🌐 Stranger Danger (Network Jump)
*   **What it is:** Sending money to a completely unknown group of users very suddenly.
*   **Why it's suspicious:** Real people send money to friends. Criminals send money to "mule" networks they've never interacted with before.

---

## 3. Machine Learning (UAIC)
*Unsupervised Anomaly Intelligence Component*

### 🤖 Behavioral Anomaly (Statistical Outlier)
*   **What it is:** A transaction that breaks no specific rule but is statistically rare (e.g., User usually spends ₹50 at noon, but suddenly spends ₹50,000 at 3 AM).
*   **Why it's suspicious:** Our **Isolation Forest** model learns normal behavior. Extreme deviations in **Amount**, **Time**, or **Frequency** are flagged as anomalies, often catching **Account Takeovers** or **First-Time Fraud** that rules miss.
