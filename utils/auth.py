# utils/auth.py

import streamlit as st
from db.models import User
from datetime import datetime
from typing import Optional, Dict, Any

class AuthenticationValidator:
    """Handles validation for authentication operations."""
    
    @staticmethod
    def validate_credentials(identifier, password, role):
        """Validate authentication credentials."""
        if not identifier or not password or not role:
            return False
        if role not in ['job', 'hire']:
            return False
        return True
    
    @staticmethod
    def validate_profile_data(updates):
        """Validate profile update data."""
        if not isinstance(updates, dict) or not updates:
            return False
        return True

class UserMatcher:
    """Handles user matching logic for authentication."""
    
    @staticmethod
    def match_user_by_identifier(users, identifier):
        """Match user by identifier (name or phone)."""
        identifier_lower = identifier.lower()
        for user in users:
            user_name = user.get("name", "").lower()
            user_phone = user.get("phone", "")
            if identifier_lower == user_name or identifier == user_phone:
                return user
        return None

class ProfileCompletionCalculator:
    """Handles profile completion percentage calculations."""
    
    def __init__(self):
        self.job_seeker_fields = [
            'name', 'phone', 'email', 'aadhaar', 'address', 'city', 
            'experience', 'job_types', 'expected_salary', 'availability'
        ]
        self.employer_fields = [
            'name', 'phone', 'email', 'company_name', 'company_type', 
            'address', 'city', 'business_description'
        ]
    
    def get_required_fields(self, role):
        """Get required fields based on user role."""
        if role == 'job':
            return self.job_seeker_fields
        else:  # employer
            return self.employer_fields
    
    def calculate_completion(self, user):
        """Calculate profile completion percentage."""
        required_fields = self.get_required_fields(user['role'])
        completed = sum(1 for field in required_fields if user.get(field))
        return int((completed / len(required_fields)) * 100)

class UserRepository:
    """Handles database operations for users."""
    
    def __init__(self):
        self.user_model = User()
    
    def find_users_by_role_and_password(self, role, password):
        """Find users by role and password."""
        sql = "SELECT * FROM users WHERE role=%s AND password=%s"
        params = (role, password)
        with User.db.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    
    def update_user(self, user_id, updates):
        """Update user profile and return row count."""
        return self.user_model.update(user_id, updates)
    
    def get_user(self, user_id):
        """Get user by ID."""
        return self.user_model.get(user_id)
    
    def get_next_user_id(self, users):
        """Generate next available user ID."""
        return max([u.get("id", 0) for u in users], default=0) + 1

class AuthenticationService:
    """Main service class for authentication operations."""
    
    def __init__(self):
        self.repository = UserRepository()
        self.validator = AuthenticationValidator()
        self.matcher = UserMatcher()
        self.completion_calculator = ProfileCompletionCalculator()
    
    def authenticate_user(self, identifier, password, role):
        """
        Authenticate a user using the database.
        Returns the user dict if authenticated, else None.
        """
        # Validate input
        if not self.validator.validate_credentials(identifier, password, role):
            return None
        
        # Find users with matching role and password
        users = self.repository.find_users_by_role_and_password(role, password)
        if not users:
            return None
        
        # Match user by identifier
        return self.matcher.match_user_by_identifier(users, identifier)
    
    def calculate_profile_completion(self, user):
        """Calculate profile completion percentage."""
        return self.completion_calculator.calculate_completion(user)
    
    def update_user_profile(self, user_id, updates):
        """
        Update user profile in the database.
        Returns updated user dict if successful, else None.
        """
        # Validate input
        if not self.validator.validate_profile_data(updates):
            return None
        
        # Update user in database
        rowcount = self.repository.update_user(user_id, updates)
        if rowcount > 0:
            return self.repository.get_user(user_id)
        return None
    
    def generate_next_user_id(self, users):
        """Generate next available user ID."""
        return self.repository.get_next_user_id(users)

class UserIdGenerator:
    """Handles user ID generation logic."""
    
    @staticmethod
    def generate_next_id(users):
        """Generate next available user ID from list of users."""
        return max([u.get("id", 0) for u in users], default=0) + 1

# ============= SESSION MANAGEMENT CLASSES =============

class SessionManager:
    """Handles Streamlit session state operations for authentication."""
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get the current authenticated user from session state."""
        return st.session_state.get('current_user', None)
    
    @staticmethod
    def set_current_user(user: Dict[str, Any]) -> None:
        """Set the current user in session state."""
        st.session_state['current_user'] = user
    
    @staticmethod
    def clear_current_user() -> None:
        """Clear current user from session state (logout)."""
        if 'current_user' in st.session_state:
            del st.session_state['current_user']
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if a user is currently authenticated."""
        return st.session_state.get('current_user') is not None

class AuthorizationService:
    """Handles authorization and access control."""
    
    @staticmethod
    def require_authentication() -> Optional[Dict[str, Any]]:
        """Require authentication and return current user or stop execution."""
        user = SessionManager.get_current_user()
        if user is None:
            st.error("🔐 Please log in to access this page.")
            st.stop()
        return user
    
    @staticmethod
    def require_role(required_role: str) -> Optional[Dict[str, Any]]:
        """Require specific role and return user or stop execution."""
        user = AuthorizationService.require_authentication()
        
        # Convert role names for compatibility
        user_role = user.get('role')
        if required_role == 'employer' and user_role != 'hire':
            st.error("🚫 Only employers can access this page.")
            st.stop()
        elif required_role == 'job_seeker' and user_role != 'job':
            st.error("🚫 Only job seekers can access this page.")
            st.stop()
        
        return user
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get the current user's role."""
        user = SessionManager.get_current_user()
        return user.get('role') if user else None
    
    @staticmethod
    def is_employer() -> bool:
        """Check if current user is an employer."""
        return AuthorizationService.get_user_role() == 'hire'
    
    @staticmethod
    def is_job_seeker() -> bool:
        """Check if current user is a job seeker."""
        return AuthorizationService.get_user_role() == 'job'

# Create service instances
_auth_service = AuthenticationService()
_id_generator = UserIdGenerator()
_session_manager = SessionManager()
_auth_service_instance = AuthorizationService()

# ============= PUBLIC API FUNCTIONS =============

# ---------- Authentication & Profile Helpers ----------

def authenticate(identifier, pwd, role):
    """
    Authenticate a user using the database.
    Returns the user dict if authenticated, else None.
    """
    return _auth_service.authenticate_user(identifier, pwd, role)

def next_user_id(users):
    """Generate next available user ID."""
    return _id_generator.generate_next_id(users)

def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    return _auth_service.calculate_profile_completion(user)

def update_user_profile(user_id, updates):
    """
    Update user profile in the database.
    Returns updated user dict if successful, else None.
    """
    return _auth_service.update_user_profile(user_id, updates)

# ---------- Session Management Functions ----------

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from session state.
    
    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    return _session_manager.get_current_user()

def set_current_user(user: Dict[str, Any]) -> None:
    """
    Set the current user in session state.
    
    Args:
        user (Dict): User data to store in session
    """
    return _session_manager.set_current_user(user)

def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.
    
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    return _session_manager.is_authenticated()

def logout() -> None:
    """Clear current user from session state (logout)."""
    return _session_manager.clear_current_user()

def require_authentication() -> Optional[Dict[str, Any]]:
    """
    Require authentication and return current user or redirect to login.
    
    Returns:
        Optional[Dict]: Current user if authenticated, None if not
    """
    return _auth_service_instance.require_authentication()

def require_employer() -> Optional[Dict[str, Any]]:
    """
    Require employer role and return current user.
    
    Returns:
        Optional[Dict]: Current user if employer, stops execution if not
    """
    return _auth_service_instance.require_role('employer')

def require_job_seeker() -> Optional[Dict[str, Any]]:
    """
    Require job seeker role and return current user.
    
    Returns:
        Optional[Dict]: Current user if job seeker, stops execution if not
    """
    return _auth_service_instance.require_role('job_seeker')

def get_user_role() -> Optional[str]:
    """
    Get the current user's role.
    
    Returns:
        Optional[str]: User role ('hire', 'job') or None
    """
    return _auth_service_instance.get_user_role()

def is_employer() -> bool:
    """
    Check if current user is an employer.
    
    Returns:
        bool: True if user is employer, False otherwise
    """
    return _auth_service_instance.is_employer()

def is_job_seeker() -> bool:
    """
    Check if current user is a job seeker.
    
    Returns:
        bool: True if user is job seeker, False otherwise
    """
    return _auth_service_instance.is_job_seeker()

# ---------- Utility Functions ----------

def get_user_by_credentials(email_or_phone: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Get user by login credentials (compatibility function).
    
    Args:
        email_or_phone (str): Email or phone identifier
        password (str): Password
        
    Returns:
        Optional[Dict]: User data if found, None otherwise
    """
    # Try job seeker first
    user = authenticate(email_or_phone, password, 'job')
    if user:
        return user
    
    # Try employer
    user = authenticate(email_or_phone, password, 'hire')
    return user
