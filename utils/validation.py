import re

def validate_phone(phone: str) -> bool:
    """Validate 10-digit phone number."""
    if not phone:
        return False
    try:
        cleaned = re.sub(r"\D", "", str(phone))
        return len(cleaned) == 10
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    try:
        email = email.strip()
        if len(email) < 5 or len(email) > 254:
            return False
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))
    except Exception:
        return False

def validate_aadhaar(aadhaar: str) -> bool:
    """Validate 12-digit Aadhaar number."""
    if not aadhaar:
        return False
    try:
        cleaned = re.sub(r"\D", "", str(aadhaar))
        return len(cleaned) == 12
    except Exception:
        return False

def validate_password_detailed(password: str) -> tuple[bool, str]:
    """Validate password with specific error messages."""
    if not password or not isinstance(password, str):
        return False, "Password cannot be empty."
    
    try:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character."
        
        return True, ""
        
    except Exception:
        return False, "Password validation failed."
