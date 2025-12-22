# 🤖 Judge Mode Cheat Sheet: How to Impress 

Use this guide to trigger specifically designed anomalies during your live demo.

### 🌟 Prerequisites
1.  **Start the Server:** `python app.py`
2.  **Load Context:** Go to Dashboard -> Upload `Final_Presentation_Demo.csv`. (This loads the history for users like User_Travel, User_Bot, etc.)
3.  **Open Judge Mode:** Click "Judge Mode" or "PhonePe Simulator".

---

### 1. 🔮 The "Future Time Travel" Trick
*   **Action:** Enter a date in the far future.
    *   **User ID:** `User_Test`
    *   **Timestamp:** `2035-01-01 12:00:00`
    *   **Amount:** `500`
*   **Result:** 🔴 **SUSPICIOUS**
*   **Why:** Triggers "Timestamp Violation".
*   **Pitch:** *"Watch closely. Even if the amount is normal, the system detects the date manipulation instantly."*

---

### 2. ⚡ The "Burst" Attack (High Velocity)
*   **Action:** Rapidly click "Analyze" twice.
    *   **User ID:** `User_Bot_Live`
    *   **Amount:** `100`
    *   **Click:** Analyze -> *Wait 0.5s* -> Click Analyze again.
*   **Result:** The first might be Safe, but the **Second** will be 🔴 **SUSPICIOUS**.
*   **Why:** Triggers "High Velocity (Burst)" (< 2 seconds gap).
*   **Pitch:** *"I will now simulate a bot attack. I send two requests in under a second... and caught! No human can transact this fast."*

---

### 3. 🌍 The "Impossible Travel" (Teleportation)
*   **Requirement:** Must have loaded `Final_Presentation_Demo.csv` first (containing `User_Travel`).
*   **Action:**
    *   **User ID:** `User_Travel` (Use this exact ID)
    *   **Location:** `New York` (The CSV put them in Mumbai/London recently)
*   **Result:** 🔴 **SUSPICIOUS**
*   **Why:** Triggers "Location Conflict" (Impossible to move from London to New York in ~minutes).
*   **Pitch:** *"User_Travel was in London 5 minutes ago (in our data). Now I try to transact from New York. Account Compromise detected!"*

---

### 4. 🔄 The "Money Laundering Loop" (Advanced)
*   **Requirement:** Must have loaded `Final_Presentation_Demo.csv`.
*   **Context:** The CSV has `TXN-2009` (A->B) and `TXN-2010` (B->C).
    *   A = `User_26`
    *   B = `User_27`
    *   C = `User_28`
    *   The loop in CSV is A->B->C->A.
*   **Action:** Let's create a *new* loop.
    *   Upload CSV first.
    *   **Transaction 1 (Judge Mode):** `User_X` -> `User_Y` (₹50,000) -> *Click Analyze*.
    *   **Transaction 2 (Judge Mode):** `User_Y` -> `User_Z` (₹49,000) -> *Click Analyze*.
    *   **Transaction 3 (Judge Mode):** `User_Z` -> `User_X` (₹48,000) -> *Click Analyze*.
*   **Result:** Transaction 3 will ideally trigger 🔴 **SUSPICIOUS** (Graph Graph Score High).
*   **Pitch:** *"The system tracks relationships in memory. I just completed a washing cycle, and the graph engine flagged it immediately."*

---

### 5. 🛑 The "Negative Amount" (Basic Check)
*   **Action:** Enter a negative number.
    *   **Amount:** `-5000`
*   **Result:** 🔴 **SUSPICIOUS**
*   **Why:** Triggers "Amount Anomaly".
