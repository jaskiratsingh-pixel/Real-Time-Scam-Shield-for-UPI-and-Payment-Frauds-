# Generated with Claude, reviewed and modified by the team
from checkers.message import check_message
from scoring import verdict_from_score, combine


def test_verdict_bands():
    assert verdict_from_score(10) == "safe"
    assert verdict_from_score(45) == "suspicious"
    assert verdict_from_score(75) == "scam"


def test_otp_and_link_is_scam():
    msg = check_message("Share your OTP now http://bit.ly/abc")
    assert combine(msg)["verdict"] == "scam"


def test_genuine_otp_is_safe():
    msg = check_message("Your OTP is 482910. Do not share this with anyone.")
    assert combine(msg)["verdict"] == "safe"
    
    
def test_prize_plus_call_is_suspicious():
    msg = check_message(
        "Congratulations you won a lucky draw of Rs 25 lakh. "
        "Call customer care 98XXXXXX10 to claim"
    )
    assert combine(msg)["verdict"] == "suspicious"