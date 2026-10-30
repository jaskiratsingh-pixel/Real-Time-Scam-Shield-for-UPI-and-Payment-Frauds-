# Generated with Claude, reviewed and modified by the team
import glob
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

TEXT_COLS = ["text", "message", "msg", "sms", "content", "input"]
LABEL_COLS = ["label", "verdict", "expected", "truth"]
SKIP = ("results.csv",)


def find_dataset():
    best = None
    for path in glob.glob("data/*.csv"):
        if path.replace("\\", "/").split("/")[-1] in SKIP:
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        t = [c for c in TEXT_COLS if c in df.columns]
        l = [c for c in LABEL_COLS if c in df.columns]
        print(f"Checked {path}: columns {list(df.columns)}")
        if t and l and (best is None or len(df) > len(best[1])):
            best = (path, df, t[0], l[0])
    return best


found = find_dataset()
if found is None:
    raise SystemExit("\nNo message CSV found in data/. Ask Laptop C for data/messages.csv "
                     "with columns text,label (label = scam / suspicious / safe).")

path, df, tcol, lcol = found
print("\nUsing:", path)
df = df[[tcol, lcol]].dropna()
X = df[tcol].astype(str)
y = (df[lcol].astype(str).str.lower().str.strip() == "scam").astype(int)  # 1 = scam
print("Rows:", len(df), "| scam:", int(y.sum()), "| not scam:", int((y == 0).sum()))

if len(df) < 20 or y.sum() < 2 or (y == 0).sum() < 2:
    raise SystemExit("Too little data. Need at least 20 rows with several scam and several safe.")

model = make_pipeline(
    TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=True),
    LogisticRegression(class_weight="balanced", max_iter=1000),
)

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
model.fit(Xtr, ytr)
pred = model.predict(Xte)
print("Accuracy :", round(accuracy_score(yte, pred), 3))
print("Precision:", round(precision_score(yte, pred, zero_division=0), 3))
print("Recall   :", round(recall_score(yte, pred, zero_division=0), 3))
print("Confusion matrix [[TN FP] [FN TP]]:\n", confusion_matrix(yte, pred))

model.fit(X, y)  # final model uses all data
joblib.dump(model, "model.joblib")
print("Saved model.joblib")