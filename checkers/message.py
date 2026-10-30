# Generated with Claude, reviewed and modified by the team
"""Message checker: reads SMS/WhatsApp text and returns the shared contract:
{"score": 0-100, "reasons": [CODES], "details": {...}}"""
import re

F = re.I  # ignore upper/lower case

# --- Rules that ADD points: code -> (points, list of patterns) ---
RULES = {
    "ASKS_SECRET": (45, [
        r"\b(?:share|send|enter|give|tell|provide|submit|reply with)\b.{0,30}\b(?:otp|pin|cvv|password|passcode)\b",
        r"\b(?:otp|pin|cvv|password)\b.{0,20}\b(?:batao|bata do|bhejo|daalo|dalo|dasso|share karo|send karo)\b",
    ]),
    "COLLECT_TRICK": (50, [
        r"\bcollect request\b.{0,60}\b(?:approve|accept|pin)\b",
        r"\b(?:approve|accept)\b.{0,40}\bcollect\b",
        r"\bpin\b.{0,30}\b(?:to receive|receive money|to get)\b",
        r"\bapprove karo\b",
    ]),
    "SCAN_TO_RECEIVE": (50, [
        r"\bscan\b.{0,60}\b(?:receive|refund|prize|reward|cashback|claim)\b",
    ]),
    "URGENCY": (20, [
        r"\b(?:urgent|urgently|immediately|last chance|legal action|deactivated|suspended|blocked)\b",
        r"\bwithin \d+ ?(?:hours|hrs|hour)\b",
        r"\bwill be (?:blocked|suspended|closed|deactivated)\b",
        r"\b(?:turant|abhi|aaj hi|jaldi|band ho jayega|block ho jayega|khata band)\b",
    ]),
    "PRIZE_BAIT": (30, [
        r"\b(?:you have won|you won|winner|lottery|lucky draw|free gift|prize|kbc|congratulations)\b",
        r"\b(?:inaam|jeet gaye|muft)\b",
    ]),
    "CALL_NUMBER": (15, [
        r"\b(?:call|dial|contact)\b.{0,30}(?:\+?\d[\d\s-]{7,}|number|customer care|helpline|support|executive)",
        r"\b(?:customer care|helpline)\b",
        r"\bcall karo\b",
    ]),
    "INSTALL_APP": (35, [
        r"\binstall\b",
        r"\bdownload\b.{0,20}\bapp\b",
        r"\.apk\b",
        r"\b(?:anydesk|teamviewer|quicksupport)\b",
    ]),
}

# --- Link detection (HAS_LINK +10) ---
LINK_RE = re.compile(
    r"https?://\S+|www\.\S+"
    r"|\b(?:bit\.ly|tinyurl\.com|cutt\.ly|is\.gd|rb\.gy)/?\S*"
    r"|\b[a-z0-9-]{2,}\.(?:xyz|top|click|icu|vip|link|site|online)\b\S*", F)

# --- Genuine patterns ---
# "Do not share ..." sentences are warnings, so we cut them out before checking ASKS_SECRET.
WARNING_RE = re.compile(
    r"\b(?:do not|don't|dont|never)\s+(?:share|tell|give|disclose|send)\b[^.!?]*"
    r"|\bmat\s+(?:batao|bataye|bhejo|share|dena)\b[^.!?]*", F)
BANK_ALERT_RE = re.compile(
    r"\b(?:a/c|acct|account)\b.{0,40}\b(?:debited|credited)\b"
    r"|\b(?:debited|credited)\b.{0,40}(?:rs\.?|inr|₹)", F)


def check_message(text):
    """Return {"score": int, "reasons": [codes], "details": {...}}."""
    # Empty or non-text input is treated as safe, and we never crash
    if not isinstance(text, str) or not text.strip():
        return {"score": 0, "reasons": [], "details": {"links": [], "genuine": []}}

    t = " ".join(text.lower().split())          # lowercase, tidy spaces
    links = LINK_RE.findall(t)
    has_link = bool(links)
    has_warning = bool(WARNING_RE.search(t))
    t_for_secret = WARNING_RE.sub(" ", t)       # remove "do not share" sentences

    score, reasons, genuine = 0, [], []

    for code, (points, patterns) in RULES.items():
        subject = t_for_secret if code == "ASKS_SECRET" else t
        if any(re.search(p, subject, F) for p in patterns):
            score += points
            reasons.append(code)

    if has_link:
        score += 10
        reasons.append("HAS_LINK")

    # Genuine patterns lower the score (only when there is no link)
    if has_warning and not has_link:
        score -= 30
        genuine.append("DO_NOT_SHARE_NOTICE")
    if BANK_ALERT_RE.search(t) and not has_link:
        score -= 20
        genuine.append("BANK_ALERT_FORMAT")

    score = max(0, min(100, score))             # clamp 0..100
    return {"score": score, "reasons": reasons,
            "details": {"links": links, "genuine": genuine}}