import streamlit as st
from datetime import datetime
from utils.applications import get_job_applications
from db.models import JobPosting

class HireDashboardRenderer:
    """Handles rendering of hire dashboard UI components."""
    
    def render_header(self, user):
        """Render dashboard header with user greeting."""
        st.title("🏢 Employer Dashboard")
        st.subheader(f"Welcome back, {user['name']}! 👋")
    
    def render_quick_actions(self):
        """Render quick action buttons for main dashboard functions."""
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📝 Post New Job", use_container_width=True, type="secondary", key="hire_post_job"):
                st.session_state.page = "post_job"
                st.rerun()
        with col2:
            if st.button("👥 Browse Job Seekers", use_container_width=True, key="hire_browse_seekers"):
                st.session_state.page = "browse_job_seekers"
                st.rerun()
        with col3:
            if st.button("📋 Applications", use_container_width=True, key="hire_view_applications"):
                st.session_state.page = "view_applications"
                st.rerun()
        with col4:
            if st.button("📊 My Job Posts", use_container_width=True, key="hire_my_job_posts"):
                st.session_state.page = "my_job_postings"  
                st.rerun()
    
    def render_company_stats(self, stats_data):
        """Render company statistics metrics."""
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Jobs Posted", stats_data['jobs_posted'])
        with col2:
            st.metric("Total Applications", stats_data['total_applications'])
        with col3:
            st.metric("Pending Applications", stats_data['pending_applications'])
        with col4:
            st.metric("Accepted", stats_data['accepted_applications'])
    
    def render_application_card(self, app):
        """Render individual application card with proper styling."""
        status = app.get("status", "pending")
        border_colors = {"pending": "#ffc107", "accepted": "#28a745", "rejected": "#dc3545"}
        status_colors = {"pending": "🟡 Pending", "accepted": "🟢 Accepted", "rejected": "🔴 Rejected"}

        border_color = border_colors.get(status, "#ffc107")
        status_text = status_colors.get(status, "🟡 Pending")

        name = app.get("applicant_name", "N/A")
        job = app.get("job_title", "N/A")
        phone = app.get("applicant_phone", "N/A")
        email = app.get("applicant_email", "N/A")
        experience = app.get("applicant_experience", "N/A")
        skills = app.get("applicant_skills", "Not specified")

        st.markdown(f"""
            <div style="border: 2px solid {border_color}; border-left: 5.5px solid {border_color};
                        border-radius: 10px; padding: 20px; margin: 15px 0; background-color: #f8f9fa;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 15px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
                    {name} – {job}
                </h4>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px; margin-right: 20px;">
                        <p style="margin: 5px 0;"><strong>📱 Phone:</strong> {phone}</p>
                        <p style="margin: 5px 0;"><strong>✉️ Email:</strong> {email}</p>
                    </div>
                    <div style="flex: 1; min-width: 200px; margin-right: 20px;">
                        <p style="margin: 5px 0;"><strong>Experience:</strong> {experience}</p>
                        <p style="margin: 5px 0;"><strong>Skills:</strong> {skills}</p>
                    </div>
                    <div style="flex: 0 0 auto; min-width: 120px;">
                        <p style="margin: 5px 0;"><strong>Status:</strong> {status_text}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    def render_recent_applications_section(self, recent_applications):
        """Render recent applications section without tabs."""
        st.markdown("### 📨 Recent Applications")
        
        if recent_applications:
            st.markdown("Latest applications across all your jobs:")
            for app in recent_applications:
                self.render_application_card(app)
                
            if len(recent_applications) >= 3:
                if st.button("📋 View All Applications", use_container_width=True):
                    st.session_state.page = "view_applications"
                    st.rerun()
        else:
            st.info("No applications received yet. Post some jobs to start receiving applications!")
            if st.button("📝 Post Your First Job", use_container_width=True):
                st.session_state.page = "post_job"
                st.rerun()

class HireDataManager:
    """Handles data operations for hire dashboard."""
    
    def __init__(self):
        self.job_posting_model = JobPosting()
    
    def get_employer_applications(self, employer_id):
        """Get all applications for a specific employer."""
        applications = get_job_applications()
        return [app for app in applications if str(app.get("employer_id")) == str(employer_id)]
    
    def get_employer_jobs(self, employer_id):
        """Get all job postings for a specific employer."""
        return list(self.job_posting_model.list_by_user(employer_id))
    
    def calculate_application_stats(self, applications):
        """Calculate application statistics for dashboard metrics."""
        pending_apps = len([app for app in applications if app.get("status") == "pending"])
        accepted_apps = len([app for app in applications if app.get("status") == "accepted"])
        
        return {
            'total_applications': len(applications),
            'pending_applications': pending_apps,
            'accepted_applications': accepted_apps
        }
    
    def safe_date_key(self, application):
        """Return a datetime for sorting, with None converted """
        date_val = application.get("applied_date")
        if date_val is None:
            return datetime.min  
        if isinstance(date_val, datetime):
            return date_val
        try:
            return datetime.fromisoformat(str(date_val))
        except:
            return datetime.min 
    
    def get_recent_applications(self, applications, limit=3):
        """Get recent applications sorted by date."""
        return sorted(
            applications,
            key=self.safe_date_key,
            reverse=True
        )[:limit]

class HireDashboard:
    """Main hire dashboard controller that orchestrates all dashboard components."""
    
    def __init__(self):
        self.renderer = HireDashboardRenderer()
        self.data_manager = HireDataManager()
    
    def display(self):
        """Main method to display the complete hire dashboard."""
        user = st.session_state.current_user
        self.renderer.render_header(user)
        self.renderer.render_quick_actions()

        st.markdown("---")

        my_applications = self.data_manager.get_employer_applications(user["id"])
        my_jobs = self.data_manager.get_employer_jobs(user["id"])
        
        app_stats = self.data_manager.calculate_application_stats(my_applications)
        stats_data = {
            'jobs_posted': len(my_jobs),
            **app_stats
        }

        self.renderer.render_company_stats(stats_data)

        st.markdown("---")

        recent_applications = self.data_manager.get_recent_applications(my_applications)
        self.renderer.render_recent_applications_section(recent_applications)

def hire_dashboard():
    dashboard = HireDashboard() 
    dashboard.display()
