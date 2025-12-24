import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_demo_data(num_records=1000):
    locations = ["Mumbai", "London", "New York", "Tokyo", "Dubai", "Lagos", "Singapore", "Paris", "Berlin", "Sydney"]
    users = [f"user_{i}" for i in range(1, 101)]  # 100 unique users
    
    data = []
    base_time = datetime.now() - timedelta(days=2)
    
    # 1. Generate mostly normal transactions
    for i in range(num_records - 50):  # Leave room for 50 intentional anomalies
        txn_id = f"TXN_{10000 + i}"
        sender = random.choice(users)
        receiver = random.choice(users)
        while receiver == sender:
            receiver = random.choice(users)
            
        amount = round(random.uniform(100, 5000), 2)
        # Normal time: between 9 AM and 10 PM
        random_hour = random.randint(9, 21)
        timestamp = (base_time + timedelta(hours=random_hour, minutes=random.randint(0, 59))).strftime("%Y-%m-%dT%H:%M:%SZ")
        location = random.choice(locations)
        
        data.append([txn_id, sender, receiver, amount, timestamp, location])

    # 2. Add Rule Violations (Deterministic)
    # A. Zero/Negative Amount
    data.append(["TXN_ERR_01", "user_1", "user_2", 0.00, datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "Mumbai"])
    data.append(["TXN_ERR_02", "user_3", "user_4", -50.00, datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "New York"])
    
    # B. Future Timestamp
    future_time = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    data.append(["TXN_ERR_03", "user_5", "user_6", 500.00, future_time, "London"])
    
    # C. Duplicate ID
    data.append(["TXN_10000", "user_7", "user_8", 120.00, datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "Tokyo"])

    # 3. Add ML Anomalies (Statistical Outliers)
    # A. Massive Amount
    data.append(["TXN_ML_01", "user_10", "user_11", 999999.99, datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "Dubai"])
    
    # B. Unusual Time (Late Night)
    late_night = (base_time + timedelta(hours=3, minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
    data.append(["TXN_ML_02", "user_12", "user_13", 1500.00, late_night, "Paris"])

    # 4. Add Graph Anomalies (Money Laundering)
    # A. Ping-Pong (A -> B -> A)
    data.append(["TXN_GPA_01", "user_20", "user_21", 5000.00, (base_time + timedelta(hours=10)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Mumbai"])
    data.append(["TXN_GPA_02", "user_21", "user_20", 4950.00, (base_time + timedelta(hours=11)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Mumbai"])
    
    # B. The Classic Loop (A -> B -> C -> A)
    data.append(["TXN_GPA_03", "user_26", "user_27", 10000.00, (base_time + timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Singapore"])
    data.append(["TXN_GPA_04", "user_27", "user_28", 10000.00, (base_time + timedelta(hours=13)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Singapore"])
    data.append(["TXN_GPA_05", "user_28", "user_26", 10000.00, (base_time + timedelta(hours=14)).strftime("%Y-%m-%dT%H:%M:%SZ"), "Singapore"])

    # Shuffle for realism
    random.shuffle(data)
    
    df = pd.DataFrame(data, columns=["transaction_id", "user_id", "recipient_id", "amount", "timestamp", "location"])
    df.to_csv("Final_Presentation_Demo_1000.csv", index=False)
    print(f"Successfully generated Final_Presentation_Demo_1000.csv with {len(df)} records.")

if __name__ == "__main__":
    generate_demo_data()
