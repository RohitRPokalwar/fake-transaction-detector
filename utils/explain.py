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

        # PRIORITY 1: Rule Violations (Definitive & Exclusive)
        if reasons:
            r_text = " ".join(reasons).lower()
            if "duplicate" in r_text:
                fraud_type = "Transaction Duplicate"
            elif "future" in r_text or "timestamp" in r_text:
                fraud_type = "Timestamp Violation"
            elif "negative" in r_text or "amount" in r_text or "zero" in r_text:
                fraud_type = "Amount Anomaly"
            elif "location" in r_text:
                fraud_type = "Location Conflict"
            elif "gap" in r_text or "velocity" in r_text or "burst" in r_text:
                fraud_type = "High Velocity (Burst)"
            elif "missing" in r_text:
                fraud_type = "Data Integrity Violation"
            else:
                fraud_type = "Rule Violation"

        # PRIORITY 2: Graph Analysis (Structural)
        elif graph_reasons:
             r_text_g = str(graph_reasons)
             if 'Loop' in r_text_g:
                 fraud_type = "Money Laundering Loop"
             elif any('Community' in r for r in graph_reasons):
                 fraud_type = "Money Laundering Ring"
             elif any('Interaction' in r for r in graph_reasons):
                 fraud_type = "Graph Interaction Risk"
             else:
                 fraud_type = "Graph Structural Anomaly"

        # PRIORITY 3: ML Explanation (Behavioral - SHAP)
        # Only run this if no hard rules were broken, to explain "The Why" of the ML score
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
        if reasons:
            # User request: "If Transaction is Duplicate show that Only not other Anamoly"
            # We display the raw rule reason(s) directly
            why_suspicious = "; ".join(reasons) + "."
            
        elif graph_reasons:
            why_suspicious = "; ".join(graph_reasons) + "."
            
        elif top_factors:
             readable_factors = [f.replace('_', ' ') for f in top_factors]
             why_suspicious = f"Unusual statistical patterns in {', '.join(readable_factors)}."
        elif ml_score > 0.6:
             why_suspicious = "Deviates significantly from learned behavioral model."
        else:
             why_suspicious = "Anomaly detected by hybrid scoring logic."

        # Combine rule reasons and graph reasons for the "Triggered Rule" display
        all_reasons = (reasons or []) + (graph_reasons or [])

        # 3. Construct "Normal Pattern" comparison
        comparison_html = "No historical data available for comparison."
        if global_stats and row:
            comps = []
            # Amount
            if 'amount' in row and 'mean_amount' in global_stats:
                amt = float(row['amount'])
                avg = global_stats['mean_amount']
                if amt > avg * 1.5:
                     comps.append(f"Amount: <b>${amt:,.2f}</b> (Normal Avg: ${avg:,.2f})")
            
            # Velocity (if computed for this user/session)
            # Currently simplistic
            
            if comps:
                comparison_html = "<br>".join(comps)
            else:
                comparison_html = "Values are within statistical deviation ranges, but pattern is complex."

        # 4. Confidence Score
        confidence = f"{ml_score * 100:.1f}" if ml_score > 0 else "N/A (Rule Only)"
        
        # 5. Build HTML
        html = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 0.9rem; line-height: 1.6;">
            <div style="margin-bottom: 5px;"><strong>Triggered Rule:</strong> <span style="color: #ff3b3b;">{', '.join(all_reasons) if all_reasons else 'None (Pure ML Detection)'}</span></div>
            <div style="margin-bottom: 5px;"><strong>Why Suspicious:</strong> {why_suspicious}</div>
            <div style="margin-bottom: 5px;"><strong>Normal Pattern:</strong> <div style="padding-left: 20px; font-size: 0.85rem; color: #666;">{comparison_html}</div></div>
            <div style="margin-bottom: 5px;"><strong>Confidence:</strong> <b>{confidence}%</b></div>
            <div style="margin-bottom: 5px;"><strong>Probable Type:</strong> <span style="background: rgba(255, 59, 59, 0.1); color: #ff3b3b; padding: 2px 6px; border-radius: 4px; font-weight: 600;">{fraud_type}</span></div>
        </div>
        """
        
        return html
