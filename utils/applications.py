# utils/applications.py

from datetime import datetime
from db.models import Application, JobPosting
import streamlit as st

class ApplicationDataValidator:
    """Handles validation of application data."""
    
    @staticmethod
    def validate_application_data(data):
        """Validate application data before saving."""
        required_fields = ['job_id', 'employer_id', 'applicant_id']
        return all(field in data and data[field] is not None for field in required_fields)
    
    @staticmethod
    def validate_status_update(app_id, status):
        """Validate status update parameters."""
        valid_statuses = ['pending', 'accepted', 'rejected']
        return isinstance(app_id, int) and app_id > 0 and status in valid_statuses
    
    @staticmethod
    def validate_job_update_params(app_id, job_id, employer_id):
        """Validate parameters for job status updates."""
        return (isinstance(app_id, int) and app_id > 0 and 
                isinstance(job_id, int) and job_id > 0 and
                employer_id is not None)

class ApplicationDataProcessor:
    """Handles processing and preparation of application data."""
    
    @staticmethod
    def prepare_application_data(data):
        """Prepare application data with required defaults."""
        processed_data = data.copy()
        processed_data.setdefault("status", "pending")
        processed_data.setdefault("applied_date", datetime.now())
        return processed_data
    
    @staticmethod
    def sanitize_application_data(data):
        """Sanitize application data to ensure data integrity."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized

class JobStatusManager:
    """Handles job status updates when applications are accepted."""
    
    def __init__(self):
        self.job_model = JobPosting()
    
    def update_job_on_acceptance(self, job_id, employer_id):
        """Update job hiring status when an application is accepted."""
        try:
            # Get current job data
            job = self.job_model.get_by_id(job_id)
            if not job or str(job.get('user_id')) != str(employer_id):
                return False, "Job not found or unauthorized"
            
            # Calculate new hired count
            current_hired = job.get('hired_count', 0)
            new_hired_count = current_hired + 1
            required_candidates = job.get('required_candidates', 1)
            
            # Prepare update data
            update_data = {'hired_count': new_hired_count}
            
            # Auto-close job if all positions filled
            if new_hired_count >= required_candidates:
                update_data.update({
                    'is_closed': True,
                    'auto_closed': True,
                    'closed_date': datetime.now()
                })
            
            # Update job in database
            job_updated = self.job_model.update(job_id, update_data)
            
            if job_updated:
                if new_hired_count >= required_candidates:
                    return True, f"Job post automatically closed (all {required_candidates} positions filled)."
                else:
                    remaining = required_candidates - new_hired_count
                    return True, f"{remaining} more position(s) needed."
            else:
                return False, "Failed to update job status"
                
        except Exception as e:
            return False, f"Error updating job status: {str(e)}"

class ApplicationRepository:
    """Handles database operations for applications."""
    
    def __init__(self):
        self.application_model = Application()
    
    def get_all_applications(self):
        """Return every row from the applications table."""
        return self.application_model.stream_all()
    
    def create_application(self, data):
        """Insert a new application and return the ID."""
        return self.application_model.create(data)
    
    def update_application_status(self, app_id, status, message=""):
        """Update application status and return success indicator."""
        return self.application_model.update_status(app_id, status, message)
    
    def get_application_by_id(self, app_id):
        """Get application by ID."""
        return self.application_model.get_by_id(app_id)

class CongratsNotificationManager:
    """Handles congratulations notification clearing for dashboard popup."""
    
    @staticmethod
    def clear_congrats_flag_for_user(applicant_id):
        """Clear congratulations flag so popup shows on next dashboard visit."""
        try:
            if 'st' in globals():  # Check if streamlit is available
                popup_key = f"congrats_shown_{datetime.now().strftime('%Y-%m-%d')}"
                # Clear the flag so the popup can show again
                if popup_key in st.session_state:
                    del st.session_state[popup_key]
                
                # Also clear any user-specific flags
                user_popup_key = f"congrats_shown_{applicant_id}_{datetime.now().strftime('%Y-%m-%d')}"
                if user_popup_key in st.session_state:
                    del st.session_state[user_popup_key]
        except Exception as e:
            print(f"[DEBUG] Could not clear congrats flag: {e}")
            # Non-critical error, continue silently

class ApplicationService:
    """Main service class for application operations."""
    
    def __init__(self):
        self.repository = ApplicationRepository()
        self.validator = ApplicationDataValidator()
        self.processor = ApplicationDataProcessor()
        self.job_manager = JobStatusManager()
        self.congrats_manager = CongratsNotificationManager()  # ← NEW
    
    def get_all_applications(self):
        """Get all applications from database."""
        return self.repository.get_all_applications()
    
    def save_application(self, data):
        """
        Save a new application with validation and data processing.
        
        • Validates required fields
        • Guarantees "status" (defaults to pending)
        • Guarantees "applied_date" (current timestamp)
        • Sanitizes input data
        """
        # Validate input data
        if not self.validator.validate_application_data(data):
            return False
        
        # Process and sanitize data
        sanitized_data = self.processor.sanitize_application_data(data)
        processed_data = self.processor.prepare_application_data(sanitized_data)
        
        # Save to database
        result = self.repository.create_application(processed_data)
        return result > 0
    
    def update_status(self, app_id, status, message=""):
        """
        Update application status with validation.
        
        Args:
            app_id: Application ID
            status: New status (pending, accepted, rejected)
            message: Optional status update message
        """
        # Validate parameters
        if not self.validator.validate_status_update(app_id, status):
            return False
        
        # Update status
        result = self.repository.update_application_status(app_id, status, message)
        return result > 0
    
    def accept_application(self, app_id, job_id=None, employer_id=None):
        """
        Accept an application and update job hiring status.
        
        Args:
            app_id: Application ID
            job_id: Job ID (optional - will be fetched if not provided)
            employer_id: Employer ID (optional - will be fetched if not provided)
        """
        try:
            # Get application details if job_id not provided
            if not job_id or not employer_id:
                app = self.repository.get_application_by_id(app_id)
                if not app:
                    return False, "Application not found"
                job_id = job_id or app.get('job_id')
                employer_id = employer_id or app.get('employer_id')
            
            # Validate parameters
            if not self.validator.validate_job_update_params(app_id, job_id, employer_id):
                return False, "Invalid parameters"
            
            # 1. Update application status
            app_success = self.update_status(app_id, "accepted")
            if not app_success:
                return False, "Failed to update application status"
            
            # 2. Update job hiring status
            job_success, job_message = self.job_manager.update_job_on_acceptance(job_id, employer_id)
            if not job_success:
                return False, f"Application accepted but {job_message}"
            
            # 3. Clear congratulations flag so job seeker gets popup ← NEW
            app = self.repository.get_application_by_id(app_id)
            if app:
                applicant_id = app.get('applicant_id')
                if applicant_id:
                    self.congrats_manager.clear_congrats_flag_for_user(applicant_id)
            
            return True, f"Application accepted! {job_message}"
            
        except Exception as e:
            return False, f"Error accepting application: {str(e)}"
    
    def reject_application(self, app_id):
        """Reject an application."""
        try:
            success = self.update_status(app_id, "rejected")
            return success, "Application rejected successfully" if success else "Failed to reject application"
        except Exception as e:
            return False, f"Error rejecting application: {str(e)}"

# Create service instance for use by public functions
_application_service = ApplicationService()

# ------------------ public helpers ------------------------------

def get_job_applications():
    """Return every row from the applications table."""
    return _application_service.get_all_applications()

def save_job_application(data: dict) -> bool:
    """
    Insert a new application.

    • guarantees "status" (defaults to pending)
    • guarantees "applied_date" (current timestamp)
    """
    return _application_service.save_application(data)

def update_application_status(app_id: int, status: str, message: str = "") -> bool:
    """Update application status."""
    return _application_service.update_status(app_id, status, message)

def accept_application(app_id: int, job_id: int = None, employer_id = None):
    """Accept an application with job status update."""
    return _application_service.accept_application(app_id, job_id, employer_id)

def reject_application(app_id: int):
    """Reject an application."""
    return _application_service.reject_application(app_id)
