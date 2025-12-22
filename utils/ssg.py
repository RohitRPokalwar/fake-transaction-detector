import pandas as pd
import numpy as np

class SSG:
    """
    Statistical Signature Generator (SSG)
    Computes global and per-user transaction patterns.
    """

    def __init__(self):
        pass

    def compute_global_stats(self, df):
        """
        Compute global statistical signatures.
        """
        stats = {}

        if 'amount' in df.columns:
            amounts = pd.to_numeric(df['amount'], errors='coerce').dropna()
            if len(amounts) > 0:
                mean_val = amounts.mean()
                std_val = amounts.std()
                median_val = amounts.median()
                mad_val = (amounts - amounts.median()).abs().mean()
                q1_val = amounts.quantile(0.25)
                q3_val = amounts.quantile(0.75)
                iqr_val = q3_val - q1_val
                min_val = amounts.min()
                max_val = amounts.max()

                stats['mean_amount'] = float(mean_val) if not pd.isna(mean_val) else 0.0
                stats['std_amount'] = float(std_val) if not pd.isna(std_val) else 0.0
                stats['median_amount'] = float(median_val) if not pd.isna(median_val) else 0.0
                stats['mad_amount'] = float(mad_val) if not pd.isna(mad_val) else 0.0
                stats['q1_amount'] = float(q1_val) if not pd.isna(q1_val) else 0.0
                stats['q3_amount'] = float(q3_val) if not pd.isna(q3_val) else 0.0
                stats['iqr_amount'] = float(iqr_val) if not pd.isna(iqr_val) else 0.0
                stats['min_amount'] = float(min_val) if not pd.isna(min_val) else 0.0
                stats['max_amount'] = float(max_val) if not pd.isna(max_val) else 0.0

        # Transaction velocity (transactions per hour)
        if 'timestamp' in df.columns:
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], errors='coerce')
            df_copy = df_copy.dropna(subset=['timestamp'])
            if len(df_copy) > 0:
                time_range_hours = (df_copy['timestamp'].max() - df_copy['timestamp'].min()).total_seconds() / 3600
                if time_range_hours > 0:
                    velocity = len(df_copy) / time_range_hours
                    stats['transaction_velocity'] = float(velocity) if not pd.isna(velocity) else 0.0

        # User activity patterns
        if 'user_id' in df.columns:
            user_counts = df['user_id'].value_counts()
            unique_users = len(user_counts)
            avg_txns = user_counts.mean()
            max_txns = user_counts.max()

            stats['unique_users'] = int(unique_users) if not pd.isna(unique_users) else 0
            stats['avg_transactions_per_user'] = float(avg_txns) if not pd.isna(avg_txns) else 0.0
            stats['max_transactions_per_user'] = int(max_txns) if not pd.isna(max_txns) else 0
            stats['most_active_user_id'] = str(user_counts.idxmax()) if not user_counts.empty else "N/A"

        return stats

    def compute_user_stats(self, df):
        """
        Compute per-user statistical signatures.
        """
        user_stats = {}

        if 'user_id' in df.columns and 'amount' in df.columns:
            for user_id, group in df.groupby('user_id'):
                amounts = pd.to_numeric(group['amount'], errors='coerce').dropna()
                if len(amounts) > 0:
                    user_stats[user_id] = {
                        'mean_amount': amounts.mean(),
                        'std_amount': amounts.std(),
                        'transaction_count': len(amounts),
                        'total_amount': amounts.sum()
                    }

        return user_stats
