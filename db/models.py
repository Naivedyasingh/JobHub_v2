# db/models.py

import json
import pymysql
from typing import Any, Dict, List, Optional


def db_operation(func):
    """Decorator for database operations with logging"""
    def wrapper(self, *args, **kwargs):
        print(f"[DB] {func.__name__} args={args} kwargs={kwargs}")
        return func(self, *args, **kwargs)
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
            # ⬅️ FIX: Add UTF-8 encoding to handle special characters
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Split and execute each statement
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
        # Convert Python lists/objects to JSON strings for JSON columns
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
                # Convert JSON strings back to Python objects
                json_columns = ['job_types', 'availability', 'languages']
                for col in json_columns:
                    if col in result and result[col]:
                        try:
                            result[col] = json.loads(result[col])
                        except (json.JSONDecodeError, TypeError):
                            result[col] = []  # Default to empty list if parsing fails
                    elif col in result:
                        result[col] = []  # Default to empty list if None/empty
            
            return result

    @db_operation
    def update(self, user_id: int, updates: dict) -> int:
        # Convert Python lists/objects to JSON strings for JSON columns
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
            
            # Process JSON columns for all results
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
    def list_by_user(self, user_id: int):
        sql = "SELECT * FROM job_postings WHERE user_id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (user_id,))
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
    def stream_all(self):
        sql = "SELECT * FROM applications"
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    @db_operation
    def update_status(self, app_id: int, status: str, response_message: str = "") -> int:
        sql = "UPDATE applications SET status=%s, response_message=%s, response_date=NOW() WHERE id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (status, response_message, app_id))
            return cur.rowcount


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
    def stream_all(self):
        sql = "SELECT * FROM job_offers"
        with self.db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    @db_operation
    def update_status(self, offer_id: int, status: str, response_message: str = "") -> int:
        sql = "UPDATE job_offers SET status=%s, response_message=%s, response_date=NOW() WHERE id=%s"
        with self.db.cursor() as cur:
            cur.execute(sql, (status, response_message, offer_id))
            return cur.rowcount


class JobDAO:
    """Data Access Object for job-related operations"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager or User.db

    @db_operation
    def insert_job(self, employer_id: int, job_data: dict) -> bool:
        """Insert a new job posting"""
        try:
            from datetime import datetime
            
            # ⬅️ FIX: Change job_types to job_type to match table schema
            if 'job_types' in job_data:
                # Convert job_types list to a single job_type string
                job_types = job_data.pop('job_types')
                if isinstance(job_types, list) and job_types:
                    job_data['job_type'] = job_types[0]  # Take first job type
                elif isinstance(job_types, str):
                    job_data['job_type'] = job_types
                else:
                    job_data['job_type'] = 'General'  # Default fallback
            
            # Add metadata
            job_data.update({
                'user_id': employer_id,
                'posted_date': datetime.now(),
                'status': 'active',
                'applications_count': 0
            })
            
            cols = ", ".join(job_data.keys())
            vals = ", ".join(["%s"] * len(job_data))
            sql = f"INSERT INTO job_postings ({cols}) VALUES ({vals})"
            
            with self.db.cursor() as cur:
                cur.execute(sql, tuple(job_data.values()))
                return cur.lastrowid > 0
        except Exception as e:
            print(f"[DB] Error inserting job: {e}")
            return False

    @db_operation
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID - delegates to User model"""
        user_model = User()
        return user_model.get(user_id)


def init_models(db_manager: DatabaseManager):
    """Initialize all models with database manager"""
    BaseModel.set_db(db_manager)
    User.db = db_manager
    JobPosting.db = db_manager
    Application.db = db_manager
    JobOffer.db = db_manager
