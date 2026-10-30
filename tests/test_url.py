# Generated with Claude, reviewed and modified by the team
from checkers.url import check_url


def check(u):
    return check_url(u, lookup_age=False)


def test_shortener():
    assert "SHORT_LINK" in check("http://bit.ly/abc")["reasons"]


def test_brand_in_other_domain():
    r = check("http://paytm-secure.xyz/login")
    assert "LOOKALIKE" in r["reasons"] and "ODD_TLD" in r["reasons"]
    assert r["score"] >= 60


def test_brand_as_subdomain():
    assert "BRAND_ELSEWHERE" in check("https://sbi.kyc-update.top")["reasons"]


def test_lookalike():
    assert "LOOKALIKE" in check("https://phonepay.in")["reasons"]


def test_ip_and_http():
    r = check("http://192.168.1.1/login")
    assert "IP_HOST" in r["reasons"] and "NO_HTTPS" in r["reasons"]


def test_official_is_zero():
    assert check("https://paytm.com")["score"] == 0


def test_at_sign_trick():
    assert "AT_SIGN" in check("http://paytm.com@evil.top")["reasons"]


def test_apk():
    assert "APK" in check("https://example.com/app.apk")["reasons"]


def test_garbage_does_not_crash():
    assert check("")["score"] == 0
    assert check(None)["score"] == 0
    assert check("not a link at all !!")["score"] >= 0