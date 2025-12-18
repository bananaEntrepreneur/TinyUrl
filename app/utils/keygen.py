import secrets
import string


def create_random_key(length: int = 5) -> str:
    """
    Creates a random key and returns it.

    Args:
        length: Key length (default: 5)

    Returns:
        Random key
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))