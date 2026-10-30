# Generated with Claude, reviewed and modified by the team
from checkers.message import check_message


def test_genuine_otp_is_safe():
    r = check_message("Your OTP for login is 482910. Do not share this with anyone.")
    assert r["score"] < 30 and "ASKS_SECRET" not in r["reasons"]


def test_fake_kyc_with_link():
    r = check_message("Dear customer your SBI account will be blocked today. Update KYC http://sbi-kyc.xyz")
    assert "URGENCY" in r["reasons"] and "HAS_LINK" in r["reasons"] and r["score"] >= 30


def test_collect_request_trick():
    r = check_message("Rs 500 collect request from Rahul. Approve and enter PIN to receive money")
    assert "COLLECT_TRICK" in r["reasons"] and r["score"] >= 60


def test_bank_alert_is_safe():
    r = check_message("A/c XX1234 debited Rs 250.00 on 12-10. Avl bal Rs 3,400. -YourBank")
    assert r["score"] < 30


def test_hinglish_kyc():
    r = check_message("Aapka khata band ho jayega. Abhi KYC update karo bit.ly/abc")
    assert "URGENCY" in r["reasons"] and "HAS_LINK" in r["reasons"]


def test_hinglish_otp_ask():
    r = check_message("OTP batao abhi")
    assert "ASKS_SECRET" in r["reasons"] and r["score"] >= 60


def test_scan_to_receive():
    r = check_message("Scan this QR code to receive your refund of Rs 2000")
    assert "SCAN_TO_RECEIVE" in r["reasons"]


def test_empty_text_does_not_crash():
    assert check_message("")["score"] == 0