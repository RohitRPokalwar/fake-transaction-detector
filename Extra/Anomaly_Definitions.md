# 🚨 Anomaly Definitions Guide

This guide explains the specific fraud patterns detected by the **Fake Transaction Detector**.

### ⚡ High Velocity (Burst)
*   **What it is:** A single user sending multiple transactions **within 2 seconds**.
*   **Why it's suspicious:** No human can type and send money that fast. This is a clear sign of a **Bot Script**, **Automated Attack**, or **API Abuse**.
*   **Real World Example:** A hacker using a script to drain an account by sending $1000 fifty times in one minute.

### 🔄 Money Circle (Laundering Ring)
*   **What it is:** Money moving in a circle (A -> B -> C -> A).
*   **Why it's suspicious:** Genuine payments usually go one way. A "Money Circle" is used to "wash" dirty money to make it look like legitimate business turnover.

### 👯 Copy-Paste Fraud (Replay Attack)
*   **What it is:** The exact same transaction appearing twice.
*   **Why it's suspicious:** A hacker might be "copy-pasting" a valid transaction to get paid twice.

### 📍 Teleportation Alert (Location Conflict)
*   **What it is:** A user moving between cities (Mumbai to London) in 5 minutes.
*   **Why it's suspicious:** Humans can't teleport. It means two different people are using the same account in different countries at the same time.

### 🔮 Time Travel (Future Date)
*   **What it is:** A transaction dated in the future (e.g., Year 2035).
*   **Why it's suspicious:** Indicates a system hack or an attempt to mess up the bank's records.

### 🛑 Ghost Money (Invalid Amount)
*   **What it is:** Sending -5000 or 0.
*   **Why it's suspicious:** You can't send negative cash! This usually means someone is trying to exploit a bug to "steal" money by sending negative values.

### 🌐 Stranger Danger (Cross-Community Transaction)
*   **What it is:** Alice (who usually pays her friends) suddenly sends a large sum to a group of people in a different city that she has NO connection with.
*   **Why it's suspicious:** Real accounts stay within their "Trusted Circle" (family, local shops). A sudden "jump" to a totally unrelated group of people is a classic sign of a **Hacked Account** or a **Mule Network** used for illegal transfers.
