import streamlit as st
from db.models import User
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class BaseService(ABC):
    """Abstract base class defining service contracts for all services."""
    
    @abstractmethod
    def validate(self, data):
        pass
    
    @abstractmethod
    def process(self, data):
        pass
    
    @abstractmethod
    def get_service_name(self):
        pass

class BaseAuthService(ABC):
    """Abstract authentication service interface."""
    
    @abstractmethod
    def authenticate_user(self, identifier, password, role):
        pass
    
    @abstractmethod
    def validate_credentials(self, identifier, password, role):
        pass

class BaseRepositoryInterface(ABC):
    """Abstract repository interface for data access."""
    
    @abstractmethod
    def create(self, data):
        pass
    
    @abstractmethod
    def read(self, identifier):
        pass
    
    @abstractmethod
    def update(self, identifier, data):
        pass
    
    @abstractmethod
    def delete(self, identifier):
        pass


class AuthenticationValidator:
    """Handles validation for authentication operations."""

    @staticmethod
    def validate_credentials(identifier, password, role):
        if not identifier or not password or not role:
            return False
        if role not in ['job', 'hire']:
            return False
        return True

    @staticmethod
    def validate_profile_data(updates):
        if not isinstance(updates, dict) or not updates:
            return False
        return True

class UserMatcher:
    """Handles user matching logic for authentication."""

    @staticmethod
    def match_user_by_identifier(users, identifier):
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
            'experience', 'job_types', 'expected_salary', 'availability','pincode'
        ]
        self.employer_fields = [
            'name', 'phone', 'email', 'company_name', 'company_type',
            'address', 'city', 'business_description'
        ]

    def get_required_fields(self, role):
        if role == 'job':
            return self.job_seeker_fields
        else:  
            return self.employer_fields

    def calculate_completion(self, user):
        required_fields = self.get_required_fields(user['role'])
        completed = sum(1 for field in required_fields if user.get(field))
        return int((completed / len(required_fields)) * 100)

class UserRepository(BaseRepositoryInterface):
    """Handles database operations for users - implements abstract repository."""

    def __init__(self):
        self.user_model = User()

    def create(self, data):
        return self.user_model.create(data)
    
    def read(self, user_id):
        return self.user_model.get(user_id)
    
    def update(self, user_id, data):
        return self.user_model.update(user_id, data)
    
    def delete(self, user_id):
        pass

    def find_users_by_role_and_password(self, role, password):
        sql = "SELECT * FROM users WHERE role=%s AND password=%s"
        params = (role, password)
        with User.db.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def update_user(self, user_id, updates):
        return self.user_model.update(user_id, updates)

    def get_user(self, user_id):
        return self.user_model.get(user_id)

    def get_next_user_id(self, users):
        return max([u.get("id", 0) for u in users], default=0) + 1

class AuthenticationService(BaseAuthService, BaseService):
    """Main service class for authentication operations - implements abstract interfaces."""

    def __init__(self):
        self.repository = UserRepository()
        self.validator = AuthenticationValidator()
        self.matcher = UserMatcher()
        self.completion_calculator = ProfileCompletionCalculator()

    def validate(self, data):
        return self.validator.validate_credentials(
            data.get('identifier'), 
            data.get('password'), 
            data.get('role')
        )
    
    def process(self, data):
        return self.authenticate_user(
            data.get('identifier'), 
            data.get('password'), 
            data.get('role')
        )
    
    def get_service_name(self):
        return "AuthenticationService"

    def validate_credentials(self, identifier, password, role):
        return self.validator.validate_credentials(identifier, password, role)

    def authenticate_user(self, identifier, password, role):

        if not self.validator.validate_credentials(identifier, password, role):
            return None

        users = self.repository.find_users_by_role_and_password(role, password)
        if not users:
            return None

        return self.matcher.match_user_by_identifier(users, identifier)

    def calculate_profile_completion(self, user):
        return self.completion_calculator.calculate_completion(user)

    def update_user_profile(self, user_id, updates):

        if not self.validator.validate_profile_data(updates):
            return None

        rowcount = self.repository.update_user(user_id, updates)
        if rowcount > 0:
            return self.repository.get_user(user_id)
        return None

    def generate_next_user_id(self, users):
        return self.repository.get_next_user_id(users)

class UserIdGenerator:
    """Handles user ID generation logic."""

    @staticmethod
    def generate_next_id(users):
        return max([u.get("id", 0) for u in users], default=0) + 1

class SessionManager:
    """Handles Streamlit session state operations for authentication."""

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        return st.session_state.get('current_user', None)

    @staticmethod
    def set_current_user(user: Dict[str, Any]) -> None:
        st.session_state['current_user'] = user

    @staticmethod
    def clear_current_user() -> None:
        if 'current_user' in st.session_state:
            del st.session_state['current_user']

    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get('current_user') is not None

class AuthorizationService:
    """Handles authorization and access control."""

    @staticmethod
    def require_authentication() -> Optional[Dict[str, Any]]:
        user = SessionManager.get_current_user()
        if user is None:
            st.error("🔐 Please log in to access this page.")
            st.stop()
        return user

    @staticmethod
    def require_role(required_role: str) -> Optional[Dict[str, Any]]:
        user = AuthorizationService.require_authentication()
        
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
        user = SessionManager.get_current_user()
        return user.get('role') if user else None

    @staticmethod
    def is_employer() -> bool:
        return AuthorizationService.get_user_role() == 'hire'

    @staticmethod
    def is_job_seeker() -> bool:
        return AuthorizationService.get_user_role() == 'job'

_auth_service = AuthenticationService()
_id_generator = UserIdGenerator()
_session_manager = SessionManager()
_auth_service_instance = AuthorizationService()


def authenticate(identifier, pwd, role):
    return _auth_service.authenticate_user(identifier, pwd, role)

def next_user_id(users):
    return _id_generator.generate_next_id(users)

def calculate_profile_completion(user):
    return _auth_service.calculate_profile_completion(user)

def update_user_profile(user_id, updates):
    return _auth_service.update_user_profile(user_id, updates)

def get_current_user() -> Optional[Dict[str, Any]]:
    return _session_manager.get_current_user()

def set_current_user(user: Dict[str, Any]) -> None:
    return _session_manager.set_current_user(user)

def is_authenticated() -> bool:
    return _session_manager.is_authenticated()

def logout() -> None:
    return _session_manager.clear_current_user()

def require_authentication() -> Optional[Dict[str, Any]]:
    return _auth_service_instance.require_authentication()

def require_employer() -> Optional[Dict[str, Any]]:
    return _auth_service_instance.require_role('employer')

def require_job_seeker() -> Optional[Dict[str, Any]]:
    return _auth_service_instance.require_role('job_seeker')

def get_user_role() -> Optional[str]:
    return _auth_service_instance.get_user_role()

def is_employer() -> bool:
    return _auth_service_instance.is_employer()

def is_job_seeker() -> bool:
    return _auth_service_instance.is_job_seeker()

def get_user_by_credentials(email_or_phone: str, password: str) -> Optional[Dict[str, Any]]:

    user = authenticate(email_or_phone, password, 'job')
    if user:
        return user
  
    user = authenticate(email_or_phone, password, 'hire')
    return user
