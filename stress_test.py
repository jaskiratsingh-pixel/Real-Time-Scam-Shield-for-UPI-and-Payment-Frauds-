# Generated with Claude, reviewed and modified by the team
from checkers.message import check_message
from checkers.url import check_url
from scoring import combine


def run(text):
    msg = check_message(text)
    urls = [check_url(u) for u in msg["details"]["links"]]
    return combine(msg, urls)


# (text, set of acceptable verdicts)
CASES = [
    # genuine: must NOT be flagged
    ("Cashback of Rs 50 credited to your wallet.", {"safe"}),
    ("Your KYC is verified successfully.", {"safe"}),
    ("Rs 250 debited from A/c XX1234. Avl bal Rs 3,400.", {"safe"}),
    ("Your Swiggy order is arriving in 10 minutes.", {"safe"}),
    ("Do not share your OTP with anyone. Your OTP is 482910.", {"safe"}),
    # scams: must be flagged red
    ("Aapka khata band ho jayega, abhi KYC update karo bit.ly/abc", {"scam"}),
    ("Rs 500 collect request. Approve and enter PIN to receive money", {"scam"}),
    ("Scan this QR to get your refund", {"scam"}),
    ("OTP dasso, nahi ta account band", {"scam"}),
]

# crash tests: only need to return without an exception
CRASH = [
    "", None, "a" * 10000, "😀😀😀",
    "आपका खाता बंद हो जाएगा, अभी KYC अपडेट करें",
    "ਤੁਹਾਡਾ ਖਾਤਾ ਬੰਦ ਹੋ ਜਾਵੇਗਾ, ਹੁਣੇ KYC ਅੱਪਡੇਟ ਕਰੋ",
    "http://a.com http://b.com http://c.com http://d.com http://e.com",
]

fails = 0
for text, ok in CASES:
    try:
        r = run(text)
        good = r["verdict"] in ok
        print("OK  " if good else "FAIL", r["verdict"], r["score"], r["reasons"], "|", text)
        fails += (not good)
    except Exception as e:
        print("CRASH", repr(e), "|", text)
        fails += 1

for text in CRASH:
    try:
        r = run(text)
        print("OK   no crash ->", r["verdict"], r["score"], "|", str(text)[:40])
    except Exception as e:
        print("CRASH", repr(e), "|", str(text)[:40])
        fails += 1

print("\nProblems found:", fails)