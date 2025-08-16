# # utils/jobs.py
# import json
# from db.models import DatabaseManager
# from mysql.connector import Error
# from mysql.connector import connect


# class JobDataValidator:
#     """Handles validation of job posting data."""
    
#     @staticmethod
#     def validate_job_payload(payload):
#         """Validate job posting payload."""
#         required_fields = [
#             'user_id', 'title', 'location', 'salary', 'job_type', 
#             'experience', 'working_hours', 'urgency', 'contract_type', 
#             'description', 'requirements', 'benefits'
#         ]
        
#         if not isinstance(payload, dict):
#             return False
        
#         # Check required fields
#         for field in required_fields:
#             if field not in payload or payload[field] is None:
#                 return False
        
#         # Validate specific field types
#         if not isinstance(payload['user_id'], int) or payload['user_id'] <= 0:
#             return False
        
#         if not isinstance(payload['salary'], (int, float)) or payload['salary'] <= 0:
#             return False
        
#         return True
    
#     @staticmethod
#     def validate_job_id(job_id):
#         """Validate job ID."""
#         return isinstance(job_id, int) and job_id > 0
    
#     @staticmethod
#     def validate_user_id(user_id):
#         """Validate user ID."""
#         return isinstance(user_id, int) and user_id > 0
    
#     @staticmethod
#     def validate_updates(updates):
#         """Validate update data."""
#         if not isinstance(updates, dict) or not updates:
#             return False
        
#         # Ensure no attempts to update protected fields
#         protected_fields = ['id', 'posted_date', 'user_id']
#         for field in protected_fields:
#             if field in updates:
#                 return False
        
#         return True


# class JobDataProcessor:
#     """Handles processing and sanitization of job data."""
    
#     @staticmethod
#     def sanitize_payload(payload):
#         """Sanitize job payload data."""
#         sanitized = {}
#         for key, value in payload.items():
#             if isinstance(value, str):
#                 sanitized[key] = value.strip()
#             else:
#                 sanitized[key] = value
#         return sanitized
    
#     @staticmethod
#     def prepare_insert_params(payload):
#         """Prepare parameters for job insertion."""
#         return (
#             payload['user_id'], payload['title'], payload['location'], 
#             payload['salary'], payload['job_type'], payload['experience'], 
#             payload['working_hours'], payload['urgency'], payload['contract_type'], 
#             payload['description'], payload['requirements'], payload['benefits']
#         )
    
#     @staticmethod
#     def prepare_update_query(updates):
#         """Prepare update query components."""
#         assignments = ", ".join(f"{k}=%s" for k in updates)
#         params = tuple(updates.values())
#         return assignments, params


# class JobRepository:
#     """Handles database operations for job postings."""
    
#     def __init__(self, db_manager: DatabaseManager):
#         self.db = db_manager
    
#     def insert_job_posting(self, params):
#         """Insert new job posting into database."""
#         query = """
#         INSERT INTO job_postings 
#         (user_id, title, location, salary, job_type, experience, working_hours, 
#          urgency, contract_type, description, requirements, benefits, posted_date, status, applications_count) 
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),'active',0)
#         """
#         with self.db.cursor() as cur:
#             cur.execute(query, params)
#             return cur.lastrowid
    
#     def fetch_jobs_by_user(self, user_id):
#         """Fetch all jobs for a specific user."""
#         with self.db.cursor() as cur:
#             cur.execute("SELECT * FROM job_postings WHERE user_id=%s", (user_id,))
#             return cur.fetchall()
    
#     def fetch_job_by_id(self, job_id):
#         """Fetch single job by ID."""
#         with self.db.cursor() as cur:
#             cur.execute("SELECT * FROM job_postings WHERE id=%s", (job_id,))
#             return cur.fetchone()
    
#     def update_job_posting(self, job_id, assignments, params):
#         """Update job posting in database."""
#         full_params = params + (job_id,)
#         with self.db.cursor() as cur:
#             cur.execute(f"UPDATE job_postings SET {assignments} WHERE id=%s", full_params)
#             return cur.rowcount
    
#     def delete_job_posting(self, job_id):
#         """Delete job posting from database."""
#         with self.db.cursor() as cur:
#             cur.execute("DELETE FROM job_postings WHERE id=%s", (job_id,))
#             return cur.rowcount


# class JobService:
#     """Main service class for job posting operations."""
    
#     def __init__(self, db_manager: DatabaseManager):
#         self.repository = JobRepository(db_manager)
#         self.validator = JobDataValidator()
#         self.processor = JobDataProcessor()
    
#     def create_job_posting(self, payload):
#         """
#         Create a new job posting with validation and processing.
#         Returns job ID if successful, 0 if failed.
#         """
#         # Validate payload
#         if not self.validator.validate_job_payload(payload):
#             return 0
        
#         # Sanitize data
#         sanitized_payload = self.processor.sanitize_payload(payload)
        
#         # Prepare parameters
#         params = self.processor.prepare_insert_params(sanitized_payload)
        
#         # Insert into database
#         try:
#             return self.repository.insert_job_posting(params)
#         except Exception as e:
#             print(f"Error creating job posting: {e}")
#             return 0
    
#     def get_user_jobs(self, user_id):
#         """
#         Get all job postings for a user.
#         Returns list of jobs or empty list if error.
#         """
#         if not self.validator.validate_user_id(user_id):
#             return []
        
#         try:
#             return self.repository.fetch_jobs_by_user(user_id)
#         except Exception as e:
#             print(f"Error fetching user jobs: {e}")
#             return []
    
#     def get_job_by_id(self, job_id):
#         """
#         Get a specific job posting by ID.
#         Returns job dict or None if not found/error.
#         """
#         if not self.validator.validate_job_id(job_id):
#             return None
        
#         try:
#             return self.repository.fetch_job_by_id(job_id)
#         except Exception as e:
#             print(f"Error fetching job: {e}")
#             return None
    
#     def update_job_posting(self, job_id, updates):
#         """
#         Update a job posting with validation.
#         Returns True if successful, False otherwise.
#         """
#         # Validate inputs
#         if not self.validator.validate_job_id(job_id) or not self.validator.validate_updates(updates):
#             return False
        
#         # Sanitize updates
#         sanitized_updates = self.processor.sanitize_payload(updates)
        
#         # Prepare query components
#         assignments, params = self.processor.prepare_update_query(sanitized_updates)
        
#         # Update in database
#         try:
#             rowcount = self.repository.update_job_posting(job_id, assignments, params)
#             return rowcount > 0
#         except Exception as e:
#             print(f"Error updating job: {e}")
#             return False
    
#     def delete_job_posting(self, job_id):
#         """
#         Delete a job posting.
#         Returns True if successful, False otherwise.
#         """
#         if not self.validator.validate_job_id(job_id):
#             return False
        
#         try:
#             rowcount = self.repository.delete_job_posting(job_id)
#             return rowcount > 0
#         except Exception as e:
#             print(f"Error deleting job: {e}")
#             return False


# # Initialize with existing DatabaseManager
# class JobDAO:
#     """Legacy JobDAO class - maintained for backward compatibility."""
    
#     def __init__(self, db_manager: DatabaseManager):
#         self.db = db_manager
#         self.service = JobService(db_manager)

#     def insert_job(self, payload: dict) -> int:
#         """Insert job posting - delegates to service layer."""
#         return self.service.create_job_posting(payload)

#     def fetch_all_jobs(self, user_id: int) -> list:
#         """Fetch all jobs for user - delegates to service layer."""
#         return self.service.get_user_jobs(user_id)

#     def fetch_job(self, job_id: int) -> dict:
#         """Fetch single job - delegates to service layer."""
#         return self.service.get_job_by_id(job_id)

#     def update_job(self, job_id: int, updates: dict) -> bool:
#         """Update job - delegates to service layer."""
#         return self.service.update_job_posting(job_id, updates)

#     def delete_job(self, job_id: int) -> bool:
#         """Delete job - delegates to service layer."""
#         return self.service.delete_job_posting(job_id)


# # Public interface functions for backward compatibility
# def add_job_posting(user_id: int, job_data: dict) -> bool:
#     """
#     Public function to add a job posting.
#     Maintains backward compatibility with existing code.
#     """
#     from db.models import DatabaseManager
#     db_manager = DatabaseManager()
#     service = JobService(db_manager)
    
#     # Add user_id to job_data for processing
#     payload = job_data.copy()
#     payload['user_id'] = user_id
    
#     result = service.create_job_posting(payload)
#     return result > 0
