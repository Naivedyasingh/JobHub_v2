import json
import pymysql
from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

def db_operation(func):
    """Decorator for database operations with logging"""
    def wrapper(self, *args, **kwargs):
        print(f"[DB] {func.__name__} args={args} kwargs={kwargs}")
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(f"[DB] Error in {func.__name__}: {e}")
            return None
    return wrapper

class DatabaseManager:
    def __init__(self, host: str, user: str, password: str, db: str, port: int = 3306):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': db,
            'port': port,
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': True
        }
        self._connection = None

    def get_connection(self):
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(**self.config)
        return self._connection

    def cursor(self):
        return self.get_connection().cursor()

    def init_schema(self, schema_file: str):
        """Initialize database schema from SQL file"""
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            with self.cursor() as cur:
                for statement in statements:
                    if statement:
                        cur.execute(statement)
            print(f"[DB] Schema initialized from {schema_file}")
        except Exception as e:
            print(f"[DB] Error initializing schema: {e}")

    def close(self):
        if self._connection:
            self._connection.close()

class BaseModel:
    db = None

    @classmethod
    def set_db(cls, database_manager):
        cls.db = database_manager

class User(BaseModel):
    @db_operation
    def create(self, data: dict) -> int:
        json_columns = ['job_types', 'availability', 'languages']
        processed_data = {}
        for key, value in data.items():
            if key in json_columns and isinstance(value, (list, dict)):
                processed_data[key] = json.dumps(value) if value else json.dumps([])
            else:
                processed_data[key] = value

        cols = ", ".join(processed_data.keys())
        vals = ", ".join(["%s"] * len(processed_data))
        sql = f"INSERT INTO users ({cols}) VALUES ({vals})"
        
        with self.db.cursor() as cur:
            cur.execute(sql, tuple(processed_data.values()))
            return cur.lastrowid

    @db_operation
    def get(self, user_id: int) -> dict:
        sql = "SELECT * FROM users WHERE id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (user_id,))
            result = cur.fetchone()
            if result:
                json_columns = ['job_types', 'availability', 'languages']
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return result

    @db_operation
    def get_by_id(self, user_id: int) -> dict:
        return self.get(user_id)

    @db_operation
    def get_by_email(self, email: str) -> dict:
        sql = "SELECT * FROM users WHERE email=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (email,))
            result = cur.fetchone()
            if result:
                json_columns = ['job_types', 'availability', 'languages']
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return result

    @db_operation
    def get_by_phone(self, phone: str) -> dict:
        sql = "SELECT * FROM users WHERE phone=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (phone,))
            result = cur.fetchone()
            if result:
                json_columns = ['job_types', 'availability', 'languages']
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return result

    @db_operation
    def update(self, user_id: int, updates: dict) -> int:
        json_columns = ['job_types', 'availability', 'languages']
        processed_updates = {}
        for key, value in updates.items():
            if key in json_columns and isinstance(value, (list, dict)):
                processed_updates[key] = json.dumps(value) if value else json.dumps([])
            else:
                processed_updates[key] = value

        assignments = ", ".join(f"{k}=%s" for k in processed_updates)
        sql = f"UPDATE users SET {assignments} WHERE id=%s"
        
        with self.db.cursor() as cur:
            cur.execute(sql, (*processed_updates.values(), user_id))
            return cur.rowcount

    @db_operation
    def stream_all(self):
        sql = "SELECT * FROM users"
        with self.db.cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
            json_columns = ['job_types', 'availability', 'languages']
            for result in results:
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return results

    @db_operation
    def list_job_seekers(self) -> list:
        sql = "SELECT * FROM users WHERE role='job_seeker'"
        with self.db.cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
            json_columns = ['job_types', 'availability', 'languages']
            for result in results:
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return results

    @db_operation
    def list_employers(self) -> list:
        sql = "SELECT * FROM users WHERE role='employer'"
        with self.db.cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
            json_columns = ['job_types', 'availability', 'languages']
            for result in results:
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []
                    elif col in result:
                        result[col] = []
            return results

class JobPosting(BaseModel):
    @db_operation
    def create(self, data: dict) -> int:
        cols = ", ".join(data.keys())
        vals = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO job_postings ({cols}) VALUES ({vals})"
        
        with self.db.cursor() as cur:
            cur.execute(sql, tuple(data.values()))
            return cur.lastrowid

    @db_operation
    def get_by_id(self, job_id: int) -> dict:
        sql = "SELECT * FROM job_postings WHERE id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (job_id,))
            return cur.fetchone()

    @db_operation
    def update(self, job_id: int, updates: dict) -> int:
        if not updates:
            return 0
        
        assignments = ", ".join(f"{k}=%s" for k in updates)
        sql = f"UPDATE job_postings SET {assignments} WHERE id=%s"
        
        with self.db.cursor() as cur:
            cur.execute(sql, (*updates.values(), job_id))
            return cur.rowcount

    @db_operation
    def list_all(self) -> list:
        """Get only open job postings available for job seekers (hide filled/closed positions)."""
        sql = """SELECT * FROM job_postings 
                WHERE status='active' 
                AND (is_closed = FALSE OR is_closed IS NULL)
                AND (hired_count < required_candidates OR hired_count IS NULL OR required_candidates IS NULL)
                ORDER BY posted_date DESC"""
        
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    @db_operation
    def list_by_user(self, user_id: int) -> list:
        """Get job postings by user ID (show all for employer dashboard)."""
        sql = "SELECT * FROM job_postings WHERE user_id=%s ORDER BY posted_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchall()

    @db_operation
    def search(self, filters: dict) -> list:
        """Search job postings with filters - only show open positions for job seekers."""
        conditions = [
            "status='active'",
            "(is_closed = FALSE OR is_closed IS NULL)",
            "(hired_count < required_candidates OR hired_count IS NULL OR required_candidates IS NULL)"
        ]
        params = []

        if filters.get('job_type'):
            conditions.append("job_type=%s")
            params.append(filters['job_type'])
        if filters.get('location'):
            conditions.append("location LIKE %s")
            params.append(f"%{filters['location']}%")
        if filters.get('salary_min'):
            conditions.append("salary >= %s")
            params.append(filters['salary_min'])
        if filters.get('salary_max'):
            conditions.append("salary <= %s")
            params.append(filters['salary_max'])
        if filters.get('experience'):
            conditions.append("experience=%s")
            params.append(filters['experience'])

        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM job_postings WHERE {where_clause} ORDER BY posted_date DESC"
        
        with self.db.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    @db_operation
    def list_all_with_status(self) -> list:
        """Get all job postings with their status."""
        sql = "SELECT * FROM job_postings ORDER BY posted_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

class Application(BaseModel):
    @db_operation
    def create(self, data: dict) -> int:
        cols = ", ".join(data.keys())
        vals = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO applications ({cols}) VALUES ({vals})"
        
        with self.db.cursor() as cur:
            cur.execute(sql, tuple(data.values()))
            return cur.lastrowid

    @db_operation
    def get_by_id(self, app_id: int) -> dict:
        sql = "SELECT * FROM applications WHERE id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (app_id,))
            return cur.fetchone()

    @db_operation
    def update_status(self, app_id: int, status: str, message: str = "") -> int:
        sql = """UPDATE applications 
                SET status=%s, response_message=%s, response_date=NOW() 
                WHERE id=%s"""
        
        with self.db.cursor() as cur:
            cur.execute(sql, (status, message, app_id))
            return cur.rowcount

    @db_operation
    def stream_all(self) -> list:
        sql = "SELECT * FROM applications ORDER BY applied_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    @db_operation
    def list_by_job(self, job_id: int) -> list:
        sql = "SELECT * FROM applications WHERE job_id=%s ORDER BY applied_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql, (job_id,))
            return cur.fetchall()

    @db_operation
    def list_by_applicant(self, applicant_id: int) -> list:
        sql = "SELECT * FROM applications WHERE applicant_id=%s ORDER BY applied_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql, (applicant_id,))
            return cur.fetchall()

    @db_operation
    def list_by_employer(self, employer_id: str) -> list:
        sql = "SELECT * FROM applications WHERE employer_id=%s ORDER BY applied_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql, (employer_id,))
            return cur.fetchall()

    @db_operation
    def check_existing(self, job_id: int, applicant_id: int) -> dict:
        sql = "SELECT * FROM applications WHERE job_id=%s AND applicant_id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (job_id, applicant_id))
            return cur.fetchone()

class JobOffer(BaseModel):
    @db_operation
    def create(self, data: dict) -> int:
        cols = ", ".join(data.keys())
        vals = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO job_offers ({cols}) VALUES ({vals})"
        
        with self.db.cursor() as cur:
            cur.execute(sql, tuple(data.values()))
            return cur.lastrowid

    @db_operation
    def update_status(self, offer_id: int, status: str, response_message: str = "") -> int:
        sql = """UPDATE job_offers 
                SET status=%s, response_message=%s, response_date=NOW() 
                WHERE id=%s"""
        
        with self.db.cursor() as cur:
            cur.execute(sql, (status, response_message, offer_id))
            return cur.rowcount

    @db_operation
    def stream_all(self) -> list:
        sql = "SELECT * FROM job_offers ORDER BY offered_date DESC"
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

class ApplicationGenerator:
    """Generator class for streaming applications efficiently by various criteria."""
    
    def __init__(self, application_model):
        self.model = application_model
    
    def stream_by_status(self, status):
        """Generator to yield applications by status."""
        all_apps = self.model.stream_all()
        for app in all_apps:
            if app.get('status') == status:
                yield app
    
    def stream_by_job_id(self, job_id):
        """Generator to yield applications for a specific job."""
        all_apps = self.model.stream_all()
        for app in all_apps:
            if str(app.get('job_id')) == str(job_id):
                yield app
    
    def stream_by_employer(self, employer_id):
        """Generator to yield applications for a specific employer."""
        all_apps = self.model.stream_all()
        for app in all_apps:
            if str(app.get('employer_id')) == str(employer_id):
                yield app
    
    def stream_by_applicant(self, applicant_id):
        """Generator to yield applications for a specific applicant."""
        all_apps = self.model.stream_all()
        for app in all_apps:
            if str(app.get('applicant_id')) == str(applicant_id):
                yield app
    
    def batch_stream_applications(self, batch_size=10):
        """Generator to yield applications in batches for efficient processing."""
        all_apps = self.model.stream_all()
        for i in range(0, len(all_apps), batch_size):
            yield all_apps[i:i + batch_size]
    
    def stream_recent_applications(self, days=7):
        """Generator to yield applications from last N days."""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        all_apps = self.model.stream_all()
        for app in all_apps:
            app_date = app.get('applied_date')
            if app_date and isinstance(app_date, datetime) and app_date >= cutoff_date:
                yield app

class JobGenerator:
    """Generator class for streaming job postings efficiently."""
    
    def __init__(self, job_model):
        self.model = job_model
    
    def stream_by_employer(self, employer_id):
        """Generator to yield jobs for a specific employer."""
        all_jobs = self.model.list_by_user(employer_id)
        for job in all_jobs:
            yield job
    
    def stream_active_jobs(self):
        """Generator to yield only active job postings."""
        all_jobs = self.model.list_all()
        for job in all_jobs:
            if job.get('status') == 'active':
                yield job
    
    def stream_by_location(self, location):
        """Generator to yield jobs by location."""
        all_jobs = self.model.list_all()
        for job in all_jobs:
            if location.lower() in job.get('location', '').lower():
                yield job


class JobDAO:
    """Data Access Object for job operations."""
    
    def __init__(self):
        self.job_posting_model = JobPosting()
    
    def insert_job(self, employer_id: int, job_data: dict) -> int:
        """Insert a new job posting."""
        job_data['user_id'] = employer_id
        job_data['posted_date'] = datetime.now()
        job_data['status'] = 'active'
        job_data['applications_count'] = 0
        
        return self.job_posting_model.create(job_data)
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID."""
        user_model = User()
        return user_model.get(user_id)

def get_user_by_credentials(email_or_phone: str, password: str) -> dict:
    """Get user by login credentials."""
    user_model = User()
    user = user_model.get_by_email(email_or_phone)
    if not user:
        user = user_model.get_by_phone(email_or_phone)
    return user

def get_all_jobs() -> list:
    """Get all active and open job postings for job seekers."""
    job_model = JobPosting()
    return job_model.list_all()

def get_job_by_id(job_id: int) -> dict:
    """Get job posting by ID."""
    job_model = JobPosting()
    return job_model.get_by_id(job_id)

def create_application(application_data: dict) -> int:
    """Create a new application."""
    app_model = Application()
    return app_model.create(application_data)

def get_applications_by_job(job_id: int) -> list:
    """Get all applications for a job."""
    app_model = Application()
    return app_model.list_by_job(job_id)

def get_applications_by_user(user_id: int, user_role: str) -> list:
    """Get applications by user (either applicant or employer)."""
    app_model = Application()
    if user_role == 'job_seeker':
        return app_model.list_by_applicant(user_id)
    elif user_role == 'employer':
        return app_model.list_by_employer(str(user_id))
    return []

def can_apply_to_job(job_id: int, applicant_id: int) -> tuple:
    """Check if user can apply to this job."""
    job_model = JobPosting()
    app_model = Application()
    
    job = job_model.get_by_id(job_id)
    if not job:
        return False, "Job not found"
    
    required = job.get('required_candidates', 1)
    hired = job.get('hired_count', 0)
    is_closed = job.get('is_closed', False)
    
    if is_closed or hired >= required:
        return False, "This position has been filled"
    
    existing = app_model.check_existing(job_id, applicant_id)
    if existing:
        return False, "You have already applied to this job"
    
    return True, "Can apply"

def update_application_status(application_id: int, new_status: str) -> bool:
    """Update application status in database."""
    try:
        app_model = Application()
        result = app_model.update_status(application_id, new_status)
        return result > 0
    except Exception as e:
        print(f"Error updating application status: {e}")
        return False

def init_models(db_manager: DatabaseManager):
    """Initialize all models with database manager"""
    BaseModel.set_db(db_manager)
    User.db = db_manager
    JobPosting.db = db_manager
    Application.db = db_manager
    JobOffer.db = db_manager
