# utils/offers.py

from datetime import datetime, timedelta
from db.models import JobOffer


class OfferDataValidator:
    """Handles validation of job offer data."""
    
    @staticmethod
    def validate_offer_data(offer_data):
        """Validate job offer data before saving."""
        if not isinstance(offer_data, dict) or not offer_data:
            return False
        
        required_fields = [
            'job_title', 'employer_id', 'job_seeker_id', 
            'salary_offered', 'location'
        ]
        
        # Check required fields exist and are not None/empty
        for field in required_fields:
            if field not in offer_data or not offer_data[field]:
                return False
        
        # Validate specific field types
        if not isinstance(offer_data['employer_id'], int) or offer_data['employer_id'] <= 0:
            return False
        
        if not isinstance(offer_data['job_seeker_id'], int) or offer_data['job_seeker_id'] <= 0:
            return False
        
        if not isinstance(offer_data['salary_offered'], (int, float)) or offer_data['salary_offered'] <= 0:
            return False
        
        return True
    
    @staticmethod
    def validate_offer_id(offer_id):
        """Validate offer ID."""
        return isinstance(offer_id, int) and offer_id > 0
    
    @staticmethod
    def validate_status(status):
        """Validate offer status."""
        valid_statuses = ['pending', 'accepted', 'rejected', 'expired']
        return isinstance(status, str) and status.lower() in valid_statuses


class OfferDataProcessor:
    """Handles processing and preparation of offer data."""
    
    @staticmethod
    def sanitize_offer_data(offer_data):
        """Sanitize offer data by trimming strings and ensuring data integrity."""
        sanitized = {}
        for key, value in offer_data.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
            elif isinstance(value, datetime):
                sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def add_default_fields(offer_data):
        """Add default fields to offer data if not present."""
        processed = offer_data.copy()
        
        # Set default status if not provided
        if 'status' not in processed:
            processed['status'] = 'pending'
        
        # Set offered_date to current datetime if not provided
        if 'offered_date' not in processed:
            processed['offered_date'] = datetime.now()
        
        # Set expiry date if not provided (24 hours from now)
        if 'expires_at' not in processed:
            processed['expires_at'] = datetime.now() + timedelta(hours=24)
        
        return processed


class OfferRepository:
    """Handles database operations for job offers."""
    
    def __init__(self):
        self.job_offer_model = JobOffer()
    
    def get_all_offers(self):
        """Get all job offers from database."""
        return list(self.job_offer_model.stream_all())
    
    def create_offer(self, offer_data):
        """Create new job offer in database."""
        return self.job_offer_model.create(offer_data)
    
    def update_offer_status(self, offer_id, status, response_message=""):
        """Update job offer status in database."""
        return self.job_offer_model.update_status(offer_id, status, response_message)


class OfferService:
    """Main service class for job offer operations."""
    
    def __init__(self):
        self.repository = OfferRepository()
        self.validator = OfferDataValidator()
        self.processor = OfferDataProcessor()
    
    def get_all_offers(self):
        """
        Get all job offers.
        
        Returns:
            list: List of job offers, empty list if error
        """
        try:
            return self.repository.get_all_offers()
        except Exception as e:
            print(f"Error fetching job offers: {e}")
            return []
    
    def save_offer(self, offer_data):
        """
        Save a job offer with validation and processing.
        
        Args:
            offer_data: Dictionary containing job offer data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate offer data
            if not self.validator.validate_offer_data(offer_data):
                return False
            
            # Sanitize and process data
            sanitized_data = self.processor.sanitize_offer_data(offer_data)
            processed_data = self.processor.add_default_fields(sanitized_data)
            
            # Save to database
            new_id = self.repository.create_offer(processed_data)
            return new_id is not None and new_id > 0
            
        except Exception as e:
            print(f"Error saving job offer: {e}")
            return False
    
    def update_status(self, offer_id, status, response_message=""):
        """
        Update job offer status with validation.
        
        Args:
            offer_id: ID of the offer to update
            status: New status for the offer
            response_message: Optional response message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not self.validator.validate_offer_id(offer_id):
                return False
            
            if not self.validator.validate_status(status):
                return False
            
            # Sanitize response message
            sanitized_message = response_message.strip() if isinstance(response_message, str) else ""
            
            # Update in database
            rows_affected = self.repository.update_offer_status(offer_id, status, sanitized_message)
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error updating offer status: {e}")
            return False


# Create service instance for use by public functions
_offer_service = OfferService()


# Public interface functions - maintaining backward compatibility
def get_job_offers():
    """Get all job offers using ORM model."""
    return _offer_service.get_all_offers()


def save_job_offer(offer_data):
    """Save a job offer from employer to job seeker using ORM create method."""
    return _offer_service.save_offer(offer_data)


def update_offer_status(offer_id, status, response_message=""):
    """Update job offer status using ORM update_status method."""
    return _offer_service.update_status(offer_id, status, response_message)
