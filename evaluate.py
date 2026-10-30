import pandas as pd
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             classification_report)


df = pd.read_csv("data/labelled_items.csv")
df["decoded"] = df["image_file"].apply(lambda f: decode_qr(f"test_qr/{f}"))

# 1) QR decode accuracy
df["exact"] = df["decoded"] == df["qr_text"]
print(f"Decode accuracy: {df['exact'].mean():.3f} "
      f"({df['exact'].sum()}/{len(df)})")

# 2) Scam classification from the DECODED text
SCAM = "scam"          # <- change to match your label value

def predict(text):
    """Placeholder rules. Swap in your real classifier if you have one."""
    if not text:
        return "undecoded"
    t = text.lower()
    bad = ["urgent", "refund", "lottery", "kyc", "reward", "verify", "prize"]
    if any(w in t for w in bad) or "am=" in t and "pa=" not in t:
        return SCAM
    return [l for l in df["label"].unique() if l != SCAM][0]

df["pred"] = df["decoded"].apply(predict)
labels = sorted(df["label"].unique())
print("\nAccuracy:", round(accuracy_score(df["label"], df["pred"]), 3))
print("\nConfusion matrix (rows=true, cols=pred), labels:", labels)
print(confusion_matrix(df["label"], df["pred"], labels=labels))
print("\n", classification_report(df["label"], df["pred"], labels=labels,
                                  zero_division=0))
df.to_csv("data/results.csv", index=False)
from qr import decode_qrfrom checkers.qr import decode_qr
got = df["image_file"].apply(lambda f: decode_qr(f"test_qr/{f}"))
ok = (got == df["qr_text"])
print(f"\nQR decode accuracy: {ok.mean():.3f} ({ok.sum()}/{len(df)})")