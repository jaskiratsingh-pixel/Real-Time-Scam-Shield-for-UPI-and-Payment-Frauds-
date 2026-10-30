import os
import random
from urllib.parse import quote

import pandas as pd
import qrcode

random.seed(42)
os.makedirs("test_qr", exist_ok=True)
os.makedirs("data", exist_ok=True)

banks = ["oksbi", "okhdfcbank", "okicici", "paytm", "ybl", "axl"]
shops = ["Sharma Store", "Gupta Medicals", "Royal Bakery", "City Fruits",
         "Anand Tea Stall", "Kumar Stationery", "Singh Dairy",
         "Patel Mobile Repair", "Green Grocers", "Raj Tailors",
         "Lakshmi Sweets", "Metro Cafe", "Verma Books", "Joshi Hardware",
         "Fresh Veg Mart"]
people = ["Ramesh Kumar", "Priya Singh", "Amit Verma", "Neha Sharma",
          "Suresh Yadav", "Anjali Gupta", "Rohit Mehra", "Kavita Joshi",
          "Manoj Tiwari", "Pooja Nair"]
scam_names = ["SBI Refund Desk", "KYC Update Support", "Lucky Draw Winner",
              "Cashback Claim", "Customer Care Helpdesk",
              "Electricity Bill Officer", "Income Tax Refund",
              "Prize Claim Center", "Bank Verification", "Gift Reward Team"]
scam_words = ["refund", "kyc", "prize", "lottery", "cashback", "helpdesk",
              "reward", "claim", "support", "verify"]
scam_urls = ["http://sbi-kyc-update.xyz/login", "http://bit.ly/refund-now",
             "http://paytm-cashback.top/claim", "http://upi-verify.online/pay",
             "http://lucky-draw-win.click/prize"]

rows = []

# 55 legit items
for i in range(55):
    name = random.choice(shops + people)
    if random.random() < 0.5:
        pa = f"{random.randint(6000000000, 9999999999)}@{random.choice(banks)}"
    else:
        pa = f"{name.lower().replace(' ', '')}@{random.choice(banks)}"
    text = f"upi://pay?pa={pa}&pn={quote(name)}"
    if random.random() < 0.5:
        text += f"&am={random.choice([10, 20, 50, 100, 150, 250, 500, 1200])}"
    rows.append((text, "legit"))

# 55 scam items
for i in range(55):
    if i % 11 == 10:
        text = random.choice(scam_urls) + f"?id={random.randint(100, 999)}"
    else:
        pa = f"{random.choice(scam_words)}{random.randint(10, 9999)}@{random.choice(banks)}"
        name = random.choice(scam_names)
        amount = random.randint(4999, 49999)
        text = f"upi://pay?pa={pa}&pn={quote(name)}&am={amount}&tn=urgent"
    rows.append((text, "scam"))

random.shuffle(rows)

data = []
for n, (text, label) in enumerate(rows, start=1):
    filename = f"item_{n:03d}.png"
    qrcode.make(text, box_size=10, border=4).save(os.path.join("test_qr", filename))
    data.append({"id": n, "qr_text": text, "label": label,
                 "image_file": filename})

df = pd.DataFrame(data)
df.to_csv(os.path.join("data", "labelled_items.csv"), index=False)
print(df["label"].value_counts())
print("Saved", len(df), "items")