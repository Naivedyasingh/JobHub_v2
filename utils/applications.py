# utils/applications.py
from datetime import datetime
from db.models import Application


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


class ApplicationService:
    """Main service class for application operations."""
    
    def __init__(self):
        self.repository = ApplicationRepository()
        self.validator = ApplicationDataValidator()
        self.processor = ApplicationDataProcessor()
    
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
