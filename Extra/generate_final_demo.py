try:
    import pandas as pd
    from datetime import datetime, timedelta
except ImportError:
    print("Error: Pandas not installed. Please run: pip install pandas")
    print("If using a virtual environment, activate it first.")
    exit(1)

def generate_final_demo_file():
    # Base setup
    # Shift back 15 hours to avoid Timezone conflicts (Server UTC vs Local IST)
    base_time = datetime.now() - timedelta(hours=15)
    rows = []
    
    # ---------------------------------------------------------
    # 1. NORMAL TRANSACTIONS (Background Noise)
    # ---------------------------------------------------------
    # TXN-1001 to TXN-1100 (100 rows)
    locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata"]
    for i in range(1, 101):
        rows.append({
            "transaction_id": f"TXN-{1000+i}",
            "user_id": f"User_{i%20 + 1}",  # Reuse 20 users for normal traffic
            "recipient_id": f"User_{50 + (i%15)}", # Different recipients
            "amount": round(100 + ((i * 37) % 4900), 2),
            "timestamp": (base_time - timedelta(minutes=i*15)).strftime("%Y-%m-%d %H:%M:%S"),
            "location": locations[i % len(locations)]
        })

    # ---------------------------------------------------------
    # 2. ANOMALIES (One of Each Type - Numeric IDs)
    # ---------------------------------------------------------

    # A. DUPLICATE (Replay Attack)
    rows.append({
        "transaction_id": "TXN-2001",
        "user_id": "User_20",
        "recipient_id": "User_50",
        "amount": 5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Delhi"
    })
    rows.append({
        "transaction_id": "TXN-2001", # EXACT COPY
        "user_id": "User_20",
        "recipient_id": "User_50",
        "amount": 5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Delhi"
    })

    # B. FUTURE TIMESTAMP
    rows.append({
        "transaction_id": "TXN-2002",
        "user_id": "User_21",
        "recipient_id": "User_51",
        "amount": 2500,
        "timestamp": "2035-01-01 12:00:00", 
        "location": "Pune"
    })

    # C. NEGATIVE AMOUNT
    rows.append({
        "transaction_id": "TXN-2003",
        "user_id": "User_22",
        "recipient_id": "User_52",
        "amount": -5000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Bangalore"
    })

    # D. ZERO AMOUNT
    rows.append({
        "transaction_id": "TXN-2004",
        "user_id": "User_23",
        "recipient_id": "User_53",
        "amount": 0.0, # Float 0.0
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Bangalore"
    })

    # E. HIGH VELOCITY (BURST) -> 2 Transactions in 1 Second
    t_burst = base_time - timedelta(minutes=30)
    rows.append({
        "transaction_id": "TXN-2005",
        "user_id": "User_24",
        "recipient_id": "User_54",
        "amount": 100,
        "timestamp": t_burst.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Hyderabad"
    })
    rows.append({
        "transaction_id": "TXN-2006",
        "user_id": "User_24",
        "recipient_id": "User_54",
        "amount": 100,
        # 1 second difference
        "timestamp": (t_burst + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Hyderabad"
    })

    # F. IMPOSSIBLE TRAVEL (Mumbai -> London in 5 mins)
    t_travel = base_time - timedelta(minutes=60)
    rows.append({
        "transaction_id": "TXN-2007",
        "user_id": "User_25",
        "recipient_id": "User_55",
        "amount": 2000,
        "timestamp": t_travel.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Mumbai"
    })
    rows.append({
        "transaction_id": "TXN-2008",
        "user_id": "User_25",
        "recipient_id": "User_55",
        "amount": 2000,
        "timestamp": (t_travel + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "location": "London"
    })

    # G. MONEY LAUNDERING LOOP (A(User_26) -> B(User_27) -> C(User_28) -> A)
    rows.append({
        "transaction_id": "TXN-2009",
        "user_id": "User_26",
        "recipient_id": "User_27",
        "amount": 50000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })
    rows.append({
        "transaction_id": "TXN-2010",
        "user_id": "User_27",
        "recipient_id": "User_28",
        "amount": 49000,
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })
    rows.append({
        "transaction_id": "TXN-2011",
        "user_id": "User_28",
        "recipient_id": "User_26", # CLOSES LOOP
        "amount": 48500, 
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Chennai"
    })

    # Create DataFrame and Save
    df = pd.DataFrame(rows)
    output_file = "Final_Presentation_Demo.csv"
    df.to_csv(output_file, index=False)
    print(f"File created: {output_file}")
    
    # Calculate Expected Anomalies
    print("--------------------------------------------------")
    print("DATA GENERATION SUMMARY")
    print("--------------------------------------------------")
    print("Normal Transactions:      100 rows (TXN-1001 to TXN-1100)")
    print("Anomalous Transactions:   11 rows (TXN-2001 to TXN-2011)")
    print("Total Rows:               111")
    print("--------------------------------------------------")
    print("ANOMALY BREAKDOWN:")
    print("1. Duplicate: TXN-2001 (Appears twice)")
    print("2. Future:    TXN-2002")
    print("3. Negative:  TXN-2003")
    print("4. Zero Amt:  TXN-2004")
    print("5. Burst:     TXN-2005 & TXN-2006 (User_24)")
    print("6. Travel:    TXN-2007 & TXN-2008 (User_25)")
    print("7. Loop:      TXN-2009 -> TXN-2010 -> TXN-2011")
    print("--------------------------------------------------")

if __name__ == "__main__":
    generate_final_demo_file()
