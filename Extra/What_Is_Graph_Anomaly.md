# What is a "Graph Anomaly"? 🕸️

In fraud detection, **Graph Anomalies** are suspicious patterns found not by looking at a *single* transaction, but by looking at the **connections** (relationships) between users.

Traditional systems look at rows in a spreadsheet. Graph systems look at the "Cluster" or "Network".

### 🔎 Types of Graph Anomalies

1.  **Money Laundering Loops (Cycles):**
    *   **Pattern:** User A ➔ User B ➔ User C ➔ User A.
    *   **Why:** Money is moved around to hide its source, but eventually returns to the criminal. Normal people don't usually send money in perfect circles.

2.  **Isolation (The "Stranger" Risk):**
    *   **Pattern:** Two users with NO history and NO other friends in the network suddenly exchange a huge amount.
    *   **Why:** Normal users usually transact within a community (e.g., paying a known merchant or friend). A completely isolated, high-value pair often indicates a "Mule Account" (created just to move stolen funds once).

3.  **High Fan-Out (Burst):**
    *   **Pattern:** One user sends money to 50 new people in 1 minute.
    *   **Why:** Typical of a "Scatter" phase in laundering, or a hacked account draining funds.

---
### 🧪 How We Detect It
Our system uses **NetworkX** to build a map of all users.
*   We calculate **Centrality Scores** (how "important" or "connected" a user is).
*   If two "Unimportant" (Isolated) users transact → **Score Goes Up.**
*   If a "Cycle" is found → **Score Goes Up.**

In the **`graph_isolation_test.csv`** file:
*   **User_E** is a "Hub" (Highly Central, Safe).
*   **User_Z** and **User_Y** are "Islands" (Isolated).
*   Their transaction is flagged because the system asks: *"Who are these people? They have no reputation."*
