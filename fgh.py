import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_fake_transactions(
    num_transactions=1000,
    num_users=50,
    include_location=True,
    seed=42
):
    random.seed(seed)
    np.random.seed(seed)

    user_ids = [f"user_{i}" for i in range(1, num_users + 1)]
    locations = ["Mumbai", "Pune", "Delhi", "Bangalore", "Hyderabad"]

    rows = []

    # Base start time
    base_time = datetime(2024, 1, 1, 0, 0, 0)

    for i in range(num_transactions):
        user = random.choice(user_ids)

        # Random small/medium amount
        amount = round(np.random.normal(loc=500, scale=200), 2)
        if amount < 10:
            amount = round(abs(amount), 2) + 10  # avoid too small values

        # Random time increments
        ts = base_time + timedelta(minutes=random.randint(0, 60 * 24 * 30))

        row = {
            "transaction_id": f"txn_{i+1}",
            "user_id": user,
            "amount": amount,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
        }

        if include_location:
            row["location"] = random.choice(locations)

        rows.append(row)

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------
    # ADD SOME FAKE / INVALID TRANSACTIONS (for testing your app)
    # ------------------------------------------------------------

    # 1. Duplicate transactions
    if num_transactions > 10:
        duplicate_row = df.iloc[10].copy()
        df.loc[num_transactions] = duplicate_row  # exact duplicate

    # 2. Future timestamp (fake)
    df.loc[num_transactions + 1] = df.iloc[20].copy()
    df.loc[num_transactions + 1, "timestamp"] = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

    # 3. Negative amount (invalid)
    df.loc[num_transactions + 2] = df.iloc[30].copy()
    df.loc[num_transactions + 2, "amount"] = -999

    # 4. Zero amount
    df.loc[num_transactions + 3] = df.iloc[50].copy()
    df.loc[num_transactions + 3, "amount"] = 0

    # 5. Extremely high amount
    df.loc[num_transactions + 4] = df.iloc[60].copy()
    df.loc[num_transactions + 4, "amount"] = 9999999

    # 6. Missing user_id
    df.loc[num_transactions + 5] = df.iloc[70].copy()
    df.loc[num_transactions + 5, "user_id"] = ""

    # ------------------------------------------------------------

    return df


# Generate and save
df = generate_fake_transactions(50)
df.to_csv("sample_transactions.csv", index=False)

print("CSV generated: sample_transactions.csv")
print(df.head())
