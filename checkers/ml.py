# Generated with Claude, reviewed and modified by the team
from pathlib import Path
import joblib

_model = None
_tried = False


def predict_scam_prob(text):
    """Probability 0..1 that text is a scam, or None if the model is unavailable."""
    global _model, _tried
    if not _tried:
        _tried = True
        try:
            _model = joblib.load(Path(__file__).resolve().parent.parent / "model.joblib")
        except Exception:
            _model = None  # rules-only fallback, app never crashes
    if _model is None or not text or not text.strip():
        return None
    try:
        return float(_model.predict_proba([text])[0][1])
    except Exception:
        return None