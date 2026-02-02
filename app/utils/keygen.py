import secrets
import string
import hashlib
import time

def create_random_key(length: int = 8) -> str:
    timestamp = str(time.time()).encode('utf-8')
    random_bytes = secrets.token_bytes(32)
    combined = timestamp + random_bytes
    hash_digest = hashlib.sha256(combined).hexdigest()
    chars = string.ascii_letters + string.digits
    return "".join(chars[int(hash_digest[i], 16) % len(chars)] for i in range(length))