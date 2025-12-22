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
            return str(val).strip() if pd.notna(val) else default
    return default

# =========================================================
# 1) CLEAN HTML → TEXT (for explanation column)
# =========================================================
def clean_explanation(html_text):
    """
    Extracts high-impact detection logs. 
    Removes overlaps, duplicates, and redundant noise (Triggered Rule, etc.)
    """
    if not isinstance(html_text, str): return "N/A"

    soup = BeautifulSoup(html_text, "html.parser")
    found_reasons = []
    seen = set()

    for tag in soup.find_all(["div", "li"]):
        txt = tag.get_text(" ", strip=True)
        # Remove noisy prefixes that judges don't need to see in a table
        txt = txt.replace("Triggered Rule:", "").replace("WHY:", "").replace("Why Suspicious:", "").strip()
        txt = txt.encode('latin-1', 'ignore').decode('latin-1')
        
        # Check for near-duplicates (Loops often repeat the path)
        # If the start of a long string is already seen, skip it
        is_sub = False
        core_path = txt.split("(Avg")[0] if "(Avg" in txt else txt[:30]
        if core_path in seen: is_sub = True
        
        if txt and not is_sub and len(txt) > 5:
            seen.add(core_path)
            found_reasons.append(txt)

    if not found_reasons: return "Nominal."

    # Return only the FIRST unique reason for ultra-concise results
    core = found_reasons[0]
    
    # Final cleanup of common long strings
    core = core.replace("Money Laundering Loop Detected:", "ML Loop:").strip()
    
    return f"DETECTION: {core}"



# =========================================================
# 2) CUSTOM PDF CLASS (supports multiline wrapped table rows)
# =========================================================
class NeoFintechPDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def header(self):
        # Dark Tech Header Bar
        self.set_fill_color(10, 12, 20)
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_draw_color(0, 242, 234) # Neo Cyan
        self.line(0, 35, 210, 35)

        self.set_font("Arial", "B", 20)
        self.set_text_color(0, 242, 234) 
        self.set_y(8)
        self.cell(0, 10, "VIGILO // INTELLIGENCE DOSSIER", 0, 1, "C")

        self.set_font("Arial", "", 8)
        self.set_text_color(112, 0, 255) # Purple
        self.cell(0, 5, "HYBRID ANALYTICS CORE // AUTHENTICATED ACCESS", 0, 1, "C")
        self.ln(15)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"AUTHENTICATED VIA VIGILO SECURITY PORTAL | PAGE {self.page_no()}", 0, 0, "C")

    def multi_cell_row(self, widths, data, h=6):
        wrapped = []
        max_lines = 1

        for i, text in enumerate(data):
            text = str(text)
            wrap = textwrap.wrap(text, width=int(widths[i] / 2.2))
            wrapped.append(wrap)
            max_lines = max(max_lines, len(wrap))

        row_height = max_lines * h
        x_start = self.get_x()
        y_start = self.get_y()

        if y_start + row_height > 270:
            self.add_page()
            x_start = self.get_x()
            y_start = self.get_y()

        for line in range(max_lines):
            self.set_x(x_start)
            for col_index, width in enumerate(widths):
                txt = wrapped[col_index][line] if line < len(wrapped[col_index]) else ""
                
                self.set_fill_color(255, 255, 255) # White fill
                self.set_text_color(0, 0, 0)       # High Contrast Black
                self.set_draw_color(180, 180, 180) # Gray borders
                
                self.multi_cell(width, h, txt, border=1, align="L", fill=True)
                self.set_xy(x_start + sum(widths[:col_index + 1]),
                            y_start + (line * h))

        self.set_xy(x_start, y_start + row_height)



# =========================================================
# 3) REPORT GENERATOR
# =========================================================
class ReportGenerator:

    def generate_report(self, df, stats, output_path):
        pdf = NeoFintechPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 70, 150) # Deep Blue Header
        pdf.cell(0, 10, "SECTION 01: EXECUTIVE OVERVIEW", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(80, 80, 80) # Dark gray text
        pdf.cell(0, 6, f"Dossier ID: {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1)
        pdf.ln(5)

        # High Level Metrics
        total_txns = len(df)
        anomalies = df[df.get("is_anomalous", False) == True]
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_txns * 100) if total_txns else 0
        
        # Threat Level Color Logic
        if anomaly_rate > 10:
            level_txt = "CRITICAL THREAT"
            level_color = (180, 0, 0)
        elif anomaly_rate > 3:
            level_txt = "ELEVATED RISK"
            level_color = (180, 100, 0)
        else:
            level_txt = "NOMINAL / SECURE"
            level_color = (0, 120, 60)

        pdf.set_draw_color(level_color[0], level_color[1], level_color[2])
        pdf.set_fill_color(248, 248, 255) # Very light blue tint fill
        pdf.rect(pdf.get_x(), pdf.get_y(), 190, 25, 'FD')
        
        pdf.set_xy(pdf.get_x() + 5, pdf.get_y() + 5)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(level_color[0], level_color[1], level_color[2])
        pdf.cell(100, 8, f"STATUS: {level_txt}", 0, 0)
        pdf.set_font("Arial", "B", 20)
        pdf.cell(80, 15, f"{anomaly_rate:.1f}%", 0, 1, "R")
        
        pdf.set_xy(10, pdf.get_y() + 15)
        
        # ------------------------------------------------------
        # BEHAVIORAL BASELINES
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

        # ------------------------------------------------------
        # TOP THREATS SECTION
        # ------------------------------------------------------
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(180, 0, 0) # Professional Red
        pdf.cell(0, 10, "SECTION 03: HIGH-CONFIDENCE ANOMALY DETECTION", 0, 1)
        
        if anomalies.empty:
            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, "Scan Complete. No active threats identified in this batch.", 0, 1)
        else:
            if "final_score" in anomalies.columns:
                anomalies = anomalies.sort_values("final_score", ascending=False)

            top_10 = anomalies.head(10)

            # Column widths: 45 for long Txn IDs, 30 for User IDs
            col_widths = [45, 30, 20, 15, 80]
            headers = ["TRANSACTION ID", "USER ID", "AMOUNT", "SCORE", "DETECTION LOG"]

            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(230, 235, 245) # Professional bluish-gray header
            pdf.set_text_color(0, 50, 100) # Deep Navy for headers

            for w, header in zip(col_widths, headers):
                pdf.cell(w, 8, header, 1, 0, "C", True)
            pdf.ln(8)

            pdf.set_font("Arial", "", 8)
            pdf.set_text_color(0, 0, 0)
            for _, row in top_10.iterrows():
                cleaned_explanation = clean_explanation(row.get("explanation", "N/A"))
                
                # Robust ID Fetching
                txn_id = get_col(row, ["transaction_id", "Transaction ID", "txn_id", "id", "trans_id", "transaction"])
                user_id = get_col(row, ["user_id", "User ID", "uid", "sender_id", "customer_id"])
                
                pdf.multi_cell_row(
                    col_widths,
                    [
                        txn_id,
                        user_id,
                        f"INR {float(row.get('amount', 0)):,.0f}",
                        f"{row.get('final_score', 0):.2f}",
                        cleaned_explanation,
                    ],
                    h=5,
                )

        # ------------------------------------------------------
        # FOOTER / SIGN OFF
        # ------------------------------------------------------
        if pdf.get_y() > 240: pdf.add_page()
        
        pdf.ln(20)
        pdf.set_draw_color(0, 70, 150)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(0, 70, 150)
        pdf.cell(0, 6, "CONFIRMATION OF ANALYSIS", 0, 1)
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5, "This report was autonomously generated by the VIGILO Hybrid Scoring Engine. All detections are based on a merge of Rule Guards, Isolation Forest (UAIC), and Graph Temporal Analysis.")
        
        pdf.ln(10)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(40, 40, 80) 
        pdf.cell(100, 5, "ANALYST SIGNATURE", 0, 0)
        pdf.cell(90, 5, "SYSTEM TIMESTAMP", 0, 1)
        
        pdf.ln(2)
        pdf.set_font("Courier", "B", 12)
        pdf.set_text_color(0, 70, 150)
        pdf.cell(100, 10, "Digital_Seal_VIGILO_CORE", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(90, 10, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 0, 1)

        pdf.output(output_path)
