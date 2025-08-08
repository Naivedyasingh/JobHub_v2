# utils/jobs.py

import streamlit as st
from db.models import JobPosting, JobDAO

class JobOfferService:
    """Service for handling job offer operations."""
    
    @staticmethod
    def get_job_offers():
        """Get job offers using the offers utility."""
        from utils.offers import get_job_offers as get_offers
        return get_offers()

class JobDataValidator:
    """Handles validation of job posting data."""
    
    @staticmethod
    def validate_employer_id(employer_id):
        """Validate employer ID."""
        return isinstance(employer_id, int) and employer_id > 0
    
    @staticmethod
    def validate_job_data(job_data):
        """Validate job posting data."""
        if not isinstance(job_data, dict) or not job_data:
            return False
        
        required_fields = ['title', 'location', 'salary', 'job_type', 'description']
        return all(field in job_data and job_data[field] for field in required_fields)

class JobDataProcessor:
    """Handles processing and preparation of job data."""
    
    @staticmethod
    def prepare_job_payload(employer_id, job_data):
        """Prepare job data payload for database insertion."""
        payload = job_data.copy()
        payload['user_id'] = employer_id
        return payload
    
    @staticmethod
    def sanitize_job_data(job_data):
        """Sanitize job data by trimming strings."""
        sanitized = {}
        for key, value in job_data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized

class SessionStateManager:
    """Handles Streamlit session state operations."""
    
    @staticmethod
    def update_current_user(employer_id, job_dao):
        """Update current user in session state."""
        try:
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'current_user'):
                updated_user = job_dao.get_user_by_id(employer_id)
                if updated_user:
                    st.session_state.current_user = updated_user
                    return True
        except Exception as e:
            print(f"Error updating session state: {e}")
        return False

class JobPostingService:
    """Main service for job posting operations."""
    
    def __init__(self):
        self.validator = JobDataValidator()
        self.processor = JobDataProcessor()
        self.session_manager = SessionStateManager()
    
    def add_job_posting(self, employer_id, job_data):
        """
        Add a new job posting for employer using JobDAO.
        
        Args:
            employer_id: ID of the employer posting the job
            job_data: Dictionary containing job posting data
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate inputs
        if not self.validator.validate_employer_id(employer_id):
            return False
        
        if not self.validator.validate_job_data(job_data):
            return False
        
        try:
            # Sanitize and prepare job data
            sanitized_data = self.processor.sanitize_job_data(job_data)
            payload = self.processor.prepare_job_payload(employer_id, sanitized_data)
            
            # Create JobDAO instance and insert job
            job_dao = JobDAO()
            # ← ONLY CHANGE: Fixed the method call to pass both arguments
            result = job_dao.insert_job(employer_id, payload)
            
            if result:
                # Update session state with current user
                self.session_manager.update_current_user(employer_id, job_dao)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error adding job posting: {e}")
            return False

class JobUtilityService:
    """Main utility service combining all job-related operations."""
    
    def __init__(self):
        self.offer_service = JobOfferService()
        self.posting_service = JobPostingService()
    
    def get_offers(self):
        """Get job offers."""
        return self.offer_service.get_job_offers()
    
    def add_posting(self, employer_id, job_data):
        """Add job posting."""
        return self.posting_service.add_job_posting(employer_id, job_data)

# Create service instance for use by public functions
_job_service = JobUtilityService()

# Public interface functions - maintaining backward compatibility
def get_job_offers():
    """Get job offers using the offers utility."""
    return _job_service.get_offers()

def add_job_posting(employer_id, job_data):
    """Add a new job posting for employer using JobDAO"""
    return _job_service.add_posting(employer_id, job_data)
