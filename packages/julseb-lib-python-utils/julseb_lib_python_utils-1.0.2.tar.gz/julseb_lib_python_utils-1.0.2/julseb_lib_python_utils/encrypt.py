import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt(text: str, secret_key: str) -> str:
    """
    Encrypts a plain text string using AES-256-CBC encryption algorithm

    Args:
        text (str): The plain text string to encrypt
        secret_key (str): The secret key for encryption (must be exactly 32 characters long)

    Returns:
        str: The encrypted string in the format "iv:encryptedData" where both parts are hex-encoded

    Example:
        encrypt("Hello World", "my32characterlongsecretkey123456")
        # Returns "e0307ff76b606708a423018f41dc09f9:89748d0c6d7227fb37638c8111c0d4ef"
    """
    # Generate a random 16-byte IV
    iv = os.urandom(16)

    # Create cipher
    cipher = Cipher(
        algorithms.AES(secret_key.encode("utf-8")),
        modes.CBC(iv),
        backend=default_backend(),
    )

    # Encrypt the text
    encryptor = cipher.encryptor()

    # Pad the text to be a multiple of 16 bytes (AES block size)
    padded_text = text.encode("utf-8")
    padding_length = 16 - (len(padded_text) % 16)
    padded_text += bytes([padding_length] * padding_length)

    encrypted = encryptor.update(padded_text) + encryptor.finalize()

    # Return IV and encrypted data as hex strings separated by ":"
    return iv.hex() + ":" + encrypted.hex()
