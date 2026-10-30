# Generated with Claude, reviewed and modified by the team
from checkers.message import check_message
from checkers.url import check_url
from scoring import combine

# (message, what you EXPECT: safe / suspicious / scam). Fake numbers only.
TESTS = [
    ("Your order #1234 is out for delivery. Track it in the app.", "safe"),
    ("A/c XX1234 credited Rs 5000 on 30-10. Avl bal Rs 8,400. -YourBank", "safe"),
    ("Your OTP is 482910. Do not share this with anyone.", "safe"),
    ("Congratulations you won a lucky draw of Rs 25 lakh. Call customer care 98XXXXXX10 to claim", "scam"),
    ("Install this app to track your parcel https://track-parcel.top/app.apk", "scam"),
    ("Aapka OTP batao warna account band ho jayega", "scam"),
]

for text, expected in TESTS:
    m = check_message(text)
    urls = [check_url(u, lookup_age=False) for u in m["details"]["links"]]
    r = combine(m, urls)
    flag = "OK   " if r["verdict"] == expected else "WRONG"
    print(f"{flag} got={r['verdict']:<10} expected={expected:<10} score={r['score']:<3} {r['reasons']}")
    print(f"      {text[:70]}")
    