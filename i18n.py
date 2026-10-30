LANGS = {"English": "en", "हिन्दी": "hi", "ਪੰਜਾਬੀ": "pa"}

REASONS = {
  "ASKS_SECRET": {"en": "It asks for your OTP, PIN or password. Real banks never do.",
                  "hi": "...", "pa": "..."},
  "COLLECT_TRICK": {"en": "Approving a collect request sends money OUT. You never need a PIN to receive money.",
                    "hi": "...", "pa": "..."},
  "URGENCY": {"en": "It rushes or threatens you (blocked, expires today).", "hi": "...", "pa": "..."},
  # ... one entry per code above
}

ADVICE = {
  "safe":       {"en": "Looks fine, but never share your OTP or PIN.", "hi": "...", "pa": "..."},
  "suspicious": {"en": "Be careful. Do not click links or pay. Check with your bank.", "hi": "...", "pa": "..."},
  "scam":       {"en": "Do not share OTP, do not click, do not pay. Call your bank using the number on your card.",
                 "hi": "...", "pa": "..."},
}

LABELS = {
  "title":   {"en": "Real-Time Scam Shield", "hi": "...", "pa": "..."},
  "privacy": {"en": "Your text is checked here and not saved.", "hi": "...", "pa": "..."},
  "verdict_safe": {"en": "SAFE", "hi": "सुरक्षित", "pa": "ਸੁਰੱਖਿਅਤ"},
  "verdict_suspicious": {"en": "SUSPICIOUS", "hi": "संदिग्ध", "pa": "ਸ਼ੱਕੀ"},
  "verdict_scam": {"en": "SCAM", "hi": "धोखाधड़ी", "pa": "ਧੋਖਾਧੜੀ"},
  # tab_message, tab_link, tab_qr, check, paste_here, report, call_1930, copy_summary,
  # read_aloud, large_text, disclaimer, why, advice, qr_context ...
}

def _get(table, key, lang):
    entry = table.get(key, {})
    return entry.get(lang) or entry.get("en") or key   # never crash on a missing code

def reason(code, lang): return _get(REASONS, code, lang)
def advice(verdict, lang): return _get(ADVICE, verdict, lang)
def label(key, lang): return _get(LABELS, key, lang)