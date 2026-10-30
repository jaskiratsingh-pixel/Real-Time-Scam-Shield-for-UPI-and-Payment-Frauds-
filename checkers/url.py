# Generated with Claude, reviewed and modified by the team
"""URL checker: looks for phishing signs in a link.
Returns the shared contract: {"score": 0-100, "reasons": [CODES], "details": {...}}
It never crashes: bad input or a failed lookup just gives fewer points."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

import tldextract

BASE = Path(__file__).resolve().parent.parent
BRANDS_FILE = BASE / "data" / "brands.txt"
CACHE_FILE = BASE / "data" / "whois_cache.json"

# Offline-safe: use tldextract's built-in list, never download one
_extract = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)

DEFAULT_BRANDS = ["paytm", "phonepe", "sbi", "hdfc", "icici", "gpay", "npci"]

# Official domains: exact match gives score 0 (check these on each bank's real site)
OFFICIAL_DOMAINS = {
    "paytm.com", "phonepe.com", "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com",
    "icicibank.com", "npci.org.in", "google.com", "cybercrime.gov.in",
}
SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "rb.gy", "t.co", "goo.gl", "ow.ly"}
ODD_TLDS = {"xyz", "top", "click", "icu", "vip", "link", "site", "online", "buzz"}
IPV4_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def load_brands():
    """Read brand names from data/brands.txt (fallback: built-in list)."""
    try:
        names = [b.strip().lower() for b in BRANDS_FILE.read_text(encoding="utf-8").splitlines()]
        names = [b for b in names if b]
        return names or DEFAULT_BRANDS
    except OSError:
        return DEFAULT_BRANDS


def _normalise(label):
    """Undo common letter tricks: 0->o, 1->l, rn->m."""
    return label.replace("0", "o").replace("1", "l").replace("rn", "m")


def _load_cache():
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save_cache(cache):
    try:
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass  # cache is optional


def _whois_created(domain):
    import whois  # imported here so a missing library cannot break the module
    created = whois.whois(domain).creation_date
    if isinstance(created, list):
        created = min(c for c in created if c)
    return created


def domain_age_days(domain, timeout=4):
    """Age of a domain in days, or None if unknown. Uses a cache and a timeout."""
    cache = _load_cache()
    created_iso = cache.get(domain)
    if created_iso is None:
        pool = ThreadPoolExecutor(max_workers=1)
        try:
            created = pool.submit(_whois_created, domain).result(timeout=timeout)
            if not created:
                return None
            created_iso = created.isoformat()
            cache[domain] = created_iso          # only successful lookups are cached
            _save_cache(cache)
        except Exception:                        # timeout, blocked, bad data: age unknown
            return None
        finally:
            pool.shutdown(wait=False)
    try:
        created = datetime.fromisoformat(created_iso)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - created).days
    except ValueError:
        return None


def check_url(url, lookup_age=True):
    """Return {"score": int, "reasons": [codes], "details": {...}}."""
    empty = {"score": 0, "reasons": [], "details": {}}
    try:
        if not isinstance(url, str) or not url.strip():
            return empty
        raw = url.strip().rstrip(".,;)")
        explicit_scheme = "://" in raw
        parsed = urlparse(raw if explicit_scheme else "http://" + raw)
        host = (parsed.hostname or "").lower()
        if not host:
            return empty

        reasons, score = [], 0

        def add(code, points):
            nonlocal score
            reasons.append(code)
            score += points

        ext = _extract(host)
        registered = f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else host
        details = {"host": host, "domain": registered}

        # Official allow-list: exact match is safe
        if registered in OFFICIAL_DOMAINS and "@" not in parsed.netloc:
            return {"score": 0, "reasons": [], "details": {**details, "official": True}}

        if "@" in parsed.netloc:
            add("AT_SIGN", 25)
        if IPV4_RE.match(host):
            add("IP_HOST", 40)
        if "xn--" in host:
            add("PUNYCODE", 40)
        if registered in SHORTENERS:
            add("SHORT_LINK", 30)
        if ext.suffix.split(".")[-1] in ODD_TLDS:
            add("ODD_TLD", 15)
        if explicit_scheme and parsed.scheme == "http":
            add("NO_HTTPS", 10)
        if parsed.path.lower().endswith(".apk"):
            add("APK", 35)

        # Brand checks (skip for IPs and shorteners)
        if ext.domain and not IPV4_RE.match(host) and registered not in SHORTENERS:
            label = _normalise(ext.domain)
            parts = [p for p in re.split(r"[^a-z0-9]+", label) if p]
            tokens = [t for t in re.split(r"[^a-z0-9]+", host) if t]
            lookalike = brand_elsewhere = False
            for brand in load_brands():
                if any(SequenceMatcher(None, p, brand).ratio() >= 0.8 for p in [label] + parts):
                    lookalike = True
                elif brand in tokens or (len(brand) >= 4 and brand in label):
                    brand_elsewhere = True
            if lookalike:
                add("LOOKALIKE", 50)
            elif brand_elsewhere:
                add("BRAND_ELSEWHERE", 40)

        # Domain age (slow, so only for real names and only when allowed)
        if lookup_age and ext.domain and not IPV4_RE.match(host) and registered not in SHORTENERS:
            age = domain_age_days(registered)
            details["age_days"] = age
            if age is not None and age < 30:
                add("NEW_DOMAIN", 40)
            elif age is not None and age < 90:
                add("NEW_DOMAIN", 20)

        return {"score": max(0, min(100, score)), "reasons": reasons, "details": details}
    except Exception:                            # never crash the app
        return empty