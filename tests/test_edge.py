# Generated with Claude, reviewed and modified by the team
import pytest
from checkers.message import check_message
from checkers.url import check_url
from scoring import combine, combine_qr

CASES = ["", "   ", "a" * 10000, "😀😀😀",
         "आपका खाता बंद हो जाएगा, OTP बताएं",
         "ਤੁਹਾਡਾ ਖਾਤਾ ਬੰਦ ਹੋ ਜਾਵੇਗਾ",
         "pay at bit.ly/abc now", "http://",
         "see http://a.com and http://b.xyz and bit.ly/x"]


@pytest.mark.parametrize("text", CASES)
def test_pipeline_never_crashes(text):
    msg = check_message(text)
    assert isinstance(msg["details"]["links"], list)
    urls = [check_url(u) for u in msg["details"]["links"]]
    r = combine(msg, urls, text=text)
    assert r["verdict"] in ("safe", "suspicious", "scam")
    assert 0 <= r["score"] <= 100


@pytest.mark.parametrize("u", ["http://", "notaurl", "", "http://[bad", "xn--80ak6aa92e.com"])
def test_url_never_crashes(u):
    check_url(u)


def test_qr_shop_is_suspicious():
    r = combine_qr({"score": 0, "reasons": ["PAY_REQUEST"], "details": {}})
    assert r["verdict"] == "suspicious"


def test_qr_refund_is_scam():
    r = combine_qr({"score": 90, "reasons": ["PAY_REQUEST", "SCAN_TO_RECEIVE"], "details": {}})
    assert r["verdict"] == "scam"