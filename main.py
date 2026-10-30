# Real-Time Scam Shield
# Main detection engine

from checkers.message import check_message
from checkers.url import check_url
from checkers.qr import decode_qr
from scoring import combine, combine_qr


def analyze_message(text):
    """Analyze a message and any URLs found inside it."""

    # Check message
    message_result = check_message(text)

    # Extract URLs detected by message checker
    links = message_result.get("details", {}).get("links", [])

    # Check every detected URL
    url_results = []

    for link in links:
        result = check_url(link)
        url_results.append(result)

    # Combine message, URL and ML scores
    final_result = combine(
        message_result,
        url_results,
        text=text
    )

    return final_result


def analyze_url(url):
    """Analyze a single URL."""

    url_result = check_url(url)

    # Use URL score as the input message score
    message_result = {
        "score": 0,
        "reasons": [],
        "details": {}
    }

    return combine(
        message_result,
        [url_result],
        text=None
    )


def analyze_qr(image_path):
    """Decode and analyze a QR code."""

    qr_text = decode_qr(image_path)

    if not qr_text:
        return {
            "score": 0,
            "verdict": "unknown",
            "reasons": ["QR_NOT_DETECTED"],
            "details": {}
        }

    # Check decoded QR content as a URL if appropriate
    if qr_text.startswith(("http://", "https://", "www.")):
        result = check_url(qr_text)

        qr_result = {
            "score": result["score"],
            "reasons": result["reasons"],
            "details": {
                "decoded_text": qr_text,
                "url_details": result["details"]
            }
        }
    else:
        result = check_message(qr_text)

        qr_result = {
            "score": result["score"],
            "reasons": result["reasons"],
            "details": {
                "decoded_text": qr_text,
                "message_details": result["details"]
            }
        }

    return combine_qr(qr_result)


def print_result(result):
    """Display the final result."""

    print("\n========== SCAM SHIELD RESULT ==========")

    print("Risk Score:", result["score"], "/ 100")
    print("Verdict:", result["verdict"].upper())

    print("Reasons:")

    if result["reasons"]:
        for reason in result["reasons"]:
            print("-", reason)
    else:
        print("- No suspicious patterns detected")

    print("========================================\n")