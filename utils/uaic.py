import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class UAIC:
    """
    Unsupervised Anomaly Isolation Core (UAIC)
    Uses Isolation Forest for anomaly detection.
    """

    def __init__(self, contamination=0.1, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()

    def fit_predict(self, df):
        """
        Fit the model and return anomaly scores.
        """
        if len(df) < 20:
            return [0.0] * len(df)

        # Feature engineering
        features = self._create_features(df)

        # Scale features
        features_scaled = self.scaler.fit_transform(features)

        # Fit Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )

        # Get anomaly scores (-1 for outliers, 1 for inliers)
        scores = self.model.fit_predict(features_scaled)

        # Convert to 0-1 scale (higher = more anomalous)
        anomaly_scores = (scores == -1).astype(float)

        return anomaly_scores.tolist()

    def fit(self, df):
        """
        Fit the model on the full dataset.
        """
        if len(df) < 20:
            return

        # Feature engineering
        features = self._create_features(df)

        # Scale features
        features_scaled = self.scaler.fit_transform(features)

        # Fit Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )

        self.model.fit(features_scaled)

    def predict_single(self, row_dict, df_context=None):
        """
        Predict anomaly score for a single row.
        """
        if self.model is None:
            return 0.0

        # Create features for single row
        features = self._create_features_single(row_dict, df_context)

        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Get anomaly score
        score = self.model.predict(features_scaled)[0]

        # Convert to 0-1 scale (higher = more anomalous)
        anomaly_score = 1.0 if score == -1 else 0.0

        return anomaly_score

    def _create_features(self, df):
        """
        Create features for ML model.
        """
        features = []

        # Amount features
        if 'amount' in df.columns:
            amounts = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            features.append(amounts.values.reshape(-1, 1))

        # Time features
        if 'timestamp' in df.columns:
            # Parse timestamps and fill errors with current time instead of dropping
            timestamps = pd.to_datetime(df['timestamp'], errors='coerce')
            # If all are NaT, then use current time for all
            if timestamps.isna().all():
                 timestamps = pd.Series([pd.Timestamp.now()] * len(df))
            else:
                 timestamps = timestamps.fillna(pd.Timestamp.now())
            
            hours = timestamps.dt.hour.values
            # Sin/cos encoding for cyclical time
            hour_sin = np.sin(2 * np.pi * hours / 24)
            hour_cos = np.cos(2 * np.pi * hours / 24)
            features.append(hour_sin.reshape(-1, 1))
            features.append(hour_cos.reshape(-1, 1))

            day_of_week = timestamps.dt.dayofweek.values
            dow_sin = np.sin(2 * np.pi * day_of_week / 7)
            dow_cos = np.cos(2 * np.pi * day_of_week / 7)
            features.append(dow_sin.reshape(-1, 1))
            features.append(dow_cos.reshape(-1, 1))

        # User activity features
        if 'user_id' in df.columns:
            user_counts = df['user_id'].value_counts()
            user_freq = df['user_id'].map(user_counts).fillna(0)
            features.append(user_freq.values.reshape(-1, 1))

        # Concatenate all features
        if features:
            return np.concatenate(features, axis=1)
        else:
            return np.zeros((len(df), 1))

    def _create_features_single(self, row_dict, df_context=None):
        """
        Create features for a single row.
        """
        features = []

        # Amount features
        if 'amount' in row_dict:
            try:
                amount = float(row_dict['amount'])
                features.append([amount])
            except (ValueError, TypeError):
                features.append([0.0])

        # Time features
        if 'timestamp' in row_dict:
            try:
                timestamp = pd.to_datetime(row_dict['timestamp'])
                hour = timestamp.hour
                # Sin/cos encoding for cyclical time
                hour_sin = np.sin(2 * np.pi * hour / 24)
                hour_cos = np.cos(2 * np.pi * hour / 24)
                features.append([hour_sin])
                features.append([hour_cos])

                day_of_week = timestamp.dayofweek
                dow_sin = np.sin(2 * np.pi * day_of_week / 7)
                dow_cos = np.cos(2 * np.pi * day_of_week / 7)
                features.append([dow_sin])
                features.append([dow_cos])
            except (ValueError, TypeError):
                # Fallback if no valid timestamp
                features.extend([[0.0], [0.0], [0.0], [0.0]])

        # User activity features
        if 'user_id' in row_dict and df_context is not None:
            user_counts = df_context['user_id'].value_counts()
            user_freq = user_counts.get(row_dict['user_id'], 0)
            features.append([user_freq])
        elif 'user_id' in row_dict:
            # If no context, use 1 as default frequency
            features.append([1.0])

        # Concatenate all features
        if features:
            return np.array(features).flatten()
        else:
            return np.array([0.0])
