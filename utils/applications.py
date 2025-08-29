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
            job = self.job_model.get_by_id(job_id)
            if not job or str(job.get('user_id')) != str(employer_id):
                return False, "Job not found or unauthorized"
            
            current_hired = job.get('hired_count', 0)
            new_hired_count = current_hired + 1
            required_candidates = job.get('required_candidates', 1)
            
            update_data = {'hired_count': new_hired_count}
            
            if new_hired_count >= required_candidates:
                update_data.update({
                    'is_closed': True,
                    'auto_closed': True,
                    'closed_date': datetime.now()
                })
            
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
        return self.application_model.stream_all()
    
    def create_application(self, data):
        return self.application_model.create(data)
    
    def update_application_status(self, app_id, status, message=""):
        return self.application_model.update_status(app_id, status, message)
    
    def get_application_by_id(self, app_id):
        return self.application_model.get_by_id(app_id)

class CongratsNotificationManager:
    """Handles congratulations notification clearing for dashboard popup."""
    
    @staticmethod
    def clear_congrats_flag_for_user(applicant_id):
        """Clear congratulations flag so popup shows on next dashboard visit."""
        try:
            if 'st' in globals():  
                popup_key = f"congrats_shown_{datetime.now().strftime('%Y-%m-%d')}"

                if popup_key in st.session_state:
                    del st.session_state[popup_key]

                user_popup_key = f"congrats_shown_{applicant_id}_{datetime.now().strftime('%Y-%m-%d')}"
                if user_popup_key in st.session_state:
                    del st.session_state[user_popup_key]
        except Exception as e:
            print(f"[DEBUG] Could not clear congrats flag: {e}")

class ApplicationService:
    """Main service class for application operations."""
    
    def __init__(self):
        self.repository = ApplicationRepository()
        self.validator = ApplicationDataValidator()
        self.processor = ApplicationDataProcessor()
        self.job_manager = JobStatusManager()
        self.congrats_manager = CongratsNotificationManager()  
    
    def get_all_applications(self):
        return self.repository.get_all_applications()
    
    def save_application(self, data):

        if not self.validator.validate_application_data(data):
            return False
        
        sanitized_data = self.processor.sanitize_application_data(data)
        processed_data = self.processor.prepare_application_data(sanitized_data)
        
        result = self.repository.create_application(processed_data)
        return result > 0
    
    def update_status(self, app_id, status, message=""):

        if not self.validator.validate_status_update(app_id, status):
            return False
        
        result = self.repository.update_application_status(app_id, status, message)
        return result > 0
    
    def accept_application(self, app_id, job_id=None, employer_id=None):

        try:
            if not job_id or not employer_id:
                app = self.repository.get_application_by_id(app_id)
                if not app:
                    return False, "Application not found"
                job_id = job_id or app.get('job_id')
                employer_id = employer_id or app.get('employer_id')
            
            if not self.validator.validate_job_update_params(app_id, job_id, employer_id):
                return False, "Invalid parameters"
            
            app_success = self.update_status(app_id, "accepted")
            if not app_success:
                return False, "Failed to update application status"
            
            job_success, job_message = self.job_manager.update_job_on_acceptance(job_id, employer_id)
            if not job_success:
                return False, f"Application accepted but {job_message}"
            
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

_application_service = ApplicationService()


def get_job_applications():
    return _application_service.get_all_applications()

def save_job_application(data: dict) -> bool:
    return _application_service.save_application(data)

def update_application_status(app_id: int, status: str, message: str = "") -> bool:
    return _application_service.update_status(app_id, status, message)

def accept_application(app_id: int, job_id: int = None, employer_id = None):
    return _application_service.accept_application(app_id, job_id, employer_id)

def reject_application(app_id: int):
    return _application_service.reject_application(app_id)
