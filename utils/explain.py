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
        
        # Analyze row_features with SHAP if available
        if row_features is not None and self.shap_explainer is not None and model is not None:
            try:
                shap_values = self.shap_explainer.shap_values(row_features.reshape(1, -1))
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # For binary classification

                feature_importance = dict(zip(self.feature_names, shap_values[0]))
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                top_factors = [f for f, v in sorted_features[:3] if v > 0] # Take top positive contributors
                
                if top_factors:
                    primary_factor = top_factors[0]
                    if 'amount' in primary_factor:
                        fraud_type = "High Value Anomaly"
                    elif 'hour' in primary_factor or 'day' in primary_factor:
                        fraud_type = "Temporal Anomaly" # Unusual time
                    elif 'frequency' in primary_factor:
                        fraud_type = "Velocity/Frequency Anomaly"
                    elif 'location' in primary_factor:
                        fraud_type = "Location Mismatch"
            except Exception:
                pass
        
        # Fallback to Graph Reasons for Fraud Type
        if fraud_type == "Anomaly" and graph_reasons:
             if any('Community' in r for r in graph_reasons):
                 fraud_type = "Graph Clustercring Anomaly"
             elif any('Interaction' in r for r in graph_reasons):
                 fraud_type = "Network Interaction Risk"
        
        # Fallback fraud type from rules if ML didn't decide
        if fraud_type == "Anomaly" and reasons:
            if any('Amount' in r for r in reasons):
                 fraud_type = "Rule-Based: Value Exception"
            elif any('Location' in r for r in reasons):
                 fraud_type = "Rule-Based: Location Risk"
        
        # 2. Construct "Why it's suspicious" narrative
        narrative_parts = []
        if reasons:
            narrative_parts.append(f"Violated {len(reasons)} static rule(s)")
            
        if graph_reasons:
            narrative_parts.append(f"Graph Analysis: {', '.join(graph_reasons)}")
        
        if top_factors:
             readable_factors = [f.replace('_', ' ') for f in top_factors]
             narrative_parts.append(f"Unusual statistical patterns in {', '.join(readable_factors)}")
        elif ml_score > 0.6 and not graph_reasons:
             narrative_parts.append("Deviates significantly from learned behavioral model")
             
        why_suspicious = "; ".join(narrative_parts) + "."

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
            <div style="margin-bottom: 5px;">✅ <strong>Triggered Rule:</strong> <span style="color: #ff3b3b;">{', '.join(reasons) if reasons else 'None (Pure ML/Graph Detection)'}</span></div>
            <div style="margin-bottom: 5px;">❓ <strong>Why Suspicious:</strong> {why_suspicious}</div>
            <div style="margin-bottom: 5px;">📊 <strong>Normal Pattern:</strong> <div style="padding-left: 20px; font-size: 0.85rem; color: #666;">{comparison_html}</div></div>
            <div style="margin-bottom: 5px;">🎯 <strong>Confidence:</strong> <b>{confidence}%</b></div>
            <div style="margin-bottom: 5px;">🕵️ <strong>Probable Type:</strong> <span style="background: rgba(255, 59, 59, 0.1); color: #ff3b3b; padding: 2px 6px; border-radius: 4px; font-weight: 600;">{fraud_type}</span></div>
        </div>
        """
        
        return html
