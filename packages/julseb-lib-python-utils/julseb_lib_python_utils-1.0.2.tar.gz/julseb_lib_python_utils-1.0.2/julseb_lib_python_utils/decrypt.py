from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt(text: str, secret_key: str) -> str:
    """
    Decrypts an encrypted string using AES-256-CBC encryption algorithm

    Args:
        text (str): The encrypted string in the format "iv:encryptedData" where both parts are hex-encoded
        secret_key (str): The secret key for decryption (must be exactly 32 characters long)

    Returns:
        str: The decrypted plain text string

    Example:
        decrypt("e0307ff76b606708a423018f41dc09f9:89748d0c6d7227fb37638c8111c0d4ef", "my32characterlongsecretkey123456")
        # Returns "Hello World"
    """
    # Split the IV and encrypted data
    iv_hex, encrypted_hex = text.split(":")

    # Convert hex strings back to bytes
    iv = bytes.fromhex(iv_hex)
    encrypted_data = bytes.fromhex(encrypted_hex)

    # Create cipher
    cipher = Cipher(
        algorithms.AES(secret_key.encode("utf-8")),
        modes.CBC(iv),
        backend=default_backend(),
    )

    # Decrypt the data
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove PKCS7 padding
    padding_length = decrypted_padded[-1]
    decrypted = decrypted_padded[:-padding_length]

    # Convert bytes back to string
    return decrypted.decode("utf-8")
