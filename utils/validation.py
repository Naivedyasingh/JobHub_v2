# utils/validation.py

import re


class PhoneValidator:
    """Handles phone number validation."""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone is exactly 10 digits (Indian format).
        Strips non-digit characters before checking length.
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            bool: True if valid 10-digit phone number, False otherwise
        """
        if not phone:
            return False
        
        try:
            cleaned = re.sub(r"\D", "", str(phone))
            return len(cleaned) == 10
        except Exception:
            return False


class AadhaarValidator:
    """Handles Aadhaar number validation."""
    
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> bool:
        """
        Ensure Aadhaar is exactly 12 digits.
        Strips non-digit characters before checking length.
        
        Args:
            aadhaar: Aadhaar number string to validate
            
        Returns:
            bool: True if valid 12-digit Aadhaar number, False otherwise
        """
        if not aadhaar:
            return False
        
        try:
            cleaned = re.sub(r"\D", "", str(aadhaar))
            return len(cleaned) == 12
        except Exception:
            return False


class EmailValidator:
    """Handles email address validation."""
    
    def __init__(self):
        self.email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    
    def validate_email(self, email: str) -> bool:
        """
        Basic email format check.
        Returns True if matches pattern user@domain.tld
        
        Args:
            email: Email address string to validate
            
        Returns:
            bool: True if valid email format, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        try:
            # Trim whitespace
            email = email.strip()
            
            # Check basic length constraints
            if len(email) < 5 or len(email) > 254:  # RFC 5321 limit
                return False
            
            # Check pattern match
            return bool(re.match(self.email_pattern, email))
        except Exception:
            return False


class PasswordValidator:
    """Handles password validation with configurable policies."""
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, require_digit=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        
        # Compile regex patterns for efficiency
        self.uppercase_pattern = re.compile(r"[A-Z]")
        self.lowercase_pattern = re.compile(r"[a-z]")
        self.digit_pattern = re.compile(r"\d")
    
    def validate_password(self, password: str) -> bool:
        """
        Enforce configurable password policy.
        Default policy:
          - At least 8 characters
          - Contains at least one uppercase, one lowercase, one digit
        
        Args:
            password: Password string to validate
            
        Returns:
            bool: True if password meets policy requirements, False otherwise
        """
        if not password or not isinstance(password, str):
            return False
        
        try:
            # Check minimum length
            if len(password) < self.min_length:
                return False
            
            # Check uppercase requirement
            if self.require_uppercase and not self.uppercase_pattern.search(password):
                return False
            
            # Check lowercase requirement
            if self.require_lowercase and not self.lowercase_pattern.search(password):
                return False
            
            # Check digit requirement
            if self.require_digit and not self.digit_pattern.search(password):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_password_requirements(self) -> str:
        """
        Get human-readable password requirements.
        
        Returns:
            str: Description of password requirements
        """
        requirements = [f"At least {self.min_length} characters"]
        
        if self.require_uppercase:
            requirements.append("At least one uppercase letter")
        if self.require_lowercase:
            requirements.append("At least one lowercase letter")
        if self.require_digit:
            requirements.append("At least one digit")
        
        return ", ".join(requirements)


class ValidationService:
    """Main validation service combining all validators."""
    
    def __init__(self):
        self.phone_validator = PhoneValidator()
        self.aadhaar_validator = AadhaarValidator()
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator()
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number."""
        return self.phone_validator.validate_phone(phone)
    
    def validate_aadhaar(self, aadhaar: str) -> bool:
        """Validate Aadhaar number."""
        return self.aadhaar_validator.validate_aadhaar(aadhaar)
    
    def validate_email(self, email: str) -> bool:
        """Validate email address."""
        return self.email_validator.validate_email(email)
    
    def validate_password(self, password: str) -> bool:
        """Validate password."""
        return self.password_validator.validate_password(password)
    
    def get_password_requirements(self) -> str:
        """Get password requirements description."""
        return self.password_validator.get_password_requirements()
    
    def validate_user_profile(self, profile_data: dict) -> dict:
        """
        Validate complete user profile data.
        
        Args:
            profile_data: Dictionary containing user profile fields
            
        Returns:
            dict: Validation results with field-specific error messages
        """
        results = {
            'valid': True,
            'errors': {}
        }
        
        # Validate phone if provided
        if 'phone' in profile_data and profile_data['phone']:
            if not self.validate_phone(profile_data['phone']):
                results['valid'] = False
                results['errors']['phone'] = 'Phone number must be exactly 10 digits'
        
        # Validate Aadhaar if provided
        if 'aadhaar' in profile_data and profile_data['aadhaar']:
            if not self.validate_aadhaar(profile_data['aadhaar']):
                results['valid'] = False
                results['errors']['aadhaar'] = 'Aadhaar number must be exactly 12 digits'
        
        # Validate email if provided
        if 'email' in profile_data and profile_data['email']:
            if not self.validate_email(profile_data['email']):
                results['valid'] = False
                results['errors']['email'] = 'Invalid email format'
        
        # Validate password if provided
        if 'password' in profile_data and profile_data['password']:
            if not self.validate_password(profile_data['password']):
                results['valid'] = False
                results['errors']['password'] = f'Password must meet requirements: {self.get_password_requirements()}'
        
        return results


# Create service instance for use by public functions
_validation_service = ValidationService()


# Public interface functions - maintaining backward compatibility
def validate_phone(phone: str) -> bool:
    """
    Validate phone is exactly 10 digits (Indian format).
    Strips non-digit characters before checking length.
    """
    return _validation_service.validate_phone(phone)


def validate_aadhaar(aadhaar: str) -> bool:
    """
    Ensure Aadhaar is exactly 12 digits.
    Strips non-digit characters before checking length.
    """
    return _validation_service.validate_aadhaar(aadhaar)


def validate_email(email: str) -> bool:
    """
    Basic email format check.
    Returns True if matches pattern user@domain.tld
    """
    return _validation_service.validate_email(email)


def validate_password(password: str) -> bool:
    """
    Enforce a minimal password policy:
      - At least 8 characters
      - Contains at least one uppercase, one lowercase, one digit
    """
    return _validation_service.validate_password(password)
