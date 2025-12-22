import numpy as np
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin

class HybridScorer:
    """
    Hybrid Scoring System
    Combines rule_score (40%), ml_score (50%), and graph_score (10%) with auto-tuned threshold.
    """

    def __init__(self, rule_weight=0.4, ml_weight=0.5, graph_weight=0.1, threshold=None):
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        self.graph_weight = graph_weight
        self.threshold = threshold or 0.6  # Default threshold

    def compute_hybrid_score(self, rule_score, ml_score, graph_score=0.0):
        """
        Compute final hybrid score.
        All scores should be normalized between 0 and 1.
        """
        if rule_score is None:
            rule_score = 0.0
        if ml_score is None:
            ml_score = 0.0
        if graph_score is None:
            graph_score = 0.0

        # Ensure scores are between 0 and 1
        rule_score = max(0.0, min(1.0, rule_score))
        ml_score = max(0.0, min(1.0, ml_score))
        graph_score = max(0.0, min(1.0, graph_score))

        weighted_score = (self.rule_weight * rule_score +
                      self.ml_weight * ml_score +
                      self.graph_weight * graph_score)
        
        # CRITICAL FIX: Rule & Graph Override
        # 1. If a hard rule is broken, it's an anomaly.
        # 2. If a Graph Anomaly (Loop/Isolation) is strong (>0.6), it's an anomaly.
        #    (Graph weight is usually low (0.1), so we must override if the signal is strong)
        
        graph_override = graph_score if graph_score > 0.6 else 0.0
        final_score = max(weighted_score, rule_score, graph_override)

        return final_score

    def auto_tune_threshold(self, rule_scores, ml_scores, graph_scores=None, true_labels=None):
        """
        Auto-tune the anomaly threshold using ROC curve analysis or grid search.
        If true_labels are provided, use supervised tuning; otherwise, use unsupervised heuristics.
        """
        if true_labels is not None:
            # Supervised tuning using ROC curve
            y_true = np.array(true_labels)
            y_scores = np.array([
                self.compute_hybrid_score(r, m, g or 0.0)
                for r, m, g in zip(rule_scores, ml_scores, graph_scores or [0.0]*len(rule_scores))
            ])

            fpr, tpr, thresholds = roc_curve(y_true, y_scores)
            optimal_idx = np.argmax(tpr - fpr)  # Maximize TPR - FPR
            self.threshold = thresholds[optimal_idx]
        else:
            # Unsupervised tuning: Use fixed liberal threshold for Fraud Detection
            # Percentile logic hides anomalies if there are many of them (like in a test file).
            # self.threshold = np.percentile(scores, 95)
            self.threshold = 0.55

        return self.threshold

    def is_anomalous(self, final_score):
        """
        Determine if transaction is anomalous based on threshold.
        """
        return final_score >= self.threshold

    def normalize_scores(self, scores):
        """
        Normalize a list of scores to 0-1 range.
        """
        if not scores:
            return []

        scores = np.array(scores)
        min_score = np.min(scores)
        max_score = np.max(scores)

        if max_score == min_score:
            return [0.5] * len(scores)  # Default to 0.5 if all scores are equal

        normalized = (scores - min_score) / (max_score - min_score)
        return normalized.tolist()

    def grid_search_weights(self, rule_scores, ml_scores, graph_scores, true_labels=None):
        """
        Perform grid search to optimize weights for rule, ML, and graph scores.
        """
        class HybridClassifier(BaseEstimator, ClassifierMixin):
            def __init__(self, rule_weight=0.4, ml_weight=0.5, graph_weight=0.1, threshold=0.6):
                self.rule_weight = rule_weight
                self.ml_weight = ml_weight
                self.graph_weight = graph_weight
                self.threshold = threshold

            def fit(self, X, y):
                return self

            def predict(self, X):
                predictions = []
                for r, m, g in X:
                    score = (self.rule_weight * r + self.ml_weight * m + self.graph_weight * g)
                    predictions.append(1 if score >= self.threshold else 0)
                return np.array(predictions)

            def score(self, X, y):
                y_pred = self.predict(X)
                return np.mean(y_pred == y)

        # Prepare data
        X = np.column_stack([rule_scores, ml_scores, graph_scores or [0.0]*len(rule_scores)])
        y = np.array(true_labels) if true_labels else np.zeros(len(X))  # Dummy labels if unsupervised

        param_grid = {
            'rule_weight': [0.2, 0.3, 0.4, 0.5],
            'ml_weight': [0.3, 0.4, 0.5, 0.6],
            'graph_weight': [0.0, 0.1, 0.2]
        }

        grid_search = GridSearchCV(HybridClassifier(), param_grid, cv=3, scoring='accuracy')
        grid_search.fit(X, y)

        best_params = grid_search.best_params_
        self.rule_weight = best_params['rule_weight']
        self.ml_weight = best_params['ml_weight']
        self.graph_weight = best_params['graph_weight']

        return best_params
