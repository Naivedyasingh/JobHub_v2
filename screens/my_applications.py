# pages/my_applications.py
# ---------------------------------------------------
# Streamlit page: "My Applications & Offers"
# Safe version – handles NULL status, dates, etc.
# ---------------------------------------------------

import streamlit as st
from utils.applications import get_job_applications
from utils.offers import get_job_offers, update_offer_status
from datetime import datetime


class DateTimeHelper:
    """Handles datetime operations and formatting."""
    
    @staticmethod
    def fmt_date(val: object) -> str:
        """Return YYYY-MM-DD or blank if value is None/invalid."""
        if not val:
            return ""
        try:
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%d")
            return str(val)[:10]
        except Exception:
            return ""
    
    @staticmethod
    def safe_datetime(value):
        """Convert various datetime formats to datetime object"""
        if value is None:
            return datetime.now()
        if isinstance(value, datetime):
            return value  # Already a datetime object
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except:
            return datetime.now()  # Fallback


class StatusRenderer:
    """Handles status rendering and styling."""
    
    @staticmethod
    def render_status(status: str, expired: bool = False):
        """Return (border-colour, label, css-class)."""
        if expired:
            return "#6c757d", "⏰ Expired", "status-expired"
        return {
            "pending":  ("#ffc107", "🟡 Pending",   "status-pending"),
            "accepted": ("#28a745", "✅ Accepted",  "status-accepted"),
            "rejected": ("#dc3545", "❌ Declined",  "status-rejected"),
        }.get(status, ("#ffc107", "🟡 Pending", "status-pending"))


class ApplicationsDataManager:
    """Handles data operations for applications and offers."""
    
    def __init__(self):
        self.datetime_helper = DateTimeHelper()
    
    def get_user_applications(self, user_id):
        """Get all applications for a specific user."""
        applications = get_job_applications()
        return [a for a in applications if a.get("applicant_id") == user_id]
    
    def get_user_offers(self, user_id):
        """Get all offers for a specific user."""
        offers = get_job_offers()
        return [o for o in offers if o.get("job_seeker_id") == user_id]
    
    def filter_applications_by_status(self, applications, status_filter):
        """Filter applications by status."""
        if status_filter == "All":
            return applications
        
        status_filter_norm = status_filter.lower()
        return [
            a
            for a in applications
            if (str(a.get("status") or "pending").lower()) == status_filter_norm
        ]
    
    def sort_applications(self, applications, sort_by):
        """Sort applications by specified criteria."""
        def safe_sort_key(a):
            if sort_by == "Date Applied":
                date_val = a.get("applied_date")
                if date_val is None:
                    return datetime.min
                if isinstance(date_val, datetime):
                    return date_val
                try:
                    return datetime.fromisoformat(str(date_val))
                except:
                    return datetime.min
            elif sort_by == "Company":
                return a.get("employer_name") or ""
            else:  # Job Title
                return a.get("job_title") or ""
        
        return sorted(
            applications,
            key=safe_sort_key,
            reverse=(sort_by == "Date Applied"),
        )


class MyApplicationsRenderer:
    """Handles rendering of applications and offers UI components."""
    
    def __init__(self):
        self.datetime_helper = DateTimeHelper()
        self.status_renderer = StatusRenderer()
    
    def render_header(self):
        """Render page header."""
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:30px;">
                <h1 style="color:#2c3e50;font-size:2.2rem;margin-bottom:10px;">
                    📋 My Applications & Offers
                </h1>
            </div>""",
            unsafe_allow_html=True,
        )
    
    def render_custom_styles(self):
        """Render custom CSS styles."""
        st.markdown(
            """
            <style>
            .card{background:linear-gradient(135deg,#f8f9fa 0%,#fff 100%);
                  border-radius:15px;padding:20px;margin:15px 0;
                  box-shadow:0 4px 15px rgba(0,0,0,0.10);
                  border-left:6px solid;position:relative;
                  transition:transform .3s ease,box-shadow .3s ease;}
            .card:hover{transform:translateY(-5px);box-shadow:0 8px 25px rgba(0,0,0,0.15);}
            .job-title,.offer-title{font-weight:700;font-size:1.3rem;color:#2c3e50;margin-bottom:10px;}
            .job-company,.offer-company{font-size:1.1rem;color:#34495e;margin-bottom:8px;}
            .job-date{color:#7f8c8d;font-size:.95rem;margin-bottom:10px;}
            .status-badge{display:inline-block;padding:6px 12px;border-radius:20px;font-weight:600;margin-bottom:10px;}
            .status-pending{background:#fff3cd;color:#856404;border:1px solid #ffeaa7;}
            .status-accepted{background:#d4edda;color:#155724;border:1px solid #c3e6cb;}
            .status-rejected{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb;}
            .status-expired{background:#e2e3e5;color:#6c757d;border:1px solid #d6d8db;}
            .job-response{background:#e8f4fd;border-left:4px solid #3498db;padding:10px;
                           border-radius:5px;margin-top:10px;font-style:italic;color:#2c3e50;}
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    def render_offer_card(self, offer: dict, col):
        """Render individual offer card."""
        expires = self.datetime_helper.safe_datetime(offer.get("expires_at"))
        is_expired = datetime.now() > expires
        border_col, status_txt, status_cls = self.status_renderer.render_status(offer.get("status", "pending"), is_expired)

        with col:
            st.markdown(
                f"""
                <div class="card" style="border-left-color:{border_col};">
                    <div class="offer-title">💼 {offer.get('job_title')}</div>
                    <div class="offer-company">🏢 {offer.get('employer_name')}</div>
                    <div>💰 <strong>Salary:</strong> ₹{offer.get('salary_offered')}</div>
                    <div>📍 <strong>Location:</strong> {offer.get('location')}</div>
                    <div>📅 <strong>Start Date:</strong> {offer.get('start_date')}</div><br>
                    <div class="status-badge {status_cls}">{status_txt}</div>
                """,
                unsafe_allow_html=True,
            )

            # Buttons side by side using columns
            if offer.get("status") == "pending" and not is_expired:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✅ Accept", key=f"accept_{offer['id']}", type="primary", use_container_width=True):
                        update_offer_status(offer["id"], "accepted", "Offer accepted")
                        st.success("Offer accepted!")
                        st.rerun()
                with btn_col2:
                    if st.button("❌ Decline", key=f"decline_{offer['id']}", use_container_width=True):
                        update_offer_status(offer["id"], "rejected", "Offer declined")
                        st.info("Offer declined.")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
    
    def render_application_card(self, app: dict, col):
        """Render individual application card."""
        border_col, status_cls, status_txt = {
            "pending":  ("#ffc107", "status-pending",  "🟡 Under Review"),
            "accepted": ("#28a745", "status-accepted", "✅ Accepted"),
            "rejected": ("#dc3545", "status-rejected", "❌ Rejected"),
        }.get(app.get("status"), ("#ffc107", "status-pending", "🟡 Under Review"))

        resp = app.get("response_message", "")

        with col:
            st.markdown(
                f"""
                <div class="card" style="border-left-color:{border_col};">
                    <div class="job-title">💼 {app.get('job_title','N/A')}</div>
                    <div class="job-company">🏢 {app.get('employer_name','N/A')}</div>
                    <div class="job-date">📅 Applied: {self.datetime_helper.fmt_date(app.get('applied_date'))}</div>
                    <div class="status-badge {status_cls}">{status_txt}</div>
                    {f'<div class="job-response">💬 <strong>Response:</strong> {resp}</div>' if resp else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    def render_offers_tab(self, my_offers):
        """Render the offers tab content."""
        if my_offers:
            for i in range(0, len(my_offers), 2):
                cols = st.columns(2, gap="large")
                self.render_offer_card(my_offers[i], cols[0])
                if i + 1 < len(my_offers):
                    self.render_offer_card(my_offers[i + 1], cols[1])
                else:
                    with cols[1]:
                        st.markdown("<div style='height:200px'></div>", unsafe_allow_html=True)
        else:
            st.info("No job offers received yet.")
    
    def render_applications_tab(self, my_applications, data_manager):
        """Render the applications tab content."""
        if my_applications:
            # Render filters
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Accepted", "Rejected"])
            with col2:
                sort_by = st.selectbox("Sort By", ["Date Applied", "Company", "Job Title"])

            # Apply filters and sorting
            filtered = data_manager.filter_applications_by_status(my_applications, status_filter)
            filtered = data_manager.sort_applications(filtered, sort_by)

            # Render cards
            for i in range(0, len(filtered), 2):
                cols = st.columns(2, gap="large")
                self.render_application_card(filtered[i], cols[0])
                if i + 1 < len(filtered):
                    self.render_application_card(filtered[i + 1], cols[1])
                else:
                    with cols[1]:
                        st.markdown("<div style='height:200px;'></div>", unsafe_allow_html=True)
        else:
            st.info("You haven't applied for any jobs yet.")


class MyApplicationsPage:
    """Main controller for my applications page."""
    
    def __init__(self):
        self.data_manager = ApplicationsDataManager()
        self.renderer = MyApplicationsRenderer()
    
    def display(self):
        """Main method to display the complete my applications page."""
        user = st.session_state.current_user

        # Render header and styles
        self.renderer.render_header()
        self.renderer.render_custom_styles()

        # Get data
        my_applications = self.data_manager.get_user_applications(user["id"])
        my_offers = self.data_manager.get_user_offers(user["id"])

        # Create tabs
        tab_offers, tab_apps = st.tabs(
            [f"💼 Job Offers ({len(my_offers)})", f"📤 My Applications ({len(my_applications)})"]
        )

        # Render tabs content
        with tab_offers:
            self.renderer.render_offers_tab(my_offers)

        with tab_apps:
            self.renderer.render_applications_tab(my_applications, self.data_manager)


# Preserve original function signatures - NO CHANGES to existing code needed
def fmt_date(val: object) -> str:
    """Wrapper function to maintain backward compatibility."""
    return DateTimeHelper.fmt_date(val)


def safe_datetime(value):
    """Wrapper function to maintain backward compatibility."""
    return DateTimeHelper.safe_datetime(value)


def render_status(status: str, expired: bool = False):
    """Wrapper function to maintain backward compatibility."""
    return StatusRenderer.render_status(status, expired)


def my_applications_page() -> None:
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = MyApplicationsPage()
    page.display()
