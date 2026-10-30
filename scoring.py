# Generated with Claude, reviewed and modified by the team
from checkers.ml import predict_scam_prob


def _verdict(score):
    if score < 30:
        return "safe"
    if score < 60:
        return "suspicious"
    return "scam"


def _clamp(score):
    return max(0, min(100, int(round(score))))


def ml_adjust(text, score):
    """ML gives a small second opinion: +10 if very sure scam, -10 if very sure genuine."""
    p = predict_scam_prob(text)
    if p is None:
        return score
    if p >= 0.85:
        score += 10
    elif p <= 0.15:
        score -= 10
    return _clamp(score)


def combine(msg, urls, text=None):
    """msg = check_message result, urls = list of check_url results,
    text = (masked) message text, optional, enables the ML nudge."""
    urls = urls or []
    score = msg.get("score", 0)
    reasons = list(msg.get("reasons", []))
    details = dict(msg.get("details") or {})
    details.setdefault("links", [])

    # 1. rules score + 0.6 x highest URL score
    if urls:
        top_url = max(u.get("score", 0) for u in urls)
        score += 0.6 * top_url
        for u in urls:
            reasons += u.get("reasons", [])
        details["url_details"] = [u.get("details", {}) for u in urls]
    score = _clamp(score)

    # 2. ML nudge (never crashes, skipped if model missing)
    if text:
        score = ml_adjust(text, score)

    # 3. overrides come AFTER ML, so ML can never cancel them
    if "COLLECT_TRICK" in reasons:
        score = max(score, 60)
    if "SCAN_TO_RECEIVE" in reasons:
        score = max(score, 60)
    if "ASKS_SECRET" in reasons and ("HAS_LINK" in reasons or urls):
        score = max(score, 60)

    score = _clamp(score)
    return {
        "score": score,
        "reasons": list(dict.fromkeys(reasons)),
        "details": details,
        "verdict": _verdict(score),
    }


def combine_qr(qr):
    """qr = result of analyse_qr(text, context)."""
    score = qr.get("score", 0)
    reasons = list(qr.get("reasons", []))
    if "PAY_REQUEST" in reasons:
        score = max(score, 30)   # a payment QR is never Safe
    if "SCAN_TO_RECEIVE" in reasons:
        score = max(score, 60)   # "receive" context = Scam
    score = _clamp(score)
    return {
        "score": score,
        "reasons": list(dict.fromkeys(reasons)),
        "details": qr.get("details", {}),
        "verdict": _verdict(score),
    }