from fpdf import FPDF
import pandas as pd
import datetime
import textwrap
from bs4 import BeautifulSoup

# =========================================================
# 0) COLUMN RESOLVER
# =========================================================
def get_col(row, options, default="N/A"):
    # Convert all keys to lowercase and strip for a robust search
    row_keys_lower = {str(k).lower().strip(): k for k in row.keys()}
    for opt in options:
        opt_lower = opt.lower().strip()
        if opt_lower in row_keys_lower:
            val = row[row_keys_lower[opt_lower]]
            if pd.notna(val) and str(val).strip() != "":
                return str(val).strip()
    return default

# =========================================================
# 1) CLEAN HTML → TEXT
# =========================================================
def clean_explanation(html_text):
    """
    Extracts high-impact detection logs for the report table.
    Removes technical noise for a cleaner judgment interface.
    """
    if not isinstance(html_text, str): return "N/A"

    try:
        soup = BeautifulSoup(html_text, "html.parser")
        found_reasons = []
        seen = set()

        for tag in soup.find_all(["div", "li"]):
            txt = tag.get_text(" ", strip=True)
            # Remove redundant formatting and prefixes
            txt = txt.replace("Triggered Rule:", "").replace("WHY:", "").replace("Why Suspicious:", "").strip()
            txt = txt.encode('latin-1', 'ignore').decode('latin-1')
            
            # De-duplication check
            core_path = txt.split("(Avg")[0] if "(Avg" in txt else txt[:30]
            if txt and core_path not in seen and len(txt) > 5:
                seen.add(core_path)
                found_reasons.append(txt)

        if not found_reasons: return "Nominal."

        # Return only the most impactful primary reason
        core = found_reasons[0]
        core = core.replace("Money Circle: Funds are moving in a loop to hide their source", "ML Loop:").strip()
        
        return f"DETECTION: {core}"
    except:
        return "Analyzed Pattern"

# =========================================================
# 2) CUSTOM PDF CLASS (Premium High-Visibility)
# =========================================================
class ReportGenV2(FPDF):
    def header(self):
        # Dark Background Header
        self.set_fill_color(15, 20, 45) # Professional Midnight Blue
        self.rect(0, 0, 210, 35, 'F')
        
        # Cyan Border Line
        self.set_draw_color(0, 240, 255) 
        self.line(0, 35, 210, 35)

        self.set_font("Arial", "B", 24)
        self.set_text_color(0, 240, 255) # Cyan
        self.set_y(10)
        self.cell(0, 10, "VIGILO // SECURITY CLASSIFIED", 0, 1, "C")

        self.set_font("Arial", "", 8)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, "HYBRID FRAUD DETECTION AUDIT // INTERNAL USE ONLY", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"VIGILO SECURITY CORE | Page {self.page_no()}", 0, 0, "C")

    def create_table_row(self, widths, data, h=6):
        # Calculate height first
        wrapped_data = []
        max_lines = 1
        for i, text in enumerate(data):
            t = str(text) if text else "N/A"
            lines = textwrap.wrap(t, width=int(widths[i] / 2.2))
            if not lines: lines = [" "]
            wrapped_data.append(lines)
            max_lines = max(max_lines, len(lines))

        row_height = max_lines * h
        x_start = self.get_x()
        y_start = self.get_y()

        # Check for page break
        if y_start + row_height > 270:
            self.add_page()
            x_start = self.get_x()
            y_start = self.get_y()

        current_x = x_start
        for i, lines in enumerate(wrapped_data):
            self.set_xy(current_x, y_start)
            
            # --- COLOR LOGIC (AS REQUESTED) ---
            if i == 0:
                # USER ID: Light Gray BG + Bold Black Text (NEVER WHITE)
                self.set_fill_color(235, 235, 245)
                self.set_text_color(0, 0, 0)
                self.set_font("Arial", "B", 8)
            elif i == 2:
                # TRANSACTION ID: White BG + Royal Blue + Bold
                self.set_fill_color(255, 255, 255)
                self.set_text_color(0, 80, 200)
                self.set_font("Arial", "B", 8)
            else:
                # OTHERS: White BG + Dark Black Text
                self.set_fill_color(255, 255, 255)
                self.set_text_color(30, 30, 30)
                self.set_font("Arial", "", 8)

            self.set_draw_color(180, 180, 180)
            
            # Use multi_cell for each column manually
            # Combine lines back because multi_cell wraps internally
            formatted_text = "\n".join(lines)
            self.multi_cell(widths[i], h, formatted_text, border=1, align="L", fill=True)
            
            current_x += widths[i]
        
        # Advance cursor to below the entire row
        self.set_xy(x_start, y_start + row_height)

# =========================================================
# 3) EXPORT CLASS
# =========================================================
class ReportGeneratorV2:
    def generate_report(self, df, stats, output_path):
        pdf = ReportGenV2()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # --------------------------------------------------
        # SECTION 1: EXECUTIVE OVERVIEW
        # --------------------------------------------------
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 70, 150)
        pdf.cell(0, 10, "SECTION 01: EXECUTIVE OVERVIEW", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, f"Dossier ID: {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1)
        pdf.ln(5)

        total_txns = len(df)
        anomalies = df[df.get("is_anomalous", False) == True].copy()
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_txns * 100) if total_txns else 0
        
        # Threat Box
        level_color = (0, 120, 60) if anomaly_rate < 3 else (180, 100, 0) if anomaly_rate < 10 else (180, 0, 0)
        level_txt = "NOMINAL" if anomaly_rate < 3 else "ELEVATED" if anomaly_rate < 10 else "CRITICAL"

        pdf.set_draw_color(*level_color)
        pdf.set_fill_color(248, 248, 255)
        pdf.rect(10, pdf.get_y(), 190, 20, 'FD')
        
        pdf.set_xy(15, pdf.get_y() + 5)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(*level_color)
        pdf.cell(100, 10, f"THREAT LEVEL: {level_txt}", 0, 0)
        pdf.set_font("Arial", "B", 18)
        pdf.cell(75, 10, f"{anomaly_rate:.1f}% Risks Found", 0, 1, "R")
        
        pdf.ln(15)

        # ------------------------------------------------------
        # SECTION 02: GLOBAL BEHAVIORAL BASELINES
        # ------------------------------------------------------
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 70, 150)
        pdf.cell(0, 10, "SECTION 02: GLOBAL BEHAVIORAL BASELINES", 0, 1)
        pdf.ln(2)

        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(40, 40, 40)
        baseline_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Volume", f"{total_txns}", "Unique Users", f"{stats.get('unique_users', 'N/A')}"],
            ["Max Txn Value", f"INR {stats.get('max_amount', 0):,.2f}" ,"Most Active User", f"{stats.get('most_active_user_id', 'N/A')}"],
        ]

        # Simple Grid
        cell_w = 47.5
        pdf.set_draw_color(220, 220, 220)
        pdf.set_fill_color(250, 250, 250)
        for row_data in baseline_data:
            for item in row_data:
                pdf.cell(cell_w, 8, str(item), 1, 0, "L", fill=True)
            pdf.ln(8)

        pdf.ln(10)

        # --------------------------------------------------
        # SECTION 03: HIGH-RISK DETECTION LOG
        # --------------------------------------------------
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(180, 0, 0) # Alert Red
        pdf.cell(0, 10, "SECTION 03: HIGH-RISK ANOMALY DETECTION LOG", 0, 1)

        # 1. Resolve Columns
        id_cols = ["transaction_id", "txn_id", "id", "Transaction ID"]
        user_cols = ["user_id", "sender_id", "uid", "sender"]
        recv_cols = ["recipient_id", "receiver_id", "to_id", "receiver"]
        
        # 2. Prep Table Config
        # Order: User ID, Receiver ID, Transaction ID, Amount, SC, Log
        widths = [30, 30, 35, 15, 10, 70]
        headers = ["USER ID", "RECEIVER ID", "TXN ID", "AMOUNT", "SC", "DETECTION LOG"]

        # Always Draw Table Header
        pdf.set_font("Arial", "B", 8)
        pdf.set_fill_color(30, 45, 75) # Dark Navy Header
        pdf.set_text_color(255, 255, 255)
        for w, h_text in zip(widths, headers):
            pdf.cell(w, 10, h_text, 1, 0, "C", True)
        pdf.ln(10)

        # 3. Draw Data or Empty Message
        if anomalies.empty:
            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, "No active threats identified in the current transaction pool.", 1, 1, "C")
        else:
            # Sort by Txn ID as requested
            anomalies['res_id'] = anomalies.apply(lambda r: get_col(r, id_cols), axis=1)
            anomalies = anomalies.sort_values("res_id", ascending=True)

            for _, row in anomalies.head(100).iterrows():
                u_id = get_col(row, user_cols)
                r_id = get_col(row, recv_cols)
                t_id = row['res_id']
                amt  = f"{float(row.get('amount', 0)):,.0f}" if pd.notna(row.get('amount')) else "0"
                sc   = f"{float(row.get('final_score', 0)):.2f}"
                log  = clean_explanation(row.get("explanation", "N/A"))

                pdf.create_table_row(widths, [u_id, r_id, t_id, amt, sc, log])

        # --------------------------------------------------
        # SECTION 3: SYSTEM AUDIT SIGNATURE
        # --------------------------------------------------
        if pdf.get_y() > 240: pdf.add_page()
        pdf.ln(20)
        pdf.set_draw_color(0, 80, 160)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(0, 80, 160)
        pdf.cell(100, 5, "SECURITY ANALYST SIGNATURE", 0, 0)
        pdf.cell(90, 5, "AUDIT TIMESTAMP", 0, 1)
        
        pdf.ln(2)
        pdf.set_font("Courier", "B", 12)
        pdf.set_text_color(0, 80, 160)
        pdf.cell(100, 10, "X-CORE_ENCRYPTED_SIGN_77", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(90, 10, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 0, 1)

        pdf.output(output_path)
