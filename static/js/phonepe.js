let latestNodePath = null;
let currentScenarioId = 0;

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
        timestamp: document.getElementById('txnTimestamp').value || new Date(new Date().getTime() + (330 * 60 * 1000)).toISOString().replace('T', ' ').substring(0, 19)
    };

    try {
        const response = await fetch('/api/judge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Store latest node path for viz
        if (data.details && data.details.node_path) {
            latestNodePath = data.details.node_path;
        }

        // Update UI
        updateResult(data);

        // Auto-generate NEW ID for next scan
        if (document.getElementById('txnId')) {
            document.getElementById('txnId').value = "TXN-" + Math.floor(Math.random() * 900000 + 100000) + "-LIVE";
        }


    } catch (e) {
        // Only alert if we didn't just reset
        if (loader.style.display !== 'none') {
            alert("Analysis Failed: " + e.message);
        }
    } finally {
        loader.style.display = 'none';
    }
}

async function showJudgeHistory() {
    const modal = document.getElementById('historyModal');
    const body = document.getElementById('historyBody');

    modal.style.display = 'flex';
    body.innerHTML = '<tr><td colspan="5" style="text-align:center">Fetching Forensic Data...</td></tr>';

    try {
        const res = await fetch('/api/judge_history');
        const data = await res.json();

        if (data.history && data.history.length > 0) {
            body.innerHTML = '';
            data.history.reverse().forEach(txn => {
                const isAnom = txn.is_anomalous;
                const row = `
                    <tr>
                        <td>${txn.transaction_id}</td>
                        <td>${txn.user_id}</td>
                        <td>${txn.recipient_id || txn.receiver_id}</td>
                        <td>₹${txn.amount}</td>
                        <td class="${isAnom ? 'status-row-anomalous' : 'status-row-safe'}">
                            ${isAnom ? 'SUSPICIOUS' : 'SAFE'}
                        </td>
                    </tr>
                `;
                body.innerHTML += row;
            });
        } else {
            body.innerHTML = '<tr><td colspan="5" style="text-align:center">No transactions in current session.</td></tr>';
        }
    } catch (e) {
        body.innerHTML = '<tr><td colspan="5">Error loading history</td></tr>';
    }
}

function closeHistoryModal() {
    document.getElementById('historyModal').style.display = 'none';
}

async function resetJudgeContext() {
    const status = document.getElementById('contextStatus');
    status.innerHTML = "● Resetting Engine...";
    status.style.color = "var(--danger)";

    // 1. Cancel any running scenarios
    currentScenarioId++;
    latestNodePath = null;

    // Hide loader if it was active
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'none';

    // 2. Clear UI Inputs
    document.getElementById('senderId').value = "user_" + Math.floor(Math.random() * 100);
    document.getElementById('receiverId').value = "merchant_" + Math.floor(Math.random() * 50);
    document.getElementById('txnAmount').value = "5000";
    document.getElementById('txnLocation').value = "Delhi, IN";
    document.getElementById('txnId').value = "TXN-" + Math.floor(Math.random() * 900000 + 100000) + "-LIVE";

    // 3. Reset Result Card & Panels
    document.getElementById('resultCard').style.display = 'none';
    document.getElementById('techToggle').style.display = 'none';
    document.getElementById('techPanel').style.display = 'none';
    document.getElementById('techPanel').innerHTML = '';
    document.getElementById('cycleVizResult').style.display = 'none';
    document.getElementById('cycleVizResult').innerHTML = '';

    // Reset any step counters on buttons (like Money Circle)
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        if (btn.dataset.step) btn.dataset.step = "0";
        const small = btn.querySelector('small');
        if (btn.innerText.includes('MONEY CIRCLE') && small) {
            small.innerHTML = 'Laundering Loop (3 Txns)';
        }
    });

    try {
        await fetch('/api/reset_judge', { method: 'POST' });
        setTimeout(() => {
            status.innerHTML = "● Context Cleared";
            status.style.color = "#00ff9d";
        }, 600);
    } catch (e) {
        status.innerHTML = "● Reset Failed";
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

    // Narrative
    narrativeText.innerHTML = data.explanation;

    // Network Loop Viz (In main Result Card)
    const cycleRes = document.getElementById('cycleVizResult');
    if (data.details && data.details.node_path && data.details.node_path.length > 0) {
        cycleRes.style.display = 'flex';
        cycleRes.innerHTML = '<div style="width:100%; font-size:0.7rem; color:var(--accent-color); margin-bottom:5px; text-transform:uppercase;">Network Path Detected:</div>';
        const path = data.details.node_path;
        path.forEach((node, idx) => {
            cycleRes.innerHTML += `<div class="node-box" style="font-size:0.6rem; padding:4px 8px;">${node}</div>`;
            if (idx < path.length - 1 || path.length > 2) {
                cycleRes.innerHTML += `<div class="node-arrow" style="font-size:0.8rem;">\u2192</div>`;
            }
        });
        if (path.length > 2) {
            cycleRes.innerHTML += `<div class="node-box" style="font-size:0.6rem; padding:4px 8px;">${path[0]}</div>`;
        }
    } else {
        cycleRes.style.display = 'none';
    }

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
    if (p.style.display === 'none' || p.style.display === '') {
        p.style.display = 'block';
    } else {
        p.style.display = 'none';
    }
}

// --- JUDGE MODE SCENARIOS ---
function loadScenario(type, event) {
    const sId = document.getElementById('senderId');
    const rId = document.getElementById('receiverId');
    const amt = document.getElementById('txnAmount');
    const loc = document.getElementById('txnLocation');
    const tid = document.getElementById('txnId');

    // Reset status indicator
    const status = document.getElementById('contextStatus');
    status.innerHTML = "● Loading Scenario...";
    status.style.color = "var(--accent-color)";

    const scenarioId = ++currentScenarioId;

    if (type === 'teleport') {
        const runTeleport = async () => {
            if (scenarioId !== currentScenarioId) return;
            sId.value = "User_Travel_88";
            rId.value = "Merchant_Global";
            amt.value = "12000";
            loc.value = "London, UK";
            tid.value = "TXN-TRAV-01";
            status.innerHTML = "● Sending Txn 1 (London)...";
            await analyzeTransaction();

            if (scenarioId !== currentScenarioId) return;
            await new Promise(r => setTimeout(r, 1500));
            if (scenarioId !== currentScenarioId) return;

            loc.value = "Mumbai, IN";
            tid.value = "TXN-TRAV-02";
            status.innerHTML = "● Sending Txn 2 (Mumbai - Jump!)...";
            await analyzeTransaction();

            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Teleportation Caught!";
            status.style.color = "#ff4081";
        };
        runTeleport();
        return;
    }

    if (type === 'bot') {
        const runBot = async () => {
            if (scenarioId !== currentScenarioId) return;
            sId.value = "Bot_Script_v4";
            rId.value = "Unknown_Node";
            amt.value = "49000";
            loc.value = "Mumbai, IN";

            tid.value = "TXN-SPEED-01";
            status.innerHTML = "● Burst Txn 1...";
            await analyzeTransaction();

            if (scenarioId !== currentScenarioId) return;
            await new Promise(r => setTimeout(r, 600));
            if (scenarioId !== currentScenarioId) return;

            tid.value = "TXN-SPEED-02";
            status.innerHTML = "● Burst Txn 2 (High Velocity!)...";
            await analyzeTransaction();

            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Bot Attack Stopped!";
            status.style.color = "#ff4081";
        };
        runBot();
        return;
    }

    if (type === 'cycle') {
        const runCycle = async () => {
            const sequence = [
                { s: "Alice", r: "Bob", a: "50000", l: "Bangalore", t: "CYC-01" },
                { s: "Bob", r: "Charlie", a: "50000", l: "Mysore", t: "CYC-02" },
                { s: "Charlie", r: "Alice", a: "50000", l: "Chennai", t: "CYC-03" }
            ];

            for (let i = 0; i < sequence.length; i++) {
                if (scenarioId !== currentScenarioId) return;
                const d = sequence[i];
                sId.value = d.s;
                rId.value = d.r;
                amt.value = d.a;
                loc.value = d.l;
                tid.value = d.t;

                status.innerHTML = `● Step ${i + 1}: ${d.s} \u2192 ${d.r}...`;
                await analyzeTransaction();
                if (i < 2) {
                    if (scenarioId !== currentScenarioId) return;
                    await new Promise(r => setTimeout(r, 1200));
                }
            }

            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Money Circle Broken!";
            status.style.color = "#ff4081";
        };
        runCycle();
        return;
    }

    if (type === 'whale') {
        sId.value = "VIP_Account_01";
        rId.value = "Offshore_Trust";
        amt.value = "15000000"; // 1.5 Crore
        loc.value = "Dubai, UAE";
        tid.value = "TXN-WHALE-99";

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Whale Loading...";
            status.style.color = "var(--accent-color)";
            analyzeTransaction();
        }, 400);
        return;
    }

    if (type === 'jump') {
        sId.value = "Regular_User_A";
        rId.value = "Dark_Web_Node_X";
        amt.value = "85000";
        loc.value = "Unknown";
        tid.value = "TXN-NODE-JUMP";

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Security Jump Detected...";
            status.style.color = "var(--danger)";
            analyzeTransaction();
        }, 400);
        return;
    }

    if (type === 'duplicate') {
        if (scenarioId !== currentScenarioId) return;
        tid.value = "TXN-FIXED-ID-123";
        sId.value = "User_A";
        rId.value = "User_B";
        amt.value = "500";

        status.innerHTML = "● Sending Original...";
        analyzeTransaction();

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            tid.value = "TXN-FIXED-ID-123"; // Exact same ID
            status.innerHTML = "● Sending Duplicate (Ghost!)...";
            analyzeTransaction();
        }, 2000);
        return;
    }

    if (type === 'future') {
        tid.value = "TXN-TIME-WARP";
        const futureDate = "2030-01-01 12:00:00";
        document.getElementById('txnTimestamp').value = futureDate;

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Time Paradox Loaded...";
            analyzeTransaction();
        }, 400);
        return;
    }

    if (type === 'corrupt') {
        tid.value = "TXN-EMPTY-META";
        rId.value = ""; // Missing Receiver

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Data Integrity Scan...";
            analyzeTransaction();
        }, 400);
        return;
    }

    if (type === 'zero') {
        tid.value = "TXN-ZERO-VAL";
        amt.value = "0";

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Zero-Value Analysis...";
            analyzeTransaction();
        }, 400);
        return;
    }

    if (type === 'new') {
        sId.value = "User_" + Math.floor(Math.random() * 999);
        rId.value = "Merchant_" + Math.floor(Math.random() * 99);
        amt.value = Math.floor(Math.random() * 5000 + 100);
        loc.value = "Delhi, IN";
        tid.value = "TXN-" + Math.floor(Math.random() * 1000);

        setTimeout(() => {
            if (scenarioId !== currentScenarioId) return;
            status.innerHTML = "● Nominal Case Loaded";
            status.style.color = "#00ff9d";
            analyzeTransaction();
        }, 400);
    }
}

// Auto-fill timestamp on load AND Reset Context
document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-fill Time (Live Clock)
    const tsInput = document.getElementById('txnTimestamp');
    if (tsInput) {
        const updateTime = () => {
            if (document.activeElement !== tsInput) {
                // Correctly offset to Indian Standard Time (UTC + 5:30)
                const nowIST = new Date(new Date().getTime() + (330 * 60 * 1000));
                const ts = nowIST.toISOString().replace('T', ' ').substring(0, 19);
                tsInput.value = ts;
            }
        };
        updateTime();
        setInterval(updateTime, 1000);
    }

    // 2. Reset Backend Context
    resetJudgeContext();
});
