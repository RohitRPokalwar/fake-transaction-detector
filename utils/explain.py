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
        if any("Laundering" in r or "Loop" in r or "Ping-Pong" in r or "Cycle" in r or "Circle" in r for r in all_reasons_merged):
            fraud_type = "Organized Money Laundering"
        
        # PRIORITY 2: Deterministic Rule Violations (Definitive Checks)
        elif "copy-paste" in r_text or "duplicate" in r_text:
            fraud_type = "Transaction Replay Attack"
        elif "ghost" in r_text or "negative" in r_text or "zero" in r_text:
            fraud_type = "Invalid Money Value"
        elif "travel" in r_text or "future" in r_text or "timestamp" in r_text:
            fraud_type = "Time/Location Logic Error"
        
        # PRIORITY 3: Statistical Graph Signals (Stranger Danger)
        elif "stranger" in r_text or any("Community" in r for r in all_reasons_merged):
            fraud_type = "Suspicious Network Jump"
        
        # PRIORITY 4: Behavioral/Velocity Rules
        elif reasons:
            if "teleportation" in r_text or "location" in r_text:
                fraud_type = "Physical Impossibility"
            elif "burst" in r_text or "velocity" in r_text:
                fraud_type = "High-Speed Bot Attack"
            elif "incomplete" in r_text or "missing" in r_text:
                fraud_type = "Broken Identity Data"
            else:
                fraud_type = "Security Policy Violation"

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
        if any("Laundering" in r or "Loop" in r or "Ping-Pong" in r or "Cycle" in r or "Circle" in r for r in all_reasons_merged):
            # Find the specific cycle desc if available
            cycle_desc = ""
            for r in all_reasons_merged:
                if " -> " in r:
                    cycle_desc = r.split(": ")[-1] if ": " in r else r
                    break
            
            if "Ping-Pong" in r_text:
                why_suspicious = "Money is bouncing back and forth rapidly between two accounts—a classic tactic to test transaction limits."
            else:
                why_suspicious = f"A hidden money-cleansing ring was found. Funds are moving in a loop: {cycle_desc or 'moving through a closed circle to hide their origin.'}"

        elif reasons:
            # Display unique rule violations as a natural list
            unique_reasons = list(dict.fromkeys(reasons))
            why_suspicious = "The system blocked this because: " + ", ".join(unique_reasons) + "."
            
        elif top_factors:
             readable_factors = [f.replace('_', ' ') for f in top_factors]
             why_suspicious = f"This transaction looks weird for this user. Specifically, the {', '.join(readable_factors)} don't match their usual habits."
        elif ml_score > 0.6:
             why_suspicious = "Our AI model flagged this because it looks significantly different from 95% of normal transactions."
        else:
             why_suspicious = "Suspicious digital fingerprint identified by our hybrid security engine."

        # Combine rule reasons and graph reasons for the "Triggered Rule" display
        # We use a set to avoid duplicates and join with ' | ' for a techy look
        unique_all_reasons = []
        for r in all_reasons_merged:
            # Clean up graph descriptions for the 'Triggered Rule' label
            clean_r = r.split(" (Avg")[0] if " (Avg" in r else r
            if clean_r not in unique_all_reasons:
                unique_all_reasons.append(clean_r)
        
        triggered_rules_display = " | ".join(unique_all_reasons) if unique_all_reasons else "Pure Statistical Anomaly"


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
            <div style="margin-bottom: 5px;"><strong>Confidence:</strong> <b>{confidence}%</b></div>
            <div style="margin-bottom: 5px;"><strong>Probable Type:</strong> <span style="background: rgba(255, 59, 59, 0.1); color: #ff3b3b; padding: 2px 6px; border-radius: 4px; font-weight: 600;">{fraud_type}</span></div>
        </div>
        """
        
        return html
