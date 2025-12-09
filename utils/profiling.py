import pandas as pd
import numpy as np

class UserProfiler:
    def __init__(self):
        pass

    def get_profile(self, df, user_id):
        """
        Generates a risk profile for a specific user.
        """
        # Ensure user_id is string for comparison
        user_id = str(user_id)
        df['user_id'] = df['user_id'].astype(str)
        
        user_txns = df[df['user_id'] == user_id].copy()
        
        if user_txns.empty:
            return None

        total_volume = float(user_txns['amount'].sum())
        txn_count = len(user_txns)
        
        # Calculate risk score (average of final_score if available, else 0)
        # Assuming 'final_score' is present in the df passed from app.py
        if 'final_score' in user_txns.columns:
            risk_score = float(user_txns['final_score'].mean())
        else:
            risk_score = 0.0

        # Identify suspicious activity
        # Assuming 'is_anomalous' is present
        if 'is_anomalous' in user_txns.columns:
            suspicious_txns = user_txns[user_txns['is_anomalous'] == True]
            suspicious_count = len(suspicious_txns)
            history = suspicious_txns[['transaction_id', 'amount', 'timestamp', 'explanation']].to_dict('records')
        else:
            suspicious_count = 0
            history = []

        return {
            'user_id': user_id,
            'risk_score': risk_score,
            'total_volume': total_volume,
            'transaction_count': txn_count,
            'suspicious_count': suspicious_count,
            'history': history
        }
