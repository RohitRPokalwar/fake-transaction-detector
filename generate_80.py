import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_fake_transactions(
    num_transactions=200,
    num_users=20,
    include_location=True,
    seed=42
):
    random.seed(seed)
    np.random.seed(seed)

    user_ids = [f"User_{i}" for i in range(1, num_users + 1)]
    locations = ["Mumbai", "Pune", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata"]

    rows = []

    # Base start time
    base_time = datetime.now() - timedelta(days=30)
    
    # 1. Normal Transactions
    for i in range(num_transactions):
        sender = random.choice(user_ids)
        recipient = random.choice([u for u in user_ids if u != sender]) # different from sender
        
        # Random small/medium amount
        amount = round(np.random.normal(loc=2000, scale=1000), 2)
        if amount < 100: amount = 100

        # Random time increments
        ts = base_time + timedelta(minutes=random.randint(0, 60 * 24 * 30))

        row = {
            "transaction_id": f"TXN-{1000+i}",
            "user_id": sender,
            "recipient_id": recipient,
            "amount": amount,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "location": random.choice(locations)
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------
    # INJECT ANOMALIES
    # ------------------------------------------------------------
    
    anomalies = []
    
    # 1. Money Laundering Loop (Graph Anomaly) -> A->B->C->A
    loop_time = datetime.now()
    loop_ids = ["User_Tax_Haven_1", "User_Mule_2", "User_Shell_3"]
    anomalies.append({
        "transaction_id": "LAUNDRY-001", "user_id": loop_ids[0], "recipient_id": loop_ids[1],
        "amount": 500000, "timestamp": loop_time.strftime("%Y-%m-%d %H:%M:%S"), "location": "Mumbai"
    })
    anomalies.append({
        "transaction_id": "LAUNDRY-002", "user_id": loop_ids[1], "recipient_id": loop_ids[2],
        "amount": 495000, "timestamp": (loop_time + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), "location": "Delhi"
    })
    anomalies.append({
        "transaction_id": "LAUNDRY-003", "user_id": loop_ids[2], "recipient_id": loop_ids[0],
        "amount": 490000, "timestamp": (loop_time + timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"), "location": "Bangalore"
    })

    # 2. Duplicate Transaction
    dup_row = df.iloc[5].to_dict()
    dup_row["transaction_id"] = "TXN-DUPLICATE" # Make ID same? Or effectively same content? 
    # Usually duplicate detection is by ID. Let's use existing ID.
    real_dup = df.iloc[5].to_dict().copy()
    anomalies.append(real_dup) # Exact duplicate of row 5

    # 3. Future Timestamp
    anomalies.append({
        "transaction_id": "FUTURE-001", "user_id": "User_TimeTravel", "recipient_id": "User_2",
        "amount": 5000, "timestamp": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Pune"
    })

    # 4. Negative Amount
    anomalies.append({
        "transaction_id": "NEG-001", "user_id": "User_Hacker", "recipient_id": "User_3",
        "amount": -50000, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Mumbai"
    })

    # 5. Zero Amount
    anomalies.append({
        "transaction_id": "ZERO-001", "user_id": "User_Tester", "recipient_id": "User_4",
        "amount": 0, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Delhi"
    })
    
    # 6. High Velocity Burst (Same user, many txns in 1 sec)
    burst_user = "User_Burst"
    burst_time = datetime.now()
    for k in range(5):
        anomalies.append({
            "transaction_id": f"BURST-{k}", "user_id": burst_user, "recipient_id": "User_victim",
            "amount": 100, "timestamp": burst_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Hyderabad"
        })

    # Append anomalies
    df_anomalies = pd.DataFrame(anomalies)
    final_df = pd.concat([df, df_anomalies], ignore_index=True)

    return final_df

# Generate and save
df = generate_fake_transactions(100)
output_file = "new_sample_transactions.csv"
df.to_csv(output_file, index=False)
# df.to_csv("transactions_80.csv", index=False) # Skip this to avoid more locks if any

print(f"CSV generated: {output_file} with {len(df)} rows")
print(df.tail(10))
