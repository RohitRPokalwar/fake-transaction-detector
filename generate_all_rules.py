import pandas as pd
from datetime import datetime, timedelta

def generate_comprehensive_test():
    # Base setup
    base_time = datetime.now()
    rows = []
    
    # 1. Background Noise (Normal Data - to establish baseline)
    # essential for ML to have something to compare against
    for i in range(1, 15):
        rows.append({
            "transaction_id": f"TXN-NORM-{i:03d}",
            "user_id": f"User_Normal_{i%5}", # Reusing 5 users
            "recipient_id": f"User_Shop_{i%3}",
            "amount": 1000 + (i * 10),
            "timestamp": (base_time - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Mumbai"
        })

    # ---------------------------------------------------------
    # RULE 1: DUPLICATE TRANSACTION
    # ---------------------------------------------------------
    # Original
    rows.append({
        "transaction_id": "TXN-DUP-ORIGIN",
        "user_id": "User_Dup",
        "recipient_id": "User_Shop_1",
        "amount": 5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Delhi"
    })
    # The Duplicate (Same ID)
    rows.append({
        "transaction_id": "TXN-DUP-ORIGIN", # Same ID
        "user_id": "User_Dup",
        "recipient_id": "User_Shop_1",
        "amount": 5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Delhi"
    })

    # ---------------------------------------------------------
    # RULE 2: TIMESTAMP VIOLATION (Future)
    # ---------------------------------------------------------
    rows.append({
        "transaction_id": "TXN-FUTURE",
        "user_id": "User_TimeTravel",
        "recipient_id": "User_Shop_2",
        "amount": 2500,
        "timestamp": (base_time + timedelta(days=3650)).strftime("%Y-%m-%d %H:%M:%S"), # 10 years later
        "location": "Pune"
    })

    # ---------------------------------------------------------
    # RULE 3: AMOUNT ANOMALY (Negative)
    # ---------------------------------------------------------
    rows.append({
        "transaction_id": "TXN-NEG",
        "user_id": "User_Hacker",
        "recipient_id": "User_Shop_3",
        "amount": -5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Bangalore"
    })

    # ---------------------------------------------------------
    # RULE 4: AMOUNT ANOMALY (Zero)
    # ---------------------------------------------------------
    rows.append({
        "transaction_id": "TXN-ZERO",
        "user_id": "User_Tester",
        "recipient_id": "User_Shop_3",
        "amount": 0,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Bangalore"
    })

    # ---------------------------------------------------------
    # RULE 5: TIME GAP ANOMALY (High Velocity)
    # ---------------------------------------------------------
    t_burst = base_time - timedelta(minutes=30)
    # Txn 1
    rows.append({
        "transaction_id": "TXN-BURST-1",
        "user_id": "User_Flash",
        "recipient_id": "User_Shop_4",
        "amount": 100,
        "timestamp": t_burst.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Hyderabad"
    })
    # Txn 2 (1 second later - impossible speed for manual txn)
    rows.append({
        "transaction_id": "TXN-BURST-2",
        "user_id": "User_Flash",
        "recipient_id": "User_Shop_4",
        "amount": 100,
        "timestamp": (t_burst + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Hyderabad"
    })

    # ---------------------------------------------------------
    # RULE 6: LOCATION CONFLICT (Impossible Travel)
    # ---------------------------------------------------------
    t_travel = base_time - timedelta(minutes=60)
    # Txn 1 in Mumbai
    rows.append({
        "transaction_id": "TXN-LOC-1",
        "user_id": "User_Teleport",
        "recipient_id": "User_Shop_5",
        "amount": 2000,
        "timestamp": t_travel.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Mumbai"
    })
    # Txn 2 in London (5 mins later)
    rows.append({
        "transaction_id": "TXN-LOC-2",
        "user_id": "User_Teleport",
        "recipient_id": "User_Shop_5",
        "amount": 2000,
        "timestamp": (t_travel + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "London"
    })

    # ---------------------------------------------------------
    # GRAPH RULE 1: MONEY LAUNDERING LOOP (A -> B -> C -> A)
    # ---------------------------------------------------------
    loop_t = base_time - timedelta(minutes=10)
    rows.append({
        "transaction_id": "TXN-LOOP-1",
        "user_id": "User_Laundromat_A",
        "recipient_id": "User_Laundromat_B",
        "amount": 50000,
        "timestamp": loop_t.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })
    rows.append({
        "transaction_id": "TXN-LOOP-2",
        "user_id": "User_Laundromat_B",
        "recipient_id": "User_Laundromat_C",
        "amount": 49000,
        "timestamp": (loop_t + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })
    rows.append({
        "transaction_id": "TXN-LOOP-3",
        "user_id": "User_Laundromat_C",
        "recipient_id": "User_Laundromat_A", # Completes the loop
        "amount": 48000,
        "timestamp": (loop_t + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })

    # ---------------------------------------------------------
    # GRAPH RULE 2: ISOLATION (Stranger Danger)
    # ---------------------------------------------------------
    # A high value anomaly between two completely new/isolated users
    rows.append({
        "transaction_id": "TXN-ISO",
        "user_id": "User_Ghost",
        "recipient_id": "User_Phantom",
        "amount": 80000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Kolkata"
    })

    # Create DataFrame and Save
    df = pd.DataFrame(rows)
    output_file = "all_rules_test_v2.csv"
    df.to_csv(output_file, index=False)
    print(f"File created: {output_file}")

if __name__ == "__main__":
    generate_comprehensive_test()
