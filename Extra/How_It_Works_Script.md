# 🧠 The "Secret Sauce": How We Catch Fraud

(Use this script when judges ask: *"How does it actually work?"*)

---

### 1. The Rule Engine (The Gatekeeper) [50% Weight]
*"First, every transaction hits our Deterministic Rule Engine. It checks for obvious impossibilities."*

*   **Future Travel:** "Are you in London now but were in Mumbai 5 minutes ago?" (Calculates speed > 1000km/h).
*   **Time Travel:** "Is the timestamp in the year 2035?"
*   **Bot Speed:** "Did you click twice in < 2 seconds?"

### 2. The AI Model (The Brain) [40% Weight]
*"If it passes the rules, our Unsupervised AI (Isolation Forest) looks at the behavior."*

*   **It learns "Normal":** "User_X usually spends $50 at 2 PM."
*   **It spots "Abnormal":** "Suddenly, User_X spends $5,000 at 3 AM."
*   *The AI doesn't know it's fraud, it just knows it's WEIRD.*

### 3. The Graph Engine (The Detective) [10% + Override]
*"Finally, the Graph Engine maps the hidden connections."*

*   **Loops:** It looks for A -> B -> C -> A cycles (classic money laundering).
*   **Override Power:** Even if the AI thinks the amount is fine, if the Graph sees a Loop, it **Overrides** everything and flags it as **100% SUSPICIOUS**.

---

### 🎯 The Final Score
*"We combine these three scores. If the weighted average > 0.6, we block it."*
