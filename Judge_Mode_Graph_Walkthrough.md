    # 🔄 Graph Anomaly: The "Live Cycle" Method (Pure Judge Mode)

You can demonstrate a Graph Anomaly **completely from scratch** in Judge Mode, without uploading any CSV. This is very impressive because you build the trap live.

### The Logic
We will create a Money Laundering Loop: **A -> B -> C -> A**.
The system remembers every transaction you scan.

---

### 🟢 Step 1: Transfer A -> B
*   **Sender ID:** `Live_A`
*   **Receiver ID:** `Live_B`
*   **Amount:** `50000`
*   **Action:** Click **SECURE SCAN & PAY**.
*   **Result:** ✅ **SAFE** (System records: "A sent to B")

---

### 🟢 Step 2: Transfer B -> C
*   **Sender ID:** `Live_B`  *(Change from prev)*
*   **Receiver ID:** `Live_C` *(Change from prev)*
*   **Amount:** `49000`
*   **Action:** Click **SECURE SCAN & PAY**.
*   **Result:** ✅ **SAFE** (System records: "B sent to C")

---

### 🔴 Step 3: Close the Loop (C -> A)
*   **Sender ID:** `Live_C` *(Change from prev)*
*   **Receiver ID:** `Live_A` *(This completes the circle!)*
*   **Amount:** `48000`
*   **Action:** Click **SECURE SCAN & PAY**.
*   **Result:** 🔴 **SUSPICIOUS**
*   **Reason:** "Money Laundering Loop Detected: Live_A -> Live_B -> Live_C -> Live_A"

---
### 💡 Important Tip
**Do not refresh the page** between steps 1, 2, and 3. Refreshing clears the memory. You must do them in one session.
