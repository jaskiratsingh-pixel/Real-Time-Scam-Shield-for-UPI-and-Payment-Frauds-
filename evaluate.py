import os
from urllib.parse import urlparse, parse_qs

import pandas as pd
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             classification_report)
from checkers.qr import decode_qr

# ---- Change these to match the values in your CSV "label" column ----
SCAM = "scam"
SAFE = "safe"
# ---------------------------------------------------------------------

df = pd.read_csv("data/labelled_items.csv")
df["decoded"] = df["image_file"].apply(lambda f: decode_qr(f"test_qr/{f}"))

# 1) QR decode accuracy
df["exact"] = df["decoded"] == df["qr_text"]
print(f"Decode accuracy: {df['exact'].mean():.3f} "
      f"({df['exact'].sum()}/{len(df)})")

# 2) Scam classification from the DECODED text
BAD_WORDS = ["urgent", "refund", "lottery", "kyc", "reward", "verify", "prize"]


def predict(text):
    """Placeholder rules. Swap in your real classifier if you have one."""
    if not isinstance(text, str) or not text.strip():
        return "undecoded"
    t = text.lower()
    if any(w in t for w in BAD_WORDS):
        return SCAM
    # UPI link that has an amount (am) but no payee address (pa)
    if t.startswith("upi://"):
        params = parse_qs(urlparse(t).query)
        if "am" in params and "pa" not in params:
            return SCAM
    return SAFE


df["pred"] = df["decoded"].apply(predict)

# Report undecoded rows separately, evaluate the rest
undecoded = (df["pred"] == "undecoded").sum()
print(f"\nUndecoded QR codes: {undecoded}/{len(df)}")

scored = df[df["pred"] != "undecoded"]
labels = sorted(df["label"].unique())

print("\nAccuracy:", round(accuracy_score(scored["label"], scored["pred"]), 3))
print("\nConfusion matrix (rows=true, cols=pred), labels:", labels)
print(confusion_matrix(scored["label"], scored["pred"], labels=labels))
print("\n", classification_report(scored["label"], scored["pred"],
                                  labels=labels, zero_division=0))

os.makedirs("data", exist_ok=True)
df.to_csv("data/results.csv", index=False)
