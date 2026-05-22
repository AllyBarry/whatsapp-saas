"""Meta webhook signature verification (X-Hub-Signature-256)."""
import hashlib
import hmac


def verify_signature(*, app_secret: str, raw_body: bytes, signature_header: str | None) -> bool:
    """Validate an X-Hub-Signature-256 header against the raw request body.

    Meta signs the request body with HMAC-SHA256 keyed by the app secret and
    sends it as `sha256=<hexdigest>`. The raw, unparsed body must be used.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        app_secret.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256
    ).hexdigest()
    provided = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)
