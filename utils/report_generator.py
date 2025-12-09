from fpdf import FPDF
import pandas as pd
import datetime
import textwrap
from bs4 import BeautifulSoup


# =========================================================
# 1) CLEAN HTML → TEXT (for explanation column)
# =========================================================
def clean_explanation(html_text):
    """
    Convert HTML explanation containing <div>, <strong>, <span>, etc.
    Into readable text for PDF report.
    """
    if not isinstance(html_text, str):
        return str(html_text)

    soup = BeautifulSoup(html_text, "html.parser")
    lines = []

    # Strategy: Find specific div blocks from explain.py or fall back to list logic
    
    # 1. Parse div-based structure (New Format)
    divs = soup.find_all("div", style=lambda value: value and "margin-bottom" in value)
    if divs:
        for div in divs:
            text = div.get_text(" ", strip=True)
            # Remove emojis for PDF compatibility (required for FPDF)
            text = text.encode('latin-1', 'ignore').decode('latin-1') 
            lines.append(f"- {text}")
            
    # 2. Parse list-based structure (Legacy Format / Comparison)
    elif soup.find("li"):
        for tag in soup.find_all(True):
            if tag.name == "strong":
                title = tag.get_text(strip=True)
                if title:
                    lines.append(f"{title.upper()}:")
            if tag.name == "li":
                txt = tag.get_text(" ", strip=True)
                if txt:
                    lines.append(f"  - {txt}")
                    
    # 3. Fallback: Just get text
    else:
        # If explicit divs aren't found, try getting all text but preserving strict lines
        text = soup.get_text("\n", strip=True)
        if text:
            lines.append(text)

    return "\n".join(lines) if lines else "Details not available in readable format."



# =========================================================
# 2) CUSTOM PDF CLASS (supports multiline wrapped table rows)
# =========================================================
class NeoFintechPDF(FPDF):

    def header(self):
        self.set_fill_color(10, 10, 10)
        self.rect(0, 0, 210, 40, 'F')

        self.set_font("Arial", "B", 22)
        self.set_text_color(0, 255, 200)
        self.cell(0, 18, "INTELLIGENCE BRIEFING", 0, 1, "C")

        self.set_font("Arial", "I", 10)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "CONFIDENTIAL // NEO-FINTECH SYSTEMS", 0, 1, "C")

        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    # =========================================================
    # MULTI-LINE WRAPPED TABLE ROW (WORKING + SAFE)
    # =========================================================
    def multi_cell_row(self, widths, data, h=6):
        wrapped = []
        max_lines = 1

        # Wrap each cell's text
        for i, text in enumerate(data):
            text = str(text)
            wrap = textwrap.wrap(text, width=int(widths[i] / 2.2))
            wrapped.append(wrap)
            max_lines = max(max_lines, len(wrap))

        row_height = max_lines * h
        x_start = self.get_x()
        y_start = self.get_y()

        # Page break check
        if y_start + row_height > 275:
            self.add_page()
            x_start = self.get_x()
            y_start = self.get_y()

        # Print line by line
        for line in range(max_lines):
            self.set_x(x_start)

            for col_index, width in enumerate(widths):
                txt = wrapped[col_index][line] if line < len(wrapped[col_index]) else ""
                self.multi_cell(width, h, txt, border=1, align="L")
                self.set_xy(x_start + sum(widths[:col_index + 1]),
                            y_start + (line * h))

        # Move cursor to end of row
        self.set_xy(x_start, y_start + row_height)



# =========================================================
# 3) REPORT GENERATOR
# =========================================================
class ReportGenerator:

    def generate_report(self, df, stats, output_path):
        pdf = NeoFintechPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # ------------------------------------------------------
        # GLOBAL STATS
        # ------------------------------------------------------
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, "Mission Status: Analysis Complete", 0, 1)

        pdf.set_font("Arial", "", 11)
        pdf.cell(
            0, 8,
            f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            0, 1,
        )
        pdf.ln(5)

        total_txns = len(df)
        anomalies = df[df.get("is_anomalous", False) == True]
        anomaly_count = len(anomalies)
        anomaly_rate = (anomaly_count / total_txns * 100) if total_txns else 0

        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(65, 12, f"Total Txns: {total_txns}", 1, 0, "C", True)
        pdf.cell(65, 12, f"Anomalies: {anomaly_count}", 1, 0, "C", True)
        pdf.cell(65, 12, f"Threat Level: {anomaly_rate:.1f}%", 1, 1, "C", True)
        pdf.ln(8)

        # ------------------------------------------------------
        # TOP THREATS HEADER
        # ------------------------------------------------------
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, "Top High-Risk Targets", 0, 1)
        pdf.set_text_color(0, 0, 0)

        if anomalies.empty:
            pdf.cell(0, 10, "No anomalies detected. System secure.", 0, 1)
            pdf.output(output_path)
            return

        if "final_score" in anomalies.columns:
            anomalies = anomalies.sort_values("final_score", ascending=False)

        top_10 = anomalies.head(10)

        # ------------------------------------------------------
        # TABLE HEADER
        # ------------------------------------------------------
        col_widths = [30, 30, 30, 20, 90]
        headers = ["Txn ID", "User ID", "Amount", "Score", "Explanation"]

        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(40, 40, 40)
        pdf.set_text_color(255, 255, 255)

        for w, header in zip(col_widths, headers):
            pdf.cell(w, 10, header, 1, 0, "C", True)
        pdf.ln(10)

        # ------------------------------------------------------
        # TABLE ROWS
        # ------------------------------------------------------
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)

        for _, row in top_10.iterrows():

            cleaned_explanation = clean_explanation(
                row.get("explanation", "N/A")
            )

            pdf.multi_cell_row(
                col_widths,
                [
                    row.get("transaction_id", "N/A"),
                    row.get("user_id", "N/A"),
                    f"INR {float(row.get('amount', 0)):,.0f}",
                    f"{row.get('final_score', 0):.3f}",
                    cleaned_explanation,
                ],
                h=6,
            )

        pdf.output(output_path)
