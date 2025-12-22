import shap
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class Explain:
    """
    Generate natural language explanations for anomalies using SHAP and LIME.
    """

    def __init__(self):
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = None

    def setup_explainer(self, model, training_data, feature_names):
        """
        Set up SHAP and LIME explainers with the trained model.
        """
        self.feature_names = feature_names

        # SHAP explainer for global feature importance
        try:
            self.shap_explainer = shap.TreeExplainer(model)
        except:
            self.shap_explainer = shap.Explainer(model, training_data)

        # LIME explainer for local explanations
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=training_data,
            feature_names=feature_names,
            class_names=['normal', 'anomaly'],
            mode='classification'
        )

    def generate_explanation(self, reasons, ml_score, row_features=None, model=None, is_anomalous=True, row=None, global_stats=None, graph_reasons=None):
        """
        Generate detailed explanation based on rules, ML score, SHAP, LIME, raw data context, global stats, and graph insights.
        """
        if not is_anomalous:
             return "<strong>Analysis:</strong><br>Transaction appears normal."

        # 1. Determine Probable Fraud Type and Top Factors
        fraud_type = "Anomaly"
        top_factors = []
        
        # Merge reasons and graph_reasons for processing
        all_reasons_merged = (reasons or []) + (graph_reasons or [])
        r_text = " ".join(all_reasons_merged).lower()

        # PRIORITY 1: Confirmed Structural Fraud (Loops/Cycles)
        if any("Laundering" in r or "Loop" in r or "Ping-Pong" in r or "Cycle" in r for r in all_reasons_merged):
            fraud_type = "Money Laundering Detection"
        
        # PRIORITY 2: Deterministic Rule Violations (Definitive Checks)
        elif "duplicate" in r_text:
            fraud_type = "Transaction Duplicate"
        elif "negative" in r_text or "zero" in r_text or ("amount" in r_text and "0.0" in r_text):
            fraud_type = "Invalid Amount Anomaly"
        elif "future" in r_text or "timestamp" in r_text:
            fraud_type = "Timestamp Violation"
        
        # PRIORITY 3: Statistical Graph Signals (Community/Rings)
        elif any("Community" in r for r in all_reasons_merged):
            fraud_type = "Suspicious Group Interaction"
        
        # PRIORITY 4: Behavioral/Velocity Rules
        elif reasons:
            if "location" in r_text:
                fraud_type = "Location Conflict"
            elif "gap" in r_text or "velocity" in r_text or "burst" in r_text:
                fraud_type = "High Velocity (Burst)"
            elif "missing" in r_text:
                fraud_type = "Data Integrity Violation"
            else:
                fraud_type = "Rule Violation"

        # PRIORITY 3: ML Explanation (Behavioral - SHAP)
        # Only run this if no hard rules/graphs were found, to explain "The Why" of the ML score
        elif row_features is not None and self.shap_explainer is not None and model is not None:
            try:
                shap_values = self.shap_explainer.shap_values(row_features.reshape(1, -1))
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # For binary classification

                feature_importance = dict(zip(self.feature_names, shap_values[0]))
                # Sort by absolute impact
                sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
                top_factors = [f for f, v in sorted_features[:3]] 
                
                if top_factors:
                    primary_factor = top_factors[0]
                    if 'amount' in primary_factor:
                        fraud_type = "Statistical Outlier (Amount)"
                    elif 'hour' in primary_factor or 'day' in primary_factor:
                        fraud_type = "Unusual Time Pattern"
                    elif 'frequency' in primary_factor:
                        fraud_type = "Behavioral Spike (Velocity)"
                    elif 'location' in primary_factor:
                        fraud_type = "Geospatial Anomaly"
            except Exception:
                pass
        
        # 2. Construct "Why it's suspicious" narrative (EXCLUSIVE)
        if any("Laundering" in r or "Loop" in r or "Ping-Pong" in r or "Cycle" in r for r in all_reasons_merged):
            # Find the specific cycle desc if available
            cycle_desc = ""
            for r in all_reasons_merged:
                if " -> " in r:
                    cycle_desc = r.split(": ")[-1] if ": " in r else r
                    break
            
            if "Ping-Pong" in r_text:
                why_suspicious = "Detected a direct back-and-forth money transfer pattern between two accounts, which is a common indicator of 'smurfing' or testing transaction limits."
            else:
                why_suspicious = f"Sophisticated circular laundering pattern identified: {cycle_desc or 'Funds are being moved through a closed loop to obscure their origin.'}"

        elif reasons:
            # Display unique rule violations as a natural list
            unique_reasons = list(dict.fromkeys(reasons))
            why_suspicious = "Significant policy violations: " + ", ".join(unique_reasons) + "."
            
        elif top_factors:
             readable_factors = [f.replace('_', ' ') for f in top_factors]
             why_suspicious = f"Unusual statistical behavioral patterns detected in {', '.join(readable_factors)} compared to user history."
        elif ml_score > 0.6:
             why_suspicious = "The transaction deviates significantly (top 5 percentile) from the learned behavioral model of legitimate activity."
        else:
             why_suspicious = "Anomalous signature identified by the hybrid weighted scoring engine."

        # Combine rule reasons and graph reasons for the "Triggered Rule" display
        # We use a set to avoid duplicates and join with ' | ' for a techy look
        unique_all_reasons = []
        for r in all_reasons_merged:
            # Clean up graph descriptions for the 'Triggered Rule' label
            clean_r = r.split(" (Avg")[0] if " (Avg" in r else r
            if clean_r not in unique_all_reasons:
                unique_all_reasons.append(clean_r)
        
        triggered_rules_display = " | ".join(unique_all_reasons) if unique_all_reasons else "Pure Statistical Anomaly"

        # 3. Construct "Normal Pattern" comparison
        comparison_html = "System expects standard peer-to-peer or merchant behavior."
        if global_stats and row:
            comps = []
            # Amount
            if 'amount' in row and 'mean_amount' in global_stats:
                amt = float(row['amount'])
                avg = global_stats['mean_amount']
                if amt > avg * 1.5:
                     comps.append(f"Amount: <b>₹{amt:,.2f}</b> (Network Typical: ₹{avg:,.2f})")
            
            if comps:
                comparison_html = "<br>".join(comps)
            elif not is_anomalous:
                comparison_html = "Values align with established statistical baselines."
            else:
                comparison_html = "Data points deviate from the multifaceted behavioral baseline established for this user/network."

        # 4. Confidence Score
        # If a deterministic rule/graph algo triggered, we are 100% confident.
        if all_reasons_merged: # Use all_reasons_merged to check if any rule/graph reason exists
            confidence = "100.0"
        else:
            confidence = f"{ml_score * 100:.1f}" if ml_score > 0 else "N/A (Rule Only)"
        
        # 5. Build HTML
        html = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 0.9rem; line-height: 1.6;">
            <div style="margin-bottom: 5px;"><strong>Triggered Rule:</strong> <span style="color: #ff3b3b;">{triggered_rules_display}</span></div>
            <div style="margin-bottom: 5px;"><strong>Why Suspicious:</strong> {why_suspicious}</div>
            <div style="margin-bottom: 5px;"><strong>Normal Pattern:</strong> <div style="padding-left: 20px; font-size: 0.85rem; color: #666;">{comparison_html}</div></div>
            <div style="margin-bottom: 5px;"><strong>Confidence:</strong> <b>{confidence}%</b></div>
            <div style="margin-bottom: 5px;"><strong>Probable Type:</strong> <span style="background: rgba(255, 59, 59, 0.1); color: #ff3b3b; padding: 2px 6px; border-radius: 4px; font-weight: 600;">{fraud_type}</span></div>
        </div>
        """
        
        return html
