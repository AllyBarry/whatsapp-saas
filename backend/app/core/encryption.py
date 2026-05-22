"""AES (Fernet) encryption utility for credential storage at rest."""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _build_fernet() -> Fernet:
    key = settings.encryption_key
    try:
        # Accept a ready-made Fernet key.
        return Fernet(key.encode())
    except (ValueError, TypeError):
        # Otherwise derive a stable 32-byte key from the configured secret.
        digest = hashlib.sha256(key.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(digest))


_fernet = _build_fernet()


def encrypt(plaintext: str) -> str:
    """Encrypt a string for storage. Returns url-safe ciphertext."""
    if plaintext is None:
        raise ValueError("Cannot encrypt None")
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a stored ciphertext string."""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt value") from exc
