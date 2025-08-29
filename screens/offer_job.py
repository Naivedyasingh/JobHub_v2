import time
import streamlit as st
from datetime import datetime, timedelta
from utils.offers import save_job_offer


class SkillsFormatter:
    """Handles formatting of skills and job types."""
    
    @staticmethod
    def format_skills(job_types):
        """Helper function to properly format job_types for display"""
        if isinstance(job_types, str):
            try:
                import json
                job_types = json.loads(job_types)
            except:
                job_types = [s.strip() for s in job_types.split(",") if s.strip()]
        elif not isinstance(job_types, list):
            job_types = []
        return ', '.join(job_types) if job_types else 'Not specified'


class OfferFormValidator:
    """Handles validation of job offer form data."""
    
    @staticmethod
    def validate_required_fields(job_title, location, job_description):
        """Validate that all required fields are filled."""
        return all([job_title.strip(), location.strip(), job_description.strip()])
    
    @staticmethod
    def validate_salary_range(salary):
        """Validate salary is within acceptable range."""
        return 5_000 <= salary <= 100_000


class OfferDataManager:
    """Handles job offer data operations."""
    
    def __init__(self):
        self.skills_formatter = SkillsFormatter()
    
    def create_offer_data(self, form_data, user, candidate):
        """Create offer data dictionary for database storage."""
        now = datetime.now()
        expires_at = now + timedelta(hours=24)
        
        return {
            "job_title": form_data["job_title"].strip(),
            "job_description": form_data["job_description"].strip(),
            "location": form_data["location"].strip(),
            "salary_offered": form_data["salary_offered"],
            "job_type": form_data["job_type"],
            "working_hours": form_data["working_hours"],
            "start_date": str(form_data["start_date"]),
            "personal_message": form_data["personal_message"].strip(),
            "employer_id": user["id"],
            "employer_name": user.get("company_name", user["name"]),
            "employer_phone": user["phone"],
            "employer_email": user["email"],
            "job_seeker_id": candidate["id"],
            "job_seeker_name": candidate["name"],
            "job_seeker_phone": candidate["phone"],
            "job_seeker_email": candidate["email"],
            "offered_date": now,
            "expires_at": expires_at,
            "status": "pending",
        }
    
    def save_offer(self, offer_data):
        """Save job offer to database."""
        return save_job_offer(offer_data)


class OfferJobRenderer:
    """Handles rendering of offer job page UI components."""
    
    def __init__(self):
        self.skills_formatter = SkillsFormatter()
        self.validator = OfferFormValidator()
    
    def render_header(self, candidate_name):
        """Render page header."""
        st.title(f"💼 Offer Job to {candidate_name}")
    
    def render_candidate_summary(self, candidate):
        """Render candidate information summary."""
        skills_text = self.skills_formatter.format_skills(candidate.get('job_types', []))
        
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        border-radius: 10px; padding: 15px; margin: 10px 0;">
                <h4>📋 Candidate Summary</h4>
                <p><strong>📱 Phone:</strong> {candidate['phone']} |
                   <strong>✉️ Email:</strong> {candidate['email']}</p>
                <p><strong>🛠️ Skills:</strong> {skills_text} |
                   <strong>📈 Experience:</strong> {candidate.get('experience', 'Not specified')}</p>
                <p><strong>💰 Expected Salary:</strong> ₹{candidate.get('expected_salary', 'Not specified')} |
                   <strong>📍 Location:</strong> {candidate.get('city', 'Not specified')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    def render_offer_form(self, user, candidate):
        """Render the job offer form and return form data."""
        with st.form("job_offer_form"):
            st.subheader("💼 Job Offer Details")

            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title *", placeholder="e.g., House Maid, Cook, Driver")
                location = st.text_input("Job Location *", value=user.get("city", ""), placeholder="City, Area")
                salary_offered = st.number_input(
                    "Salary Offer (₹) *",
                    min_value=5_000,
                    max_value=100_000,
                    value=candidate.get("expected_salary", 15_000),
                    step=1_000,
                )

            with col2:
                job_type = st.selectbox(
                    "Job Category",
                    [
                        "Maid",
                        "Cook",
                        "Driver",
                        "Cleaner",
                        "Babysitter",
                        "Gardener",
                        "Security Guard",
                        "Electrician",
                        "Plumber",
                        "Other",
                    ],
                )
                working_hours = st.selectbox("Working Hours", ["Full Time", "Part Time", "Weekends Only", "Flexible"])
                start_date = st.date_input("Preferred Start Date")

            job_description = st.text_area(
                "Job Description *", placeholder="Describe the job responsibilities and requirements..."
            )
            personal_message = st.text_area(
                "Personal Message to Candidate", placeholder="Why do you think they're perfect for this role?"
            )

            submitted = st.form_submit_button("📤 Send Job Offer", type="primary")
            
            return {
                "job_title": job_title,
                "location": location,
                "salary_offered": salary_offered,
                "job_type": job_type,
                "working_hours": working_hours,
                "start_date": start_date,
                "job_description": job_description,
                "personal_message": personal_message,
                "submitted": submitted
            }
    
    def render_navigation_buttons(self):
        """Render navigation buttons."""
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back to Browse Job Seekers", key="back_to_browse"):
                st.session_state.page = "browse_job_seekers"
                st.rerun()

        with col2:
            if st.button("🏠 Back to Dashboard", key="back_to_dashboard"):
                st.session_state.page = "hire_dashboard"
                st.rerun()
    
    def show_success_message(self, candidate_name):
        """Display success message and information."""
        st.success(f"🎉 Job offer sent to {candidate_name}!")
        st.info("The candidate has 24 hours to respond to your offer.")
        st.info("You will be notified once they accept or decline the offer.")
    
    def show_validation_error(self):
        """Display validation error message."""
        st.error("Please fill all required fields marked with *")
    
    def show_save_error(self):
        """Display save error message."""
        st.error("Failed to send job offer. Please try again.")


class OfferJobPage:
    """Main controller for offer job page."""
    
    def __init__(self):
        self.data_manager = OfferDataManager()
        self.renderer = OfferJobRenderer()
        self.validator = OfferFormValidator()
    
    def _handle_form_submission(self, form_data, user, candidate):
        """Handle the job offer form submission."""
        if not self.validator.validate_required_fields(
            form_data["job_title"], 
            form_data["location"], 
            form_data["job_description"]
        ):
            self.renderer.show_validation_error()
            return False
        
        offer_data = self.data_manager.create_offer_data(form_data, user, candidate)
        
        if self.data_manager.save_offer(offer_data):
            self.renderer.show_success_message(candidate["name"])
            self._redirect_to_dashboard()
            return True
        else:
            self.renderer.show_save_error()
            return False
    
    def _redirect_to_dashboard(self):
        """Redirect to hire dashboard after successful offer submission."""
        st.session_state.page = "hire_dashboard"
        st.session_state.page_flag = None
        st.session_state.job_posting_disabled = False
        time.sleep(3)
        st.rerun()
    
    def display(self):
        """Main method to display the complete offer job page."""
        user = st.session_state.current_user
        candidate = st.session_state.get("selected_candidate")

        if not candidate:
            st.error("No candidate selected")
            return

        self.renderer.render_header(candidate['name'])
        self.renderer.render_candidate_summary(candidate)
        st.markdown("---")
        form_data = self.renderer.render_offer_form(user, candidate)
        if form_data["submitted"]:
            self._handle_form_submission(form_data, user, candidate)
        self.renderer.render_navigation_buttons()


def format_skills(job_types):
    """Wrapper function to maintain backward compatibility."""
    return SkillsFormatter.format_skills(job_types)


def offer_job_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = OfferJobPage()
    page.display()
