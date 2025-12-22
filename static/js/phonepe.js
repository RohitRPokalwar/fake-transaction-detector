async function analyzeTransaction() {
    const loader = document.getElementById('loader');
    const resultCard = document.getElementById('resultCard');
    const techBtn = document.getElementById('techToggle');
    const techPanel = document.getElementById('techPanel');

    // Reset UI
    resultCard.style.display = 'none';
    techBtn.style.display = 'none';
    techPanel.style.display = 'none';
    loader.style.display = 'flex';

    // Gather Data
    const payload = {
        transaction_id: document.getElementById('txnId').value,
        sender_id: document.getElementById('senderId').value,
        receiver_id: document.getElementById('receiverId').value,
        amount: parseFloat(document.getElementById('txnAmount').value),
        location: document.getElementById('txnLocation').value,
        timestamp: document.getElementById('txnTimestamp').value || new Date().toISOString().replace('T', ' ').substring(0, 19)
    };

    try {
        const response = await fetch('/api/judge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Update UI
        updateResult(data);

        // Auto-generate NEW ID for next scan (prevents "Duplicate" error on Burst test)
        document.getElementById('txnId').value = "TXN-" + Math.floor(Math.random() * 900000 + 100000) + "-LIVE";


    } catch (e) {
        alert("Analysis Failed: " + e.message);
    } finally {
        loader.style.display = 'none';
    }
}

function updateResult(data) {
    const resultCard = document.getElementById('resultCard');
    const statusBadge = document.getElementById('statusBadge');
    const riskScore = document.getElementById('riskScore');
    const narrativeText = document.getElementById('narrativeText');
    const techBtn = document.getElementById('techToggle');
    const techPanel = document.getElementById('techPanel');

    resultCard.style.display = 'block';

    // Status
    if (data.is_anomalous) {
        statusBadge.className = 'status-badge status-fake';
        statusBadge.textContent = 'SUSPICIOUS';
    } else {
        statusBadge.className = 'status-badge status-safe';
        statusBadge.textContent = 'VERIFIED SAFE';
    }

    // Score
    riskScore.textContent = (data.final_score * 100).toFixed(1);

    // Narrative (extract text from HTML explanation if complex, or just use raw explanation)
    // The Explanation from backend is HTML. We can render it directly or strip tags.
    // For this UI, let's keep it simple or parse key parts.
    // Actually, we can just inject the HTML but style it minimally.
    // Or strip the HTML tags for a cleaner "PhonePe" look.
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = data.explanation;
    const plainText = tempDiv.textContent || tempDiv.innerText || "";
    // Let's try to just show the "Why Suspicious" part if possible?
    // Since structure is standard, we can verify.
    // But for safety, let's just show text content.
    narrativeText.innerHTML = data.explanation; // Allow HTML but it might look messy with default styles.
    // Let's override styles inside explanation-text

    // Tech Details
    if (data.details) {
        techBtn.style.display = 'block';
        const d = data.details;
        const w = d.weights || { rule: 0, ml: 0, graph: 0 };

        techPanel.innerHTML = `
>> INTERNAL SCORING LOGIC
---------------------------
[+] RULE ENGINE:   ${(d.rule_score * 100).toFixed(0)}% (w: ${w.rule})
[+] AI MODEL:      ${(d.ml_score * 100).toFixed(0)}% (w: ${w.ml})
[+] GRAPH NET:     ${(d.graph_score * 100).toFixed(0)}% (w: ${w.graph})
---------------------------
TOTAL RISK SCORE:  ${(data.final_score * 100).toFixed(1)}%
THRESHOLD:         ${(d.threshold * 100).toFixed(1)}%
        `.trim();
    }
}


function toggleTechDetails() {
    const p = document.getElementById('techPanel');
    if (p.style.display === 'none') {
        p.style.display = 'block';
    } else {
        p.style.display = 'none';
    }
}

// Auto-fill timestamp on load
// Auto-fill timestamp on load AND Reset Context
document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-fill Time (Live Clock)
    const tsInput = document.getElementById('txnTimestamp');
    if (tsInput) {
        const updateTime = () => {
            // Only update if user is NOT typing (not focused)
            if (document.activeElement !== tsInput) {
                const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
                tsInput.value = now;
            }
        };
        updateTime(); // Initial
        setInterval(updateTime, 1000); // Live Update
    }

    // 2. Reset Backend Context
    fetch('/api/reset_judge', { method: 'POST' })
        .then(res => console.log("Judge Context Reset"))
        .catch(err => console.error("Reset Failed", err));
});
