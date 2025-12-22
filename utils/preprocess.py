import pandas as pd
from dateutil import parser

class Preprocessor:
    """
    Data preprocessing utilities for transaction data.
    """

    def __init__(self):
        self.required_columns = ['transaction_id', 'user_id', 'amount', 'timestamp', 'location', 'recipient_id']

    def clean_data(self, df):
        """
        Clean and preprocess the dataframe.
        """
        # Convert column names to lowercase
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
