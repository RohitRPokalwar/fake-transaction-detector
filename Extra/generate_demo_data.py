import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

def generate_complex_dataset(num_rows=300):
    rows = []
    
    # Real-world User Personas
    indian_names = [
        "Amit Sharma", "Priya Patel", "Rahul Verma", "Sneha Rao", "Vikram Singh",
        "Ananya Iyer", "Arjun Reddy", "Kavita Nair", "Sanjay Gupta", "Deepa Mishra",
        "Rohan Malhotra", "Shalini Joshi", "Karthik Raja", "Meera Krishnan", "Aditya Das",
        "Tanvi Kulkarni", "Varun Bajaj", "Ishita Saxena", "Manish Pandey", "Pooja Hegde"
    ]
    
    merchants = [
        "Amazon India", "Flipkart", "Zomato", "Swiggy", "BigBasket", 
        "Reliance Digital", "Starbucks", "PVR Cinemas", "Uber", "Petrol Pump"
    ]

    locations = [
        "Mumbai, IN", "Delhi, IN", "Bangalore, IN", "Hyderabad, IN", 
        "Pune, IN", "Chennai, IN", "Kolkata, IN", "London, UK", "New York, US"
    ]

    start_time = datetime.now() - timedelta(days=2)

    # Helper for random ID
    def get_id(): return uuid.uuid4().hex.upper()[:12]

    # 1. Generate 280 Normal Transactions (The stable baseline)
    for i in range(282):
        t_id = f"TXN-{get_id()}"
        u_id = random.choice(indian_names)
        r_id = random.choice(merchants)
        amt = round(random.uniform(200, 8000), 2)
        loc = random.choice(locations[:6]) 
        ts = start_time + timedelta(minutes=random.randint(1, 2800))
        
        rows.append({
            'transaction_id': t_id,
            'user_id': u_id,
            'recipient_id': r_id,
            'amount': amt,
            'location': loc,
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S')
        })

    # 2. TELEPORTATION (2 pairs = 4 rows)
    travelers = ["Rajesh Kumar", "Sunita Patel"]
    for i in range(2):
        name = travelers[i]
        ts1 = start_time + timedelta(hours=random.randint(1, 40))
        ts2 = ts1 + timedelta(minutes=2)
        
        rows.append({
            'transaction_id': f"TXN-{get_id()}", 'user_id': name, 'recipient_id': "Airport Coffee",
            'amount': 450, 'location': "London, UK", 'timestamp': ts1.strftime('%Y-%m-%d %H:%M:%S')
        })
        rows.append({
            'transaction_id': f"TXN-{get_id()}", 'user_id': name, 'recipient_id': "Cab_Service",
            'amount': 1200, 'location': "Mumbai, IN", 'timestamp': ts2.strftime('%Y-%m-%d %H:%M:%S')
        })

    # 3. BOT BURST (1 burst of 3 = 3 rows)
    attacker = "Global_Automation_Bot"
    ts_base = start_time + timedelta(hours=24)
    for j in range(3):
        rows.append({
            'transaction_id': f"TXN-{get_id()}", 'user_id': attacker, 'recipient_id': "Digital_Gold",
            'amount': 49000, 'location': "Bangalore, IN", 'timestamp': (ts_base + timedelta(milliseconds=j*400)).strftime('%Y-%m-%d %H:%M:%S')
        })

    # 4. MONEY CIRCLE (1 loop of 3 = 3 rows)
    p1, p2, p3 = "Account_Alpha", "Account_Beta", "Account_Gamma"
    ts_base = start_time + timedelta(hours=10)
    
    rows.append({ 'transaction_id': f"TXN-{get_id()}", 'user_id': p1, 'recipient_id': p2, 'amount': 99000, 'location': "Delhi", 'timestamp': ts_base.strftime('%Y-%m-%d %H:%M:%S') })
    rows.append({ 'transaction_id': f"TXN-{get_id()}", 'user_id': p2, 'recipient_id': p3, 'amount': 99000, 'location': "Delhi", 'timestamp': (ts_base + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S') })
    rows.append({ 'transaction_id': f"TXN-{get_id()}", 'user_id': p3, 'recipient_id': p1, 'amount': 99000, 'location': "Delhi", 'timestamp': (ts_base + timedelta(minutes=4)).strftime('%Y-%m-%d %H:%M:%S') })

    # 5. WHALE ALERT (3 rows)
    for i in range(3):
        rows.append({
            'transaction_id': f"TXN-{get_id()}", 'user_id': "Institutional_Investor", 'recipient_id': "Crypto_Exchange",
            'amount': 2500000, 'location': "Dubai, UAE", 'timestamp': (start_time + timedelta(hours=30+i)).strftime('%Y-%m-%d %H:%M:%S')
        })

    # 6. Technical Anomalies (3 rows)
    fixed_id = f"DUP-{get_id()}"
    rows.append({ 'transaction_id': fixed_id, 'user_id': "Legacy_User", 'recipient_id': "Vendor_A", 'amount': 1500, 'location': "Delhi", 'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S') })
    rows.append({ 'transaction_id': fixed_id, 'user_id': "Legacy_User", 'recipient_id': "Vendor_A", 'amount': 1500, 'location': "Delhi", 'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S') })
    
    # Future Txn
    rows.append({ 'transaction_id': f"TXN-{get_id()}", 'user_id': "Time_Traveler", 'recipient_id': "Shop_X", 'amount': 50, 'location': "Mumbai", 'timestamp': "2029-12-31 23:59:59" })
    
    df = pd.DataFrame(rows)
    # Shuffle the dataset so anomalies aren't grouped
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save
    path = "C:/Users/rohit/Downloads/ProJ/vigilo_demo_300.csv"
    df.to_csv(path, index=False)
    print(f"Dataset generated at: {path}")

if __name__ == "__main__":
    generate_complex_dataset(300)
