# Generated with Claude, reviewed and modified by the team
"""Scoring: turns a 0-100 score into a verdict and applies override rules.
Verdicts: 0-29 safe (green), 30-59 suspicious (amber), 60-100 scam (red)."""


def verdict_from_score(score):
    """Map a number to 'safe', 'suspicious' or 'scam'."""
    if score >= 60:
        return "scam"
    if score >= 30:
        return "suspicious"
    return "safe"


def combine(message_result, url_results=None, ml_prob=None):
    """Combine the message result with any URL results (and optional ML probability).

    Returns the shared contract plus a 'verdict' key:
    {"score", "reasons", "details", "verdict"}
    """
    reasons = list(message_result.get("reasons", []))
    score = message_result.get("score", 0)

    # Add 60% of the worst URL score found in the message
    if url_results:
        worst = max(url_results, key=lambda r: r.get("score", 0))
        score += 0.6 * worst.get("score", 0)
        for code in worst.get("reasons", []):
            if code not in reasons:
                reasons.append(code)

    # Optional ML second opinion (a probability from 0 to 1)
    if ml_prob is not None:
        if ml_prob >= 0.85:
            score += 15
        elif ml_prob <= 0.15:
            score -= 10

    score = max(0, min(100, round(score)))

        # Overrides: these are always Scam
    asks_secret = "ASKS_SECRET" in reasons
    has_link = "HAS_LINK" in reasons
    prize_and_call = "PRIZE_BAIT" in reasons and "CALL_NUMBER" in reasons
    if ((asks_secret and has_link) or "COLLECT_TRICK" in reasons
            or "SCAN_TO_RECEIVE" in reasons or prize_and_call):
        score = max(score, 60)

    return {
        "score": score,
        "reasons": reasons,
        "details": message_result.get("details", {}),
        "verdict": verdict_from_score(score),
    }