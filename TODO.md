# Add More Features: Explainable AI, Auto-tuning Thresholds, Graph-based Anomaly Detection

## Completed Tasks
- [x] Update requirements.txt to add shap, lime, networkx dependencies
- [x] Enhance utils/explain.py to integrate SHAP and LIME for detailed ML explanations
- [x] Modify utils/scoring.py to add auto-tuning thresholds using ROC curves or grid search
- [x] Create new utils/graph_anomaly.py module for graph-based anomaly detection (transactions as graphs, centrality/community detection)
- [x] Update HybridScorer in utils/scoring.py to include graph-based scores (e.g., 10% weight)
- [x] Integrate graph analysis into the analysis pipeline in app.py
- [x] Update README.md to document new features

## Followup Steps
- [ ] Install new dependencies and verify compatibility (in progress)
- [ ] Test new features with sample data
- [ ] Ensure performance is acceptable for large datasets
- [ ] Validate that explanations are meaningful and thresholds are optimal
