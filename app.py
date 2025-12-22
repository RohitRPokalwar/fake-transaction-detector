from flask import Flask, request, jsonify, render_template, Response
import pandas as pd
import logging
import traceback
import uuid
import io
import json
import csv
from collections import defaultdict
from utils.preprocess import Preprocessor
from utils.ddie import DDIE
from utils.ssg import SSG
from utils.uaic import UAIC
from utils.scoring import HybridScorer
from utils.explain import Explain
from utils.graph_anomaly import GraphAnomalyDetector
from utils.profiling import UserProfiler
from utils.report_generator import ReportGenerator
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

uploaded_files = {}
processed_data_cache = {}

def get_or_process_data(file_id):
    """Helper to get processed dataframe, either from cache or by processing."""
    if file_id in processed_data_cache:
        return processed_data_cache[file_id]

    if file_id not in uploaded_files:
        raise ValueError("File not found")

    file_content = uploaded_files[file_id]
    df = pd.read_csv(io.StringIO(file_content))
    
    # Preprocess
    preprocessor = Preprocessor()
    df = preprocessor.clean_data(df)
    
    # Apply DDIE rules
    ddie = DDIE()
    rule_results = ddie.apply_rules(df)
    
    # ML anomaly detection
    uaic = UAIC()
    if len(df) >= 20:
        uaic.fit(df)
        ml_scores = [uaic.predict_single(row.to_dict(), df) for _, row in df.iterrows()]
    else:
        ml_scores = [0.0] * len(df)
        
    # Graph-based anomaly detection
    graph_detector = GraphAnomalyDetector()
    graph_scores = graph_detector.detect_anomalies(df)
    
    # Hybrid scoring
    scorer = HybridScorer()
    rule_scores = rule_results['rule_score'].tolist()
    scorer.auto_tune_threshold(rule_scores, ml_scores, graph_scores)
    
    final_scores = []
    is_anomalous_list = []
    explanations = []
    
    explainer = Explain()
    if len(df) >= 20 and uaic.model is not None:
        features = uaic._create_features(df)
        feature_names = ['transaction_amount', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'user_transaction_frequency']
        explainer.setup_explainer(uaic.model, features, feature_names)

    for i, row in df.iterrows():
        rule_score = rule_results.iloc[i]['rule_score']
        reasons = rule_results.iloc[i]['reasons']
        ml_score = ml_scores[i]
        
        final_score = scorer.compute_hybrid_score(rule_score, ml_score)
        is_anomalous = bool(scorer.is_anomalous(final_score))
        
        row_features = None
        if len(df) >= 20 and uaic.model is not None:
            row_features = uaic._create_features_single(row.to_dict(), df)
        
        explanation = explainer.generate_explanation(reasons, ml_score, row_features, uaic.model if len(df) >= 20 else None, is_anomalous)
        
        final_scores.append(final_score)
        is_anomalous_list.append(is_anomalous)
        explanations.append(explanation)
        
    df['final_score'] = final_scores
    df['is_anomalous'] = is_anomalous_list
    df['explanation'] = explanations
    
    processed_data_cache[file_id] = df
    return df

@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload CSV file and return file_id for analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV'}), 400

        # Generate unique file ID
        file_id = str(uuid.uuid4())

        # Read file content and store
        file_content = file.read().decode('utf-8')
        uploaded_files[file_id] = file_content

        logger.info(f"File uploaded with ID: {file_id}")
        return jsonify({'file_id': file_id}), 200

    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')

@app.route('/live')
def live_analyzer():
    return render_template('phonepe.html')

@app.route('/architecture')
def architecture():
    """Serve the system architecture visualization."""
    return render_template('architecture.html')

@app.route('/api/analyze/<file_id>', methods=['GET'])
def analyze(file_id):
    """Analyze uploaded CSV for fake transactions in streaming mode."""
    def generate():
        try:
            if file_id not in uploaded_files:
                yield f"data: {json.dumps({'error': 'File not found'})}\n\n"
                return

            file_content = uploaded_files[file_id]

            # Stream CSV processing
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = []
            headers = None

            # First pass: collect all rows for preprocessing and ML training
            for row in csv_reader:
                if headers is None:
                    headers = list(row.keys())
                rows.append(row)

            if not rows:
                yield f"data: {json.dumps({'error': 'Empty CSV file'})}\n\n"
                return

            total_transactions = len(rows)
            logger.info(f"Loaded CSV with {total_transactions} rows")

            # Convert to DataFrame for preprocessing
            df = pd.DataFrame(rows)
            logger.info("Converted to DataFrame")

            # Preprocess
            preprocessor = Preprocessor()
            df = preprocessor.clean_data(df)
            logger.info("Preprocessing completed")

            # Apply DDIE rules
            ddie = DDIE()
            rule_results = ddie.apply_rules(df)
            logger.info("DDIE rules applied")

            # Compute stats
            ssg = SSG()
            stats = ssg.compute_global_stats(df)
            logger.info("Statistical signatures computed")

            # ML anomaly detection - fit on full data first
            uaic = UAIC()
            if total_transactions >= 20:  # Minimum for ML
                uaic.fit(df)
                logger.info("ML model fitted on full data")
            else:
                logger.warning("Dataset too small for ML, using rule-only scoring")

            # Graph-based anomaly detection
            graph_detector = GraphAnomalyDetector()
            graph_scores, graph_reasons_list = graph_detector.detect_anomalies(df)
            logger.info("Graph-based anomaly detection completed")

            # Hybrid scoring setup with auto-tuning
            scorer = HybridScorer()
            rule_scores = rule_results['rule_score'].tolist()
            ml_scores = [uaic.predict_single(row, df) if total_transactions >= 20 else 0.0 for row in rows]
            scorer.auto_tune_threshold(rule_scores, ml_scores, graph_scores)
            logger.info(f"Auto-tuned threshold: {scorer.threshold}")

            # Set up explainers with SHAP/LIME if ML model available
            explainer = Explain()
            if total_transactions >= 20 and uaic.model is not None:
                features = uaic._create_features(df)
                feature_names = ['transaction_amount', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'user_transaction_frequency']
                explainer.setup_explainer(uaic.model, features, feature_names)
                logger.info("SHAP/LIME explainers set up")

            # Stream results one by one
            anomalous_count = 0
            final_scores = []
            is_anomalous_list = []
            explanations = []

            for i, row_dict in enumerate(rows):
                # Get rule-based score for this row
                rule_score = rule_results.iloc[i]['rule_score']
                reasons = rule_results.iloc[i]['reasons']

                # Get ML score for this row
                if total_transactions >= 20:
                    ml_score = uaic.predict_single(row_dict, df)
                else:
                    ml_score = 0.0

                # Get Graph score
                graph_score = graph_scores[i] if i < len(graph_scores) else 0.0

                # Compute hybrid score
                final_score = scorer.compute_hybrid_score(rule_score, ml_score, graph_score)
                is_anomalous = bool(scorer.is_anomalous(final_score))

                # Generate explanation with SHAP/LIME if available
                row_features = None
                if total_transactions >= 20 and uaic.model is not None:
                    row_features = uaic._create_features_single(row_dict, df)
                explanation = explainer.generate_explanation(reasons, ml_score, row_features, uaic.model if total_transactions >= 20 else None, is_anomalous, row=row_dict, global_stats=stats, graph_reasons=graph_reasons_list[i] if i < len(graph_reasons_list) else None)

                # Prepare row data
                row = row_dict.copy()
                row['final_score'] = float(final_score)
                row['is_anomalous'] = is_anomalous
                row['explanation'] = explanation
                if row['is_anomalous']:
                    anomalous_count += 1
                
                final_scores.append(final_score)
                is_anomalous_list.append(is_anomalous)
                explanations.append(explanation)

                # Inject anomaly stats into the final stats object
                if i == total_transactions - 1 and stats is not None:
                    stats['total_transactions'] = total_transactions
                    stats['anomalous_count'] = anomalous_count
                    stats['anomaly_rate'] = f"{(anomalous_count / total_transactions * 100):.1f}%"

                result = {
                    'index': i,
                    'row': row,
                    'total_transactions': total_transactions,
                    'anomalous_count': anomalous_count,
                    'stats': stats if i == total_transactions - 1 else None  # Send stats only at the end
                }
                yield f"data: {json.dumps(result)}\n\n"

            # Cache processed data
            df['final_score'] = final_scores
            df['is_anomalous'] = is_anomalous_list
            df['explanation'] = explanations
            processed_data_cache[file_id] = df
            logger.info(f"Cached processed data for file {file_id}")

            logger.info(f"Analysis completed: {anomalous_count} anomalies detected")

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': 'Internal server error', 'details': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})

@app.route('/api/user_profile/<file_id>/<user_id>', methods=['GET'])
def user_profile(file_id, user_id):
    try:
        df = get_or_process_data(file_id)
        profiler = UserProfiler()
        profile = profiler.get_profile(df, user_id)
        
        if profile is None:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(profile)
    except Exception as e:
        logger.error(f"Error generating user profile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_report/<file_id>', methods=['GET'])
def generate_report(file_id):
    try:
        df = get_or_process_data(file_id)
        
        # Calculate stats
        ssg = SSG()
        stats = ssg.compute_global_stats(df)
        
        generator = ReportGenerator()
        
        # Create temporary file for PDF
        report_filename = f"intelligence_report_{file_id}.pdf"
        report_path = os.path.join('static', report_filename)
        
        # Ensure static dir exists
        os.makedirs('static', exist_ok=True)
        
        generator.generate_report(df, stats, report_path)
        
        return jsonify({'report_url': f"/static/{report_filename}"})
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# --- JUDGE MODE IMPLEMENTATION ---
global_model_context = {}

def init_global_model():
    """Initialize a global model using sample data for immediate judging."""
    try:
        sample_path = 'new_sample_transactions.csv'
        if not os.path.exists(sample_path):
            sample_path = os.path.join('sample_data', 'new_sample_transactions.csv')
            
        if os.path.exists(sample_path):
            logger.info("Initializing global model from sample data...")
            df = pd.read_csv(sample_path)
            
            # Preprocess
            preprocessor = Preprocessor()
            df = preprocessor.clean_data(df)
            
            # Fit UAIC
            uaic = UAIC()
            if len(df) >= 20:
                uaic.fit(df)
            
            # Run initial analysis to get score distributions for auto-tuning
            ddie = DDIE()
            rule_results = ddie.apply_rules(df)
            
            ml_scores = [uaic.predict_single(row.to_dict(), df) for _, row in df.iterrows()] if uaic.model else [0.0]*len(df)
            
            graph_detector = GraphAnomalyDetector()
            graph_scores, _ = graph_detector.detect_anomalies(df)
            
            scorer = HybridScorer()
            scorer.auto_tune_threshold(rule_results['rule_score'].tolist(), ml_scores, graph_scores)
            
            global_model_context['df'] = df
            global_model_context['uaic'] = uaic
            global_model_context['scorer'] = scorer
            global_model_context['explainer'] = Explain()
            
            if uaic.model is not None:
                features = uaic._create_features(df)
                feature_names = ['transaction_amount', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'user_transaction_frequency']
                global_model_context['explainer'].setup_explainer(uaic.model, features, feature_names)
                
            logger.info("Global model initialized successfully.")
        else:
            logger.warning("Sample data not found. Judge mode might be limited.")
    except Exception as e:
        logger.error(f"Failed to initialize global model: {e}")
        logger.error(traceback.format_exc())

# Initialize on startup
init_global_model()

@app.route('/api/judge', methods=['POST'])
def judge_transaction():
    """Judge a single manually entered transaction."""
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        location = data.get('location', 'Unknown')
        user_id = data.get('user_id', 'JUDGE_USER')
        txn_id = data.get('transaction_id') or f"JUDGE-{uuid.uuid4().hex[:8]}"
        timestamp = data.get('timestamp')
        
        # Default timestamp if not provided
        from datetime import datetime
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Create a full transaction record
        row_dict = {
            'transaction_id': txn_id,
            'user_id': user_id,
            'amount': amount,
            'location': location,
            'timestamp': timestamp
        }
        
        # Convert to DataFrame row for processing (some utils expect DF context)
        # We use the global DF as context
        context_df = global_model_context.get('df', pd.DataFrame([row_dict]))
        
        # 1. Rule Check
        single_df = pd.DataFrame([row_dict])
        
        preprocessor = Preprocessor()
        single_df = preprocessor.clean_data(single_df)
        
        ddie = DDIE()
        rule_results = ddie.apply_rules(single_df)
        rule_score = rule_results.iloc[0]['rule_score']
        reasons = rule_results.iloc[0]['reasons'] # List of strings
        
        # 2. ML Score
        uaic = global_model_context.get('uaic')
        ml_score = 0.0
        if uaic and uaic.model:
            ml_score = uaic.predict_single(row_dict, context_df)
            
        # 3. Hybrid Score
        scorer = global_model_context.get('scorer')
        if not scorer:
            scorer = HybridScorer() # Fallback
            
        final_score = scorer.compute_hybrid_score(rule_score, ml_score)
        is_anomalous = bool(scorer.is_anomalous(final_score))
        
        # 4. Explanation Generation (Structured HTML)
        # 4. Explanation Generation
        explainer = global_model_context.get('explainer')
        if not explainer:
            explainer = Explain()
            
        row_features = None
        if uaic and uaic.model:
             row_features = uaic._create_features_single(row_dict, context_df)
             
        # Compute context stats for comparison
        ssg = SSG()
        context_stats = ssg.compute_global_stats(context_df)
        
        explanation = explainer.generate_explanation(reasons, ml_score, row_features, uaic.model if uaic else None, is_anomalous, row=row_dict, global_stats=context_stats)

        return jsonify({
            'is_anomalous': is_anomalous,
            'final_score': float(final_score),
            'explanation': explanation,
            'details': {
                'rule_score': float(rule_score),
                'ml_score': float(ml_score),
                'graph_score': 0.0,
                'weights': {
                    'rule': scorer.rule_weight,
                    'ml': scorer.ml_weight,
                    'graph': scorer.graph_weight
                },
                'threshold': scorer.threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Judge error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
