# pages/view_applications.py
# -----------------------------------------------------------
# Employer view – Manage applications sent to their postings
# -----------------------------------------------------------

import html
from datetime import datetime, timedelta
import streamlit as st
from utils.applications import (
    get_job_applications,
    update_application_status,
)


class ApplicationDataProcessor:
    """Handles processing and sanitization of application data."""
    
    @staticmethod
    def clean(text: object) -> str:
        """Return safe HTML-escaped string or placeholder."""
        if not text or str(text).lower() in ("none", "null", ""):
            return "Not provided"
        return html.escape(str(text).strip())
    
    @staticmethod
    def safe_skills(value: object) -> str:
        """Return a comma-separated skills string."""
        if not value:
            return "Not provided"
        if isinstance(value, list):
            return ", ".join(map(str, value))
        try:
            import json
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return ", ".join(map(str, parsed))
        except Exception:
            pass
        return str(value)
    
    @staticmethod
    def fmt_date(val: object) -> str:
        """Pretty relative date (Today, 3 days ago …)."""
        if not val:
            return "Not available"
        try:
            dt = val if isinstance(val, datetime) else datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        except Exception:
            return str(val)[:10]

        diff: timedelta = datetime.now() - dt
        if diff.days == 0:
            rel = "Today"
        elif diff.days == 1:
            rel = "Yesterday"
        elif diff.days < 7:
            rel = f"{diff.days} days ago"
        else:
            rel = f"{diff.days // 7} weeks ago"

        return dt.strftime("%Y-%m-%d") + f" ({rel})"


class ApplicationDataManager:
    """Handles application data operations and filtering."""
    
    def get_employer_applications(self, employer_id):
        """Get all applications for a specific employer."""
        apps = get_job_applications()
        return [
            a for a in apps
            if str(a.get("employer_id")) == str(employer_id)
        ]
    
    def filter_applications_by_status(self, applications, status):
        """Filter applications by status."""
        return [
            a for a in applications
            if (a.get("status") or "pending") == status
        ]
    
    def get_application_counts(self, applications):
        """Get counts of applications by status."""
        return {
            'pending': sum(a.get('status') in (None, '', 'pending') for a in applications),
            'accepted': sum(a.get('status') == 'accepted' for a in applications),
            'rejected': sum(a.get('status') == 'rejected' for a in applications)
        }
    
    def update_application_status(self, app_id, status, message):
        """Update application status."""
        return update_application_status(app_id, status, message)


class ApplicationCardRenderer:
    """Handles rendering of individual application cards."""
    
    def __init__(self):
        self.data_processor = ApplicationDataProcessor()
        self.status_config = {
            "pending":  ("🟡", "#fff3cd", "#856404", "#E79E0C"),
            "accepted": ("✅", "#d4edda", "#155724", "#0ad741"),
            "rejected": ("❌", "#f8d7da", "#721c24", "#f01b30"),
        }
    
    def get_status_styling(self, status):
        """Get styling configuration for application status."""
        status = (status or "pending").lower()
        return self.status_config.get(status, self.status_config["pending"])
    
    def render_card_html(self, app):
        """Render the HTML card for an application."""
        # Clean fields
        name = self.data_processor.clean(app.get("applicant_name"))
        title = self.data_processor.clean(app.get("job_title"))
        phone = self.data_processor.clean(app.get("applicant_phone"))
        skills = self.data_processor.safe_skills(app.get("applicant_skills"))
        salary = self.data_processor.clean(app.get("expected_salary"))
        applied = self.data_processor.fmt_date(app.get("applied_date"))

        # Get status styling
        icon, badge_bg, badge_color, card_bg = self.get_status_styling(app.get("status"))
        status = (app.get("status") or "pending").lower()

        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#f8f9fa 0%,#ffffff 100%);
                        border-radius:15px;padding:20px;margin:15px 0;
                        box-shadow:0 4px 15px rgba(0,0,0,.10);
                        border-left:5px solid {card_bg};">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h4 style="margin:0;">👤 {name}</h4>
                    <span style="background:{badge_bg};color:{badge_color};
                                 padding:2px 10px;border-radius:8px;">{icon} {status.title()}</span>
                </div>
                <p style="color:#6c757d;margin:6px 0;">💼 <strong>{title}</strong></p>
                <div style="font-size:.87rem;color:#495057;line-height:1.5;">
                    <div>📅 <strong>Applied:</strong> {applied}</div>
                    <div>📞 {phone}</div>
                    <div>🛠️ {skills}</div>
                    <div>💰 ₹{salary}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    def render_details_expander(self, app):
        """Render the details expander for an application."""
        with st.expander("📋 More Details"):
            email = self.data_processor.clean(app.get("applicant_email"))
            exp = self.data_processor.clean(app.get("applicant_experience"))
            applied = self.data_processor.fmt_date(app.get("applied_date"))
            phone = self.data_processor.clean(app.get("applicant_phone"))
            
            st.markdown(f"**✉️ Email:** {email}")
            st.markdown(f"**📈 Experience:** {exp}")
            st.markdown(f"**📅 Applied Date:** {applied}")
            st.code(f"Phone: {phone}\nEmail: {email}", language=None)
    
    def render_action_buttons(self, app, data_manager):
        """Render action buttons for pending applications."""
        c1, c2, c3 = st.columns(3)
        
        email = self.data_processor.clean(app.get("applicant_email"))
        phone = self.data_processor.clean(app.get("applicant_phone"))
        
        if c1.button("✅ Accept", key=f"acc{app['id']}", use_container_width=True):
            data_manager.update_application_status(app["id"], "accepted", "Accepted")
            st.success("✅ Accepted!")
            st.rerun()
        if c2.button("❌ Reject", key=f"rej{app['id']}", use_container_width=True):
            data_manager.update_application_status(app["id"], "rejected", "Rejected")
            st.info("❌ Rejected")
            st.rerun()
        if c3.button("📞 Contact", key=f"con{app['id']}", use_container_width=True):
            st.success(f"📱 {phone}")
            st.success(f"✉️ {email}")


class ApplicationGridRenderer:
    """Handles rendering of application grids and layouts."""
    
    def __init__(self):
        self.card_renderer = ApplicationCardRenderer()
    
    def render_application_card(self, app, show_actions, data_manager):
        """Render a complete application card with all components."""
        self.card_renderer.render_card_html(app)
        self.card_renderer.render_details_expander(app)
        
        if show_actions:
            self.card_renderer.render_action_buttons(app, data_manager)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    def render_applications_grid(self, apps, show_actions, data_manager):
        """Render applications in a grid layout."""
        if not apps:
            st.info("No applications here.")
            return

        for i in range(0, len(apps), 2):
            cols = st.columns(2, gap="medium")
            for col, app in zip(cols, apps[i:i + 2]):
                with col:
                    self.render_application_card(app, show_actions, data_manager)

            if len(apps[i:i + 2]) == 1:  # keep row heights even
                with cols[1]:
                    st.markdown("<div style='height:250px'></div>", unsafe_allow_html=True)


class ViewApplicationsRenderer:
    """Handles rendering of the main view applications page."""
    
    def __init__(self):
        self.grid_renderer = ApplicationGridRenderer()
    
    def render_header(self):
        """Render page header."""
        st.markdown(
            "<h2 style='text-align:center;color:#1f77b4;'>📋 Manage Applications</h2><br>",
            unsafe_allow_html=True,
        )
    
    def render_tabs(self, applications, data_manager):
        """Render tabs for different application statuses."""
        counts = data_manager.get_application_counts(applications)
        
        tabs = st.tabs([
            f"🟡 Pending ({counts['pending']})",
            f"🟢 Accepted ({counts['accepted']})",
            f"🔴 Rejected ({counts['rejected']})",
        ])
        
        statuses = ["pending", "accepted", "rejected"]
        for tab, status in zip(tabs, statuses):
            with tab:
                subset = data_manager.filter_applications_by_status(applications, status)
                show_actions = (status == "pending")
                self.grid_renderer.render_applications_grid(subset, show_actions, data_manager)


class ViewApplicationsPage:
    """Main controller for view applications page."""
    
    def __init__(self):
        self.data_manager = ApplicationDataManager()
        self.renderer = ViewApplicationsRenderer()
    
    def display(self):
        """Main method to display the complete view applications page."""
        # Render header
        self.renderer.render_header()
        
        # Get employer applications
        employer_id = st.session_state.current_user["id"]
        applications = self.data_manager.get_employer_applications(employer_id)
        
        if not applications:
            st.info("No applications received yet.")
            return
        
        # Render tabs with applications
        self.renderer.render_tabs(applications, self.data_manager)


# Preserve original function signatures - NO CHANGES to existing code needed
def clean(text: object) -> str:
    """Wrapper function to maintain backward compatibility."""
    return ApplicationDataProcessor.clean(text)


def safe_skills(value: object) -> str:
    """Wrapper function to maintain backward compatibility."""
    return ApplicationDataProcessor.safe_skills(value)


def fmt_date(val: object) -> str:
    """Wrapper function to maintain backward compatibility."""
    return ApplicationDataProcessor.fmt_date(val)


def display_grid(apps: list, show_actions: bool) -> None:
    """Wrapper function to maintain backward compatibility."""
    data_manager = ApplicationDataManager()
    grid_renderer = ApplicationGridRenderer()
    grid_renderer.render_applications_grid(apps, show_actions, data_manager)


def display_card(app: dict, show_actions: bool) -> None:
    """Wrapper function to maintain backward compatibility."""
    data_manager = ApplicationDataManager()
    grid_renderer = ApplicationGridRenderer()
    grid_renderer.render_application_card(app, show_actions, data_manager)


def view_applications_page() -> None:
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = ViewApplicationsPage()
    page.display()
