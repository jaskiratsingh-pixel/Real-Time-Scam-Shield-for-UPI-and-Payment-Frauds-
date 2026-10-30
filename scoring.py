# Generated with Claude, reviewed and modified by the team

from checkers.ml import predict_scam_prob


def verdict_from_score(score):
    """Convert a numerical score into a verdict."""
    score = max(0, min(100, int(round(score))))

    if score < 30:
        return "safe"
    elif score < 60:
        return "suspicious"
    else:
        return "scam"


def _clamp(score):
    return max(0, min(100, int(round(score))))


def ml_adjust(text, score):
    """ML provides a small second opinion."""
    try:
        p = predict_scam_prob(text)
    except Exception:
        p = None

    if p is None:
        return score

    if p >= 0.85:
        score += 10
    elif p <= 0.15:
        score -= 10

    return _clamp(score)


def combine(msg, urls=None, text=None):
    """
    Combine message and URL scores.
    ML optionally provides a second opinion.
    """

    urls = urls or []

    score = msg.get("score", 0)
    reasons = list(msg.get("reasons", []))
    details = dict(msg.get("details") or {})

    # Combine URL scores
    if urls:
        top_url = max(u.get("score", 0) for u in urls)

        score += 0.6 * top_url

        for url in urls:
            reasons += url.get("reasons", [])

        details["url_details"] = [
            u.get("details", {}) for u in urls
        ]

    score = _clamp(score)

    # ML adjustment
    if text:
        score = ml_adjust(text, score)

    # Mandatory scam overrides
    if "COLLECT_TRICK" in reasons:
        score = max(score, 60)

    if "SCAN_TO_RECEIVE" in reasons:
        score = max(score, 60)

    if "ASKS_SECRET" in reasons and (
        "HAS_LINK" in reasons or urls
    ):
        score = max(score, 60)

    score = _clamp(score)

    return {
        "score": score,
        "reasons": list(dict.fromkeys(reasons)),
        "details": details,
        "verdict": verdict_from_score(score),
    }


def combine_qr(qr):
    import re

    score = qr.get("score", 0)
    reasons = list(qr.get("reasons", []))
    details = dict(qr.get("details") or {})

    text = details.get("decoded_text", "").lower()

    # SCAM: urgent demand for money
    urgent_payment = (
        any(word in text for word in ["send", "pay", "transfer"])
        and any(word in text for word in ["urgent", "immediately", "now"])
        and any(word in text for word in ["payment", "money", "rs ", "rupees"])
    )

    if urgent_payment:
        score = max(score, 70)
        reasons.append("URGENT_PAYMENT_DEMAND")

    # SUSPICIOUS: pending payment requiring verification
    elif "payment pending" in text:
        score = max(score, 35)
        reasons.append("PENDING_PAYMENT_VERIFY")

    # Existing QR rules
    if "PAY_REQUEST" in reasons:
        score = max(score, 30)

    if "SCAN_TO_RECEIVE" in reasons:
        score = max(score, 60)

    score = _clamp(score)

    return {
        "score": score,
        "reasons": list(dict.fromkeys(reasons)),
        "details": details,
        "verdict": verdict_from_score(score)
    }