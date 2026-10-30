import re

def mask_text(text: str) -> str:
    """Hide OTPs, card/account numbers and phone numbers. Nothing is stored."""
    # digits right after the word OTP (keep length, replace with *)
    text = re.sub(r"(?i)(otp\D{0,15})(\d{4,8})",
                  lambda m: m.group(1) + "*" * len(m.group(2)), text)
    # card-like: 16 digits with optional spaces/dashes
    text = re.sub(r"\b(?:\d[ -]?){15}\d\b", lambda m: "*" * len(m.group(0)), text)
    # phone / account: 9-18 digits (not inside URLs or words)
    text = re.sub(r"(?<![\w/.])(?:\+?91[\s-]?)?\d{9,18}(?!\w)",
                  lambda m: "*" * len(m.group(0)), text)
    return text

if __name__ == "__main__":
    print(mask_text("call 9876543210, OTP 123456"))