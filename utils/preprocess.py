import pandas as pd
from dateutil import parser

class Preprocessor:
    """
    Data preprocessing utilities for transaction data.
    """

    def __init__(self):
        self.required_columns = ['transaction_id', 'user_id', 'amount', 'timestamp', 'location', 'recipient_id']
        self.aliases = {
            'transaction_id': ['txn_id', 'trans_id', 'id', 'transaction'],
            'user_id': ['sender_id', 'sender', 'customer_id', 'user', 'sender name'],
            'amount': ['amt', 'value', 'price', 'transaction_amount', 'transaction amount'],
            'timestamp': ['date', 'time', 'trans_date', 'txn_date', 'datetime'],
            'location': ['city', 'geo', 'coordinates', 'address', 'place'],
            'recipient_id': ['receiver_id', 'to_id', 'recipient', 'receiver', 'receiver name']
        }

    def _map_columns(self, df):
        """Map alternative column names to required column names."""
        current_cols = [c.lower() for c in df.columns]
        mapping = {}
        
        for required_col, alt_names in self.aliases.items():
            # If standard name is already present (case-insensitive), skip mapping
            if required_col in current_cols:
                continue
            
            # Look for aliases
            for alias in alt_names:
                if alias in current_cols:
                    # Find the original case sensitive column name
                    original_name = df.columns[current_cols.index(alias)]
                    mapping[original_name] = required_col
                    break
        
        if mapping:
            df = df.rename(columns=mapping)
        return df

    def clean_data(self, df):
        """
        Clean and preprocess the dataframe.
        """
        # Map aliases first
        df = self._map_columns(df)

        # Convert column names to lowercase for consistency
        df.columns = df.columns.str.lower()

        # Check for required columns
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean amount column
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        # Parse timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(self._parse_timestamp)

        # Fill missing values appropriately
        df = df.fillna({
            'transaction_id': 'unknown',
            'user_id': 'unknown',
            'amount': 0.0,
            'timestamp': pd.Timestamp.now(),
            'location': 'unknown'
        })

        return df

    def _parse_timestamp(self, ts):
        """
        Parse timestamp with error handling.
        """
        if pd.isna(ts):
            return pd.Timestamp.now()
        try:
            return parser.parse(str(ts))
        except:
            return pd.Timestamp.now()
