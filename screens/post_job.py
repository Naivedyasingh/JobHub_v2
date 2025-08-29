# pages/post_job.py

import time
from datetime import datetime
import streamlit as st
from utils.jobs import add_job_posting


class JobFormValidator:
    """Handles validation of job posting form data."""
    
    @staticmethod
    def validate_required_fields(job_title, location, description):
        """Validate that all required fields are filled."""
        return bool(job_title.strip() and location.strip() and description.strip())
    
    @staticmethod
    def validate_salary_range(salary):
        """Validate salary is within acceptable range."""
        return 5_000 <= salary <= 100_000
    
    @staticmethod
    def validate_candidate_count(required_candidates):
        """Validate required candidates count."""
        return 1 <= required_candidates <= 50


class JobDataManager:
    """Handles job posting data operations."""
    
    def create_job_data(self, form_data):
        """Create job data dictionary for database storage."""
        return {
            "title": form_data["job_title"].strip(),
            "location": form_data["location"].strip(),
            "salary": form_data["salary"],
            "job_type": form_data["job_type"],
            "experience": form_data["experience"],
            "working_hours": form_data["working_hours"],
            "urgency": form_data["urgency"],
            "contract_type": form_data["contract_type"],
            "description": form_data["description"].strip(),
            "requirements": form_data["requirements"].strip(),
            "benefits": form_data["benefits"].strip(),
            "required_candidates": form_data["required_candidates"],
            "hired_count": 0,
            "is_closed": False,
            "auto_closed": False,
        }
    
    def save_job_posting(self, user_id, job_data):
        """Save job posting to database."""
        return add_job_posting(user_id, job_data)


class PostJobFormRenderer:
    """Handles rendering of job posting form components."""
    
    def __init__(self):
        self.job_categories = [
            "Maid", "Cook", "Driver", "Cleaner", "Babysitter",
            "Gardener", "Security Guard", "Electrician", "Plumber", "Other"
        ]
        self.experience_levels = ["Any", "Fresher", "1-2 years", "2-5 years", "5+ years"]
        self.working_hours_options = ["Full Time", "Part Time", "Weekends Only", "Flexible"]
        self.urgency_levels = ["Normal", "Urgent", "Very Urgent"]
        self.contract_types = ["Permanent", "Temporary", "Contract", "Part-time"]
    
    def render_basic_fields(self):
        """Render basic job information fields."""
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title *", placeholder="e.g., House Maid, Cook, Driver")
            location = st.text_input("Job Location *", placeholder="City, Area")
            salary = st.number_input("Monthly Salary (₹) *", 5_000, 100_000, 15_000, 1_000)
            job_type = st.selectbox("Job Category *", self.job_categories)
        
        with col2:
            experience = st.selectbox("Experience Required", self.experience_levels)
            working_hours = st.selectbox("Working Hours", self.working_hours_options)
            urgency = st.selectbox("Urgency Level", self.urgency_levels)
            contract_type = st.selectbox("Contract Type", self.contract_types)
        
        st.markdown("### 👥 Hiring Requirements")
        required_candidates = st.number_input(
            "Number of candidates needed",
            min_value=1,
            max_value=50,
            value=1,
            help="How many people do you want to hire for this position?"
        )
        
        return {
            "job_title": job_title,
            "location": location,
            "salary": salary,
            "job_type": job_type,
            "experience": experience,
            "working_hours": working_hours,
            "urgency": urgency,
            "contract_type": contract_type,
            "required_candidates": required_candidates
        }
    
    def render_description_fields(self):
        """Render job description and requirements fields."""
        description = st.text_area(
            "Job Description *", 
            placeholder="Describe the job responsibilities, working conditions..."
        )
        requirements = st.text_area(
            "Requirements & Qualifications", 
            placeholder="Specific skills, qualifications, or experience needed..."
        )
        benefits = st.text_area(
            "Benefits & Perks", 
            placeholder="Additional benefits like meals, accommodation, bonus, etc."
        )
        
        return {
            "description": description,
            "requirements": requirements,
            "benefits": benefits
        }
    
    def render_submit_button(self, is_posting):
        """Render the submit button with appropriate state."""
        btn_txt = "⌛ Posting..." if is_posting else "📤 Post Job"
        return st.form_submit_button(btn_txt, type="primary", disabled=is_posting)


class PostJobRenderer:
    """Handles rendering of post job page UI components."""
    
    def __init__(self):
        self.form_renderer = PostJobFormRenderer()
        self.validator = JobFormValidator()
    
    def render_header(self):
        """Render page header."""
        st.title("📝 Post New Job")
        st.subheader("Find the perfect candidate for your job opening")
    
    def render_job_form(self, is_posting):
        """Render the complete job posting form."""
        with st.form("job_posting_form"):
            basic_data = self.form_renderer.render_basic_fields()
            description_data = self.form_renderer.render_description_fields()
            submitted = self.form_renderer.render_submit_button(is_posting)
            form_data = {**basic_data, **description_data, "submitted": submitted}
            return form_data
    
    def render_navigation(self):
        """Render navigation buttons."""
        st.markdown("---")
        if st.button("🏠 Back to Dashboard"):
            st.session_state.page = "hire_dashboard"
            st.session_state.page_flag = None
            st.session_state.job_posting_disabled = False
            st.rerun()
    
    def show_success_message(self):
        """Display success message."""
        st.success("🎉 Job posted successfully!")
    
    def show_validation_error(self):
        """Display validation error message."""
        st.error("Please fill all required fields marked with *")
    
    def show_candidate_count_error(self):
        """Display candidate count validation error."""
        st.error("Number of candidates must be between 1 and 50")
    
    def show_save_error(self):
        """Display save error message."""
        st.error("Failed to post job. Please try again.")


class SessionStateManager:
    """Handles session state management for job posting."""
    
    @staticmethod
    def initialize_page_state():
        """Initialize or reset page state when entering post job page."""
        if "page_flag" not in st.session_state or st.session_state.page_flag != "post_job":
            st.session_state.job_posting_disabled = False
            st.session_state.page_flag = "post_job"
    
    @staticmethod
    def set_posting_state(is_posting):
        """Set the posting disabled state."""
        st.session_state.job_posting_disabled = is_posting
    
    @staticmethod
    def get_posting_state():
        """Get the current posting state."""
        return st.session_state.get("job_posting_disabled", False)
    
    @staticmethod
    def redirect_to_dashboard():
        """Redirect to hire dashboard after successful posting."""
        st.session_state.page = "hire_dashboard"
        st.session_state.page_flag = None
        st.session_state.job_posting_disabled = False
        time.sleep(1)
        st.rerun()


class PostJobPage:
    """Main controller for post job page."""
    
    def __init__(self):
        self.data_manager = JobDataManager()
        self.renderer = PostJobRenderer()
        self.validator = JobFormValidator()
        self.session_manager = SessionStateManager()
    
    def _handle_form_submission(self, form_data, user):
        """Handle the job posting form submission."""
        if not self.validator.validate_required_fields(
            form_data["job_title"], 
            form_data["location"], 
            form_data["description"]
        ):
            self.renderer.show_validation_error()
            return False
        
        if not self.validator.validate_candidate_count(form_data["required_candidates"]):
            self.renderer.show_candidate_count_error()
            return False
        self.session_manager.set_posting_state(True)
        
        job_data = self.data_manager.create_job_data(form_data)
        
        if self.data_manager.save_job_posting(user["id"], job_data):
            self.renderer.show_success_message()
            self.session_manager.redirect_to_dashboard()
            return True
        else:
            self.renderer.show_save_error()
            self.session_manager.set_posting_state(False)
            return False
    
    def display(self):
        """Main method to display the complete post job page."""
        user = st.session_state.current_user
        
        self.session_manager.initialize_page_state()
        self.renderer.render_header()
        is_posting = self.session_manager.get_posting_state()
        form_data = self.renderer.render_job_form(is_posting)
        
        if form_data["submitted"]:
            self._handle_form_submission(form_data, user)
        self.renderer.render_navigation()


# Preserve the original function signature - NO CHANGES to existing code needed
def post_job_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = PostJobPage()
    page.display()
