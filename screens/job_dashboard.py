# pages/job_dashboard.py

import time
import streamlit as st
from datetime import datetime, timedelta
from utils.applications import (
    get_job_applications,
    save_job_application,
)
from utils.offers import get_job_offers, update_offer_status
from utils.auth import calculate_profile_completion
from db.models import User, JobPosting
from typing import List, Dict

class CongratsStorage:
    """Handles permanent storage of congratulations dismissals in database."""
    
    def __init__(self):
        self.user_model = User
    
    def is_dismissed(self, user_id, job_id, app_id):
        """Check if congratulations for this job+application has been dismissed."""
        try:
            with self.user_model.db.cursor() as cur:
                cur.execute("""
                    SELECT id FROM congratulations_dismissed 
                    WHERE user_id=%s AND job_id=%s AND application_id=%s
                """, (user_id, job_id, app_id))
                return cur.fetchone() is not None
        except Exception as e:
            print(f"[DB] Error checking dismissal: {e}")
            return False
    
    def mark_dismissed(self, user_id, job_id, app_id):
        """Permanently mark congratulations as dismissed in database."""
        try:
            with self.user_model.db.cursor() as cur:
                cur.execute("""
                    INSERT INTO congratulations_dismissed (user_id, job_id, application_id, dismissed_at)
                    VALUES (%s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE dismissed_at = NOW()
                """, (user_id, job_id, app_id))
                return True
        except Exception as e:
            print(f"[DB] Error marking dismissal: {e}")
            return False

class HiredNotificationManager:
    """Handles congratulations notifications for newly hired job seekers."""
    
    def __init__(self):
        self.storage = CongratsStorage()
    
    def get_new_accepted_applications(self, user_id):
        """Get applications that were recently accepted but not yet congratulated."""
        all_applications = get_job_applications()
        user_applications = [
            app for app in all_applications 
            if str(app.get("applicant_id")) == str(user_id) and app.get("status") == "accepted"
        ]
        
        new_accepted = []
        
        for app in user_applications:
            job_id = app.get('job_id', 0)
            app_id = app.get('id', 0)
            
            # ← FIXED: Check database instead of session state
            if not self.storage.is_dismissed(user_id, job_id, app_id):
                response_date = app.get("response_date")
                if response_date:
                    try:
                        if isinstance(response_date, str):
                            response_dt = datetime.fromisoformat(response_date.replace("Z", "+00:00"))
                        else:
                            response_dt = response_date
                        
                        time_diff = datetime.now() - response_dt
                        
                        # Only show if accepted recently (within 7 days) and not dismissed
                        if time_diff.total_seconds() <= 7 * 24 * 3600:  # Within 7 days
                            new_accepted.append({
                                'job_title': app.get('job_title', 'Job Position'),
                                'employer_name': app.get('employer_name', 'Employer'),
                                'job_id': job_id,
                                'application_id': app_id,
                                'hours_ago': int(time_diff.total_seconds() // 3600),
                                'minutes_ago': int((time_diff.total_seconds() % 3600) // 60),
                                'days_ago': time_diff.days
                            })
                    except Exception as e:
                        continue
        
        return new_accepted
    
    def show_congratulations_popup(self, accepted_jobs, user_id):
        """Display congratulations popup for newly accepted applications."""
        if not accepted_jobs:
            return
        
        # Show popup for each job that hasn't been dismissed
        for idx, job in enumerate(accepted_jobs):
            job_title = job['job_title']
            employer_name = job['employer_name']
            job_id = job.get('job_id', 0)
            app_id = job.get('application_id', 0)
            
            # Format time display
            if job['days_ago'] > 0:
                time_text = f"{job['days_ago']} day{'s' if job['days_ago'] > 1 else ''} ago"
            elif job['hours_ago'] > 0:
                time_text = f"{job['hours_ago']} hour{'s' if job['hours_ago'] > 1 else ''} ago"
            else:
                time_text = f"{job['minutes_ago']} minute{'s' if job['minutes_ago'] > 1 else ''} ago"
            
            # Create celebration popup
            st.balloons()  # Show balloons animation
            
            with st.container():
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 20px;
                        padding: 30px;
                        margin: 20px 0;
                        text-align: center;
                        color: white;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        border: 3px solid #ffd700;
                        animation: pulse 2s infinite;
                        position: relative;
                    ">
                        <h1 style="margin: 0; font-size: 2.5rem;">🎉 CONGRATULATIONS! 🎉</h1>
                        <h2 style="margin: 10px 0; color: #ffd700;">You Got Hired!</h2>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 20px; margin: 20px 0;">
                            <h3 style="margin: 0; color: #fff;">{job_title}</h3>
                            <p style="margin: 5px 0; font-size: 1.2rem;">at <strong>{employer_name}</strong></p>
                            <p style="margin: 5px 0; color: #ffd700;">Accepted {time_text}</p>
                        </div>
                        <p style="margin: 20px 0; font-size: 1.1rem;">
                            🌟 Your hard work paid off! Welcome to your new opportunity! 🌟
                        </p>
                        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; margin: 10px 0;">
                            <small style="color: #ffd700;">💡 This notification will not appear again after dismissal</small>
                        </div>
                    </div>
                    
                    <style>
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                        100% {{ transform: scale(1); }}
                    }}
                    </style>
                """, unsafe_allow_html=True)
                
                # Dismissal button with permanent database storage
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    unique_key = f"dismiss_congrats_{job_id}_{app_id}_{idx}"
                    
                    if st.button("🎊 Thank You! Got It!", 
                               use_container_width=True, 
                               type="primary",
                               key=unique_key):
                        # ← FIXED: Store dismissal in database permanently
                        if self.storage.mark_dismissed(user_id, job_id, app_id):
                            st.success("✅ Congratulations noted! This notification won't appear again.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Error saving dismissal. Please try again.")
                
                st.markdown("---")

class JobSkillsFormatter:
    """Handles formatting of user skills and job types."""
    
    @staticmethod
    def format_user_skills(job_types):
        """Helper function to properly format job_types for application"""
        if isinstance(job_types, str):
            try:
                import json
                job_types = json.loads(job_types)
            except:
                job_types = [s.strip() for s in job_types.split(",") if s.strip()]
        elif not isinstance(job_types, list):
            job_types = []
        return ", ".join(job_types)

class JobDataManager:
    """Handles fetching and processing of job data from database."""
    
    def __init__(self):
        self.user_model = User
    
    def fetch_employer_jobs(self) -> List[Dict]:
        """Return active job postings from all employers joined with employer data."""
        with self.user_model.db.cursor() as cur:
            cur.execute(
                """
                SELECT jp.*, u.id AS employer_id, u.name AS employer_name,
                       u.company_name, u.phone, u.email
                FROM job_postings jp
                JOIN users u ON jp.user_id = u.id
                WHERE jp.status = 'active'
                AND (jp.is_closed = FALSE OR jp.is_closed IS NULL)
                AND (jp.hired_count < jp.required_candidates OR jp.hired_count IS NULL OR jp.required_candidates IS NULL)
                """
            )
            rows = cur.fetchall()

        jobs: List[Dict] = []
        for r in rows:
            job = dict(r)
            # Unify key names with the old JSON structure
            job["job_types"] = [job.get("job_type")] if job.get("job_type") else []
            job["posted_date"] = job.get("posted_date").isoformat() if job.get("posted_date") else ""
            job["employer_info"] = {
                "id": job.pop("employer_id"),
                "name": job.pop("employer_name"),
                "company": job.pop("company_name") or "Company",
                "phone": job.pop("phone"),
                "email": job.pop("email"),
            }
            jobs.append(job)
        return jobs

class JobOfferManager:
    """Handles job offer operations and status management."""
    
    def __init__(self):
        self.skills_formatter = JobSkillsFormatter()
    
    def is_offer_active(self, offer):
        """Return True while an offer is within its 24-hour window."""
        # First try expires_at if it exists
        if offer.get("expires_at"):
            try:
                expires = datetime.fromisoformat(str(offer["expires_at"]))
                return datetime.now() <= expires
            except Exception:
                pass  # bad format → compute fallback

        # Fallback: use offered_date + 24 hours
        if offer.get("offered_date"):
            try:
                base = datetime.fromisoformat(str(offer["offered_date"]))
                return datetime.now() <= (base + timedelta(hours=24))
            except Exception:
                pass

        # If both are missing/invalid, consider expired
        return False
    
    def get_active_offers_for_user(self, user_id):
        """Get all active offers for a specific user."""
        return [
            o
            for o in get_job_offers()
            if o.get("job_seeker_id") == user_id and o.get("status") == "pending" and self.is_offer_active(o)
        ]
    
    def calculate_offer_hours_left(self, offer):
        """Calculate hours left for an offer to expire."""
        expires = None
        if offer.get("expires_at"):
            try:
                expires = datetime.fromisoformat(str(offer["expires_at"]))
            except Exception:
                pass
        
        if not expires and offer.get("offered_date"):
            try:
                base = datetime.fromisoformat(str(offer["offered_date"]))
                expires = base + timedelta(hours=24)
            except Exception:
                expires = datetime.now()  # fallback
        
        if not expires:
            expires = datetime.now()  # fallback
            
        return max(0, int((expires - datetime.now()).total_seconds() // 3600))

class JobFilterManager:
    """Handles job filtering and categorization logic."""
    
    def __init__(self):
        self.default_categories = [
            "Cook", "Maid", "Plumber", "Electrician", "Babysitter",
            "Gardener", "Driver", "Cleaner", "Security Guard",
        ]
    
    def get_job_categories(self, jobs):
        """Extract and return all job categories from jobs list."""
        job_categories_set = set(x.lower() for x in self.default_categories)
        for job in jobs:
            job_types = job.get("job_types", [])
            if isinstance(job_types, str):
                job_types = [job_types]
            job_categories_set.update(jt.strip().lower() for jt in job_types if jt)

        display_job_categories = sorted(j.title() for j in job_categories_set)
        display_to_lower = {j.title(): j.lower() for j in job_categories_set}
        return display_job_categories, display_to_lower
    
    def get_filter_options(self, jobs):
        """Extract filter options from jobs list."""
        locations = sorted(set(job.get("location", "Not specified") for job in jobs))
        companies = sorted(set(job["employer_info"]["company"] for job in jobs))
        salaries = [job.get("salary", 0) or 0 for job in jobs if "salary" in job]
        min_sal, max_sal = (min(salaries) if salaries else 0, max(salaries) if salaries else 0)
        return locations, companies, min_sal, max_sal
    
    def job_types_lower(self, job):
        """Convert job types to lowercase for filtering."""
        jt = job.get("job_types")
        if isinstance(jt, list):
            return [x.lower() for x in jt]
        if isinstance(jt, str):
            return [jt.lower()]
        return []
    
    def apply_filters(self, jobs, location_filter, selected_cat_lower, company_filter, salary_range):
        """Apply all filters to jobs list."""
        return [
            job
            for job in jobs
            if (location_filter == "All" or job.get("location", "Not specified") == location_filter)
            and (
                selected_cat_lower == "all"
                or selected_cat_lower in self.job_types_lower(job)
            )
            and (company_filter == "All" or job["employer_info"]["company"] == company_filter)
            and (salary_range[0] <= (job.get("salary", 0) or 0) <= salary_range[1])
        ]

class JobApplicationManager:
    """Handles job application operations and status management."""
    
    def __init__(self):
        self.skills_formatter = JobSkillsFormatter()
    
    def get_applied_jobs_set(self, user_id):
        """Get set of job IDs that user has already applied to."""
        applications = get_job_applications()
        return {
            (app.get("job_id"), str(app.get("employer_id")))
            for app in applications
            if app.get("applicant_id") == user_id
        }
    
    def split_jobs_by_application_status(self, jobs, applied_set):
        """Split jobs into applied and not-applied lists."""
        applied_jobs, not_applied_jobs = [], []
        for job in jobs:
            key = (job.get("id"), str(job["employer_info"]["id"]))
            (applied_jobs if key in applied_set else not_applied_jobs).append(job)
        return applied_jobs, not_applied_jobs
    
    def create_application_data(self, job, user):
        """Create application data dictionary."""
        return {
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "employer_id": job["employer_info"]["id"],
            "employer_name": job["employer_info"]["company"],
            "applicant_id": user["id"],
            "applicant_name": user["name"],
            "applicant_phone": user["phone"],
            "applicant_email": user["email"],
            "applicant_skills": self.skills_formatter.format_user_skills(user.get("job_types", [])),
            "applicant_experience": user.get("experience", "Not specified"),
            "expected_salary": user.get("expected_salary", "Not specified"),
            "applied_date": datetime.now(),
            "status": "pending",
        }

class JobDashboardRenderer:
    """Handles rendering of job dashboard UI components."""
    
    def __init__(self):
        self.offer_manager = JobOfferManager()
        self.filter_manager = JobFilterManager()
        self.application_manager = JobApplicationManager()
        self.notification_manager = HiredNotificationManager()
    
    def render_header(self, user):
        """Render dashboard header with user greeting."""
        st.markdown(
            f"""
            <div style="text-align:center;">
              <span style="font-size:2.2rem;"><b>🔍 Job Seeker Dashboard</b></span><br>
              <span style="font-size:1.2rem; color:#222;">Welcome back, <b>{user['name']}</b>! 👋</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
    
    def render_congratulations_section(self, user_id):
        """Render congratulations popup for recent hires that haven't been dismissed."""
        new_accepted = self.notification_manager.get_new_accepted_applications(user_id)
        if new_accepted:
            self.notification_manager.show_congratulations_popup(new_accepted, user_id)  # ← Pass user_id
    
    def render_profile_completion_warning(self, completion):
        """Render profile completion warning if profile is incomplete."""
        if completion < 100:
            st.error(
                f"⚠️ **Profile Incomplete ({completion}%)** - "
                "Complete your profile to apply for jobs and receive offers!"
            )
            if st.button("📝 Complete Profile Now", type="primary", key="dashboard_complete_profile"):
                st.session_state.page = "profile"
                st.rerun()
            st.markdown("---")
            return True
        return False
    
    def render_active_offers(self, user):
        """Render active job offers section."""
        active_offers = self.offer_manager.get_active_offers_for_user(user["id"])
        
        if active_offers:
            st.markdown("### 🎯 **Job Offers for You!**")
            for offer in active_offers:
                hours_left = self.offer_manager.calculate_offer_hours_left(offer)

                st.markdown(
                    f"""
                    <div style="border:3px solid #ff6b35; border-radius:15px; padding:20px; margin:10px 0;
                                background:linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);">
                     <b>💼 {offer.get('job_title')}</b><br>
                     <b>🏢 Company:</b> {offer.get('employer_name')}<br>
                     <b>💰 Salary:</b> ₹{offer.get('salary_offered')}<br>
                     <b>📍 Location:</b> {offer.get('location', 'Not specified')}<br>
                     <b>💬 Message:</b> {offer.get('personal_message', 'No message')}<br>
                     <b>⏰ Expires in:</b> {hours_left} hours
                    </div>""",
                    unsafe_allow_html=True,
                )

                col_accept, col_reject = st.columns(2)
                with col_accept:
                    if st.button("✅ Accept", key=f"accept_offer_{offer['id']}", type="primary"):
                        update_offer_status(offer["id"], "accepted", "Job offer accepted by job seeker")
                        st.success("🎉 Job offer accepted! The employer will be notified.")
                        st.rerun()
                with col_reject:
                    if st.button("❌ Decline", key=f"decline_offer_{offer['id']}"):
                        update_offer_status(offer["id"], "rejected", "Job offer declined by job seeker")
                        st.info("Job offer declined.")
                        st.rerun()
            st.markdown("---")
    
    def render_job_filters(self, jobs):
        """Render job filtering controls and return filter values."""
        display_job_categories, display_to_lower = self.filter_manager.get_job_categories(jobs)
        locations, companies, min_sal, max_sal = self.filter_manager.get_filter_options(jobs)

        c1, c2, c3, c4 = st.columns([2, 2, 2, 4])
        with c1:
            location_filter = st.selectbox("By Location:", ["All"] + locations, index=0)
        with c2:
            job_category_filter = st.selectbox("Job Category:", ["All"] + display_job_categories, index=0)
        with c3:
            company_filter = st.selectbox("By Company:", ["All"] + companies, index=0)
        with c4:
            if min_sal < max_sal:
                salary_range = st.slider(
                    "Salary Range (₹):", int(min_sal), int(max_sal), (int(min_sal), int(max_sal)), step=1000
                )
            else:
                salary_range = (int(min_sal), int(max_sal))

        selected_cat_lower = display_to_lower.get(job_category_filter, "all")
        return location_filter, selected_cat_lower, company_filter, salary_range
    
    def render_job_card(self, job, is_applied=False):
        """Render individual job card."""
        border_color = "#6c757d" if is_applied else "#ffff9d"
        bg_color = "#f0f0f0" if is_applied else "#f9f9ec"
        shadow_color = "#ccc" if is_applied else "#aad7b4"
        text_color = "color:#555;" if is_applied else ""
        
        st.markdown(
            f"""
            <div style="border:2px solid {border_color}; border-radius:15px; background:{bg_color}; padding:18px;
                        margin-bottom:1.5rem; box-shadow:0 2px 6px {shadow_color};">
                <h4 style="margin-bottom:.5rem; font-weight:700; {text_color}">💼 {job.get('title')}</h4>
                <b>🏢 {job['employer_info']['company']}</b> | <b>📍 {job.get('location', 'Not specified')}</b><br>
                <b>💰 Salary:</b> ₹{job.get('salary', 'Not specified')}
                <b>Type:</b> {job.get('working_hours', job.get('type', 'Not specified'))}<br>
                <b>📈 Experience:</b> {job.get('experience', 'Any')}<br>
                <b>🗓️ Posted:</b> {job.get('posted_date', '')[:10] or 'N/A'}<br>
                <b>📞 Contact:</b> {job['employer_info']['phone']} | <b>✉️</b> {job['employer_info']['email']}<br>
                <span style='font-size:0.97em; color:#444;'>
                    {(job.get('description','')[:120]+'...') if len(job.get('description','')) > 120 else job.get('description','')}
                </span>
                {"<br><br><button disabled style=\"padding:6px 12px; background:#6c757d; color:#fff; border:none; border-radius:4px;\">✅ Already Applied</button>" if is_applied else ""}
            </div>""",
            unsafe_allow_html=True,
        )
    
    def render_job_tabs(self, applied_jobs, not_applied_jobs, user):
        """Render job tabs for available and applied jobs."""
        tab_avail, tab_applied = st.tabs(
            [f"🟢 Available Jobs ({len(not_applied_jobs)})", f"✅ Applied Jobs ({len(applied_jobs)})"]
        )

        # Available jobs tab
        with tab_avail:
            if not_applied_jobs:
                for idx, job in enumerate(not_applied_jobs):
                    if idx % 2 == 0:
                        cols = st.columns(2)
                    
                    with cols[idx % 2]:
                        self.render_job_card(job, is_applied=False)

                        if st.button(
                            "🟢 Apply Now",
                            key=f"apply_{job['employer_info']['id']}_{job.get('id')}",
                            use_container_width=True,
                            type="primary",
                        ):
                            application = self.application_manager.create_application_data(job, user)
                            if save_job_application(application):
                                st.success("✅ Application sent successfully!")
                                time.sleep(1)
                                st.rerun()
            else:
                st.info("🎉 No new jobs available to apply for!")

        # Applied jobs tab
        with tab_applied:
            if applied_jobs:
                for idx, job in enumerate(applied_jobs):
                    if idx % 2 == 0:
                        cols = st.columns(2)
                    
                    with cols[idx % 2]:
                        self.render_job_card(job, is_applied=True)
            else:
                st.info("🙌 You have not applied for any jobs yet.")

class JobDashboard:
    """Main job dashboard controller that orchestrates all dashboard components."""
    
    def __init__(self):
        self.data_manager = JobDataManager()
        self.renderer = JobDashboardRenderer()
        self.filter_manager = JobFilterManager()
        self.application_manager = JobApplicationManager()
    
    def display(self):
        """Main method to display the complete job dashboard."""
        user = st.session_state.current_user
        completion = calculate_profile_completion(user)

        # Show congratulations popup first (only for new hires that haven't been dismissed)
        self.renderer.render_congratulations_section(user["id"])

        # Render header
        self.renderer.render_header(user)

        # Check profile completion
        if self.renderer.render_profile_completion_warning(completion):
            return

        # Render active offers
        self.renderer.render_active_offers(user)

        # Get and validate jobs data
        all_jobs = self.data_manager.fetch_employer_jobs()
        if not all_jobs:
            st.info("📭 No job postings available at the moment. Please check back later!")
            return

        # Render filters and get filter values
        location_filter, selected_cat_lower, company_filter, salary_range = self.renderer.render_job_filters(all_jobs)

        # Apply filters
        filtered_jobs = self.filter_manager.apply_filters(
            all_jobs, location_filter, selected_cat_lower, company_filter, salary_range
        )

        st.info(f"**Found {len(filtered_jobs)} job(s) matching your filters**")

        # Split jobs by application status
        applied_set = self.application_manager.get_applied_jobs_set(user["id"])
        applied_jobs, not_applied_jobs = self.application_manager.split_jobs_by_application_status(
            filtered_jobs, applied_set
        )

        # Render job tabs
        self.renderer.render_job_tabs(applied_jobs, not_applied_jobs, user)

# Preserve original function signatures - NO CHANGES to existing code needed
def format_user_skills(job_types):
    """Wrapper function to maintain backward compatibility."""
    return JobSkillsFormatter.format_user_skills(job_types)

def _fetch_employer_jobs() -> List[Dict]:
    """Wrapper function to maintain backward compatibility."""
    manager = JobDataManager()
    return manager.fetch_employer_jobs()

def job_dashboard():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    dashboard = JobDashboard()
    dashboard.display()
