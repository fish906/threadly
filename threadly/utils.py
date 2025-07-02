# myprog/utils.py

from passlib.context import CryptContext
import html

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_key(plain_key: str) -> str:
    return pwd_context.hash(plain_key)

def verify_key(plain_key: str, hashed_key: str) -> bool:
    return pwd_context.verify(plain_key, hashed_key)

def sanitize_input(text: str) -> str:
    """Basic sanitization to help prevent injection or HTML injection."""
    return html.escape(text.strip())
