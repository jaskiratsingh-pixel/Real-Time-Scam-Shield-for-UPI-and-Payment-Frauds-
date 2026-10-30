import cv2


def _try_decode(detector, img):
    text, _, _ = detector.detectAndDecode(img)
    return text if text else None


def decode_qr(image_path):
    """Read a QR image and return the text inside it, or None if not found.
    Retries at several sizes with a white border."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = cv2.QRCodeDetector()
    h, w = gray.shape

    for side in (None, 800, 1200, 600, 1000, 400):
        g = gray
        if side:
            scale = side / max(h, w)
            g = cv2.resize(gray, None, fx=scale, fy=scale,
                           interpolation=cv2.INTER_AREA)
        g = cv2.copyMakeBorder(g, 30, 30, 30, 30,
                               cv2.BORDER_CONSTANT, value=255)
        result = _try_decode(detector, g)
        if result:
            return result

    # last resort: newer, more robust OpenCV detector
    return _try_decode(cv2.QRCodeDetectorAruco(), gray)