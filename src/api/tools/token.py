import hashlib


def hash_access_token(access_token: str) -> str:
    """
    Hashes the access token using Bcrypt.

    Args:
        token (str): The access token to hash.

    Returns:
        str: The hashed access token.
    """
    access_token_bytes = access_token.encode("utf-8")
    return hashlib.sha512(access_token_bytes).hexdigest()
