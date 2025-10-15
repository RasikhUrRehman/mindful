import re
from pydantic import EmailStr


def validate_email(email: str) -> bool:
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_valid_email(email: str) -> bool:
    """Check if email is in valid format."""
    try:
        # Simple validation using regex
        return validate_email(email)
    except Exception:
        return False
