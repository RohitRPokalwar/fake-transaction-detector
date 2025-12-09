import pandas as pd
from dateutil import parser
import numpy as np

class DDIE:
    """
    Deterministic Data Integrity Engine (DDIE)
    Performs strict validation using rules for obvious errors.
    """

    def __init__(self):
        self.rules = {
            'duplicate_detection': self._check_duplicates,
            'timestamp_violations': self._check_timestamps,
            'amount_anomalies': self._check_amounts,
            'missing_fields': self._check_missing_fields,
            'time_gap_anomalies': self._check_time_gaps,
            'location_conflicts': self._check_location_conflicts
        }

    def apply_rules(self, df):
        """
        Apply all rules to the dataframe and return rule scores and reasons.
        """
        results = []
        for idx, row in df.iterrows():
            rule_score = 0.0
            reasons = []

            for rule_name, rule_func in self.rules.items():
                score, reason = rule_func(row, df)
                rule_score += score
                if reason:
                    reasons.append(reason)

            # Normalize rule_score to 0-1
            rule_score = min(rule_score, 1.0)

            results.append({
                'index': idx,
                'rule_score': rule_score,
                'reasons': reasons
            })

        return pd.DataFrame(results)

    def _check_duplicates(self, row, df):
        """Check for duplicate transactions."""
        if 'transaction_id' in row and pd.notna(row['transaction_id']):
            duplicates = df[df['transaction_id'] == row['transaction_id']]
            if len(duplicates) > 1:
                return 0.5, "Duplicate transaction detected"
        return 0.0, None

    def _check_timestamps(self, row, df):
        """Check for impossible or future timestamps."""
        if 'timestamp' in row and pd.notna(row['timestamp']):
            try:
                ts = parser.parse(str(row['timestamp']))
                now = pd.Timestamp.now()
                if ts > now:
                    return 0.8, "Future timestamp detected"
            except:
                return 0.6, "Invalid timestamp format"
        return 0.0, None

    def _check_amounts(self, row, df):
        """Check for negative, zero, or extreme amounts."""
        if 'amount' in row and pd.notna(row['amount']):
            amount = float(row['amount'])
            if amount <= 0:
                return 0.9, "Negative or zero amount"
            if amount > 10000:  # Placeholder threshold
                return 0.7, "Extreme amount detected"
        return 0.0, None

    def _check_missing_fields(self, row, df):
        """Check for missing mandatory fields."""
        mandatory_fields = ['transaction_id', 'user_id', 'amount', 'timestamp']
        missing = [field for field in mandatory_fields if field not in row or pd.isna(row[field])]
        if missing:
            return 0.8, f"Missing mandatory fields: {', '.join(missing)}"
        return 0.0, None

    def _check_time_gaps(self, row, df):
        """Check for unrealistic time gaps between user transactions."""
        if 'user_id' in row and 'timestamp' in row and pd.notna(row['user_id']) and pd.notna(row['timestamp']):
            try:
                user_txns = df[df['user_id'] == row['user_id']].copy()
                user_txns['timestamp'] = pd.to_datetime(user_txns['timestamp'], errors='coerce')
                user_txns = user_txns.dropna(subset=['timestamp']).sort_values('timestamp')
                if len(user_txns) > 1:
                    times = user_txns['timestamp'].values
                    gaps = np.diff(times) / np.timedelta64(1, 's')
                    min_gap = gaps.min()
                    if min_gap < 5:
                        return 0.6, "Unrealistic time gap between transactions"
            except:
                pass
        return 0.0, None

    def _check_location_conflicts(self, row, df):
        """Check for same user in different locations within short time."""
        if 'user_id' in row and 'location' in row and 'timestamp' in row:
            try:
                user_txns = df[df['user_id'] == row['user_id']].copy()
                user_txns['timestamp'] = pd.to_datetime(user_txns['timestamp'], errors='coerce')
                user_txns = user_txns.dropna(subset=['timestamp', 'location']).sort_values('timestamp')
                if len(user_txns) > 1:
                    for i in range(1, len(user_txns)):
                        prev_loc = user_txns.iloc[i-1]['location']
                        curr_loc = user_txns.iloc[i]['location']
                        time_diff = (user_txns.iloc[i]['timestamp'] - user_txns.iloc[i-1]['timestamp']).total_seconds()
                        if prev_loc != curr_loc and time_diff < 300:
                            return 0.7, "Location conflict detected"
            except:
                pass
        return 0.0, None
