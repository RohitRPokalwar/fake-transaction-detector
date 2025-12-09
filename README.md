# Fake Transaction Detector

A hybrid rule-based and AI/ML system for automatically identifying fake, incorrect, fabricated, or abnormal transaction records in large datasets.

## Features

- **Deterministic Data Integrity Engine (DDIE)**: Rule-based validation for duplicates, timestamps, amounts, missing fields, time gaps, and location conflicts
- **Statistical Signature Generator (SSG)**: Computes global and per-user transaction patterns, percentiles, IQR, deviation bands
- **Unsupervised Anomaly Isolation Core (UAIC)**: Uses Isolation Forest algorithm for ML-based anomaly detection
- **Graph-based Anomaly Detection**: Models transactions as graphs with users as nodes and detects anomalies using centrality measures and community detection
- **Explainable AI**: Provides detailed explanations using SHAP (Shapley Additive Explanations) and LIME (Local Interpretable Model-agnostic Explanations)
- **Auto-tuning Thresholds**: Dynamically adjusts anomaly detection thresholds using ROC curves or percentile-based methods
- **Hybrid Scoring**: Combines rule_score (40%), ml_score (50%), and graph_score (10%) with auto-tuned threshold
- **Flask Backend**: Lightweight API server with direct ML inference
- **Responsive Frontend**: Dark-themed dashboard with Chart.js visualizations, file upload, and download functionality

## Architecture

```
CSV Upload → Preprocessing → DDIE Rules → SSG Stats → UAIC ML → Hybrid Scoring → Explanations → Dashboard
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open http://127.0.0.1:5000/ in your browser

## Usage

1. Upload a CSV file with transaction data (columns: transaction_id, user_id, amount, timestamp, location)
2. The system will analyze the data and display results
3. View summary statistics, anomaly charts, and detailed transaction table
4. Download anomalous transactions as CSV

## Sample Data

Use `sample_data/sample.csv` for testing, which includes various anomalies like duplicates, future timestamps, negative amounts, and missing fields.

## API Endpoints

- `GET /`: Main dashboard
- `POST /api/analyze`: Analyze uploaded CSV file

## Technologies Used

- Python (Flask, Pandas, NumPy, scikit-learn, SHAP, LIME, NetworkX)
- HTML/CSS/JavaScript (Chart.js)
- Isolation Forest for anomaly detection
- Graph-based anomaly detection with NetworkX and community detection
- Explainable AI with SHAP and LIME

## Future Enhancements

- Real-time streaming with Apache Kafka
- Explainable AI with SHAP/LIME
- Auto-tuning thresholds
- Graph-based anomaly detection
- Cloud deployment (AWS/GCP/Render)

## License

This project is for educational and demonstration purposes.
