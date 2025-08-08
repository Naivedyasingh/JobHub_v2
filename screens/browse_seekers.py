# pages/browse_seekers.py

import datetime
import streamlit as st
from utils.auth import calculate_profile_completion
from utils.offers import get_job_offers
from db.models import User
from datetime import datetime as dt

class DateHelper:
    """Handles date parsing and validation operations."""
    
    @staticmethod
    def safe_parse_date(date_value):
        """Safely parse date value, return current datetime if invalid"""
        if not date_value or str(date_value).lower() in ('none', 'null', ''):
            return dt.now()
        try:
            return dt.fromisoformat(str(date_value))
        except (ValueError, TypeError):
            return dt.now()

class SkillsProcessor:
    """Handles processing and parsing of skills data."""
    
    @staticmethod
    def split_skills(value):
        """
        Return a clean list of skills regardless of the stored format.
        • JSON list → list
        • comma-separated string → list
        • already a list → list
        """
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # handle JSON-encoded list first
            import json
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # fall back to comma-separated text
            return [s.strip() for s in value.split(",") if s.strip()]
        return []

class JobSeekersDataManager:
    """Handles data operations for job seekers."""
    
    def __init__(self):
        self.user_model = User
        self.skills_processor = SkillsProcessor()
    
    def get_job_seekers(self):
        """Return all job seekers whose profile‐completion is 100%, fetched from MySQL."""
        with self.user_model.db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE role=%s", ("job",))
            users = cur.fetchall()
        return [u for u in users if calculate_profile_completion(u) == 100]
    
    def get_all_skills_from_seekers(self, seekers):
        """Extract all unique skills from job seekers."""
        seeker_skills_set = set()
        for seeker in seekers:
            skills = self.skills_processor.split_skills(seeker.get("job_types"))
            seeker_skills_set.update(s.strip().title() for s in skills if s.strip())
        return seeker_skills_set

class JobSeekersFilter:
    """Handles filtering logic for job seekers."""
    
    def __init__(self):
        self.skills_processor = SkillsProcessor()
    
    def apply_skill_filter(self, seekers, skill_filter):
        """Apply skill-based filtering."""
        if skill_filter == "All":
            return seekers
        return [
            s for s in seekers 
            if skill_filter.lower() in [skill.lower() for skill in self.skills_processor.split_skills(s.get("job_types"))]
        ]
    
    def apply_experience_filter(self, seekers, exp_filter):
        """Apply experience-based filtering."""
        if exp_filter == "All":
            return seekers
        return [s for s in seekers if s.get("experience") == exp_filter]
    
    def apply_availability_filter(self, seekers, avail_filter):
        """Apply availability-based filtering."""
        if avail_filter == "All":
            return seekers
        return [s for s in seekers if s.get("availability_status", "available") == avail_filter]
    
    def apply_all_filters(self, seekers, skill_filter, exp_filter, avail_filter):
        """Apply all filters in sequence."""
        filtered = self.apply_skill_filter(seekers, skill_filter)
        filtered = self.apply_experience_filter(filtered, exp_filter)
        filtered = self.apply_availability_filter(filtered, avail_filter)
        return filtered

class OfferStatusManager:
    """Handles offer status and timing logic."""
    
    def __init__(self):
        self.date_helper = DateHelper()
    
    def get_recent_offer_info(self, all_offers, employer_id, seeker_id):
        """Get information about recent offers between employer and seeker."""
        for offer in all_offers:
            if (str(offer.get("employer_id")) == str(employer_id) and 
                str(offer.get("job_seeker_id")) == str(seeker_id)):
                
                offer_date = self.date_helper.safe_parse_date(offer.get("offered_date"))
                time_delta = datetime.datetime.now() - offer_date
                offer_status = offer.get("status", "pending")
                
                return {
                    'exists': True,
                    'time_delta': time_delta,
                    'status': offer_status,
                    'hours_ago': int(time_delta.total_seconds() // 3600),
                    'days_ago': time_delta.days,
                    'is_expired': time_delta.total_seconds() > 24 * 3600,  # > 1 day
                    'is_pending': offer_status == "pending"
                }
        
        return {'exists': False}
    
    def should_disable_offer_button(self, offer_info):
        """Determine if offer button should be disabled."""
        if not offer_info['exists']:
            return False  # No recent offer, enable button
        
        if not offer_info['is_pending']:
            return False  # Offer was responded to, enable button
        
        if offer_info['is_expired']:
            return False  # Offer expired (>24h), enable button
        
        return True  # Recent pending offer exists, disable button

class JobSeekersRenderer:
    """Handles rendering of job seekers UI components."""
    
    def __init__(self):
        self.date_helper = DateHelper()
        self.skills_processor = SkillsProcessor()
        self.offer_manager = OfferStatusManager()  # ← NEW
    
    def render_header(self):
        """Render page header."""
        st.title("👥 Browse Job Seekers")
        st.subheader("Find the perfect candidate for your job")
    
    def render_filters(self, skills_set):
        """Render filter controls and return selected values."""
        cols = st.columns(3)
        with cols[0]:
            skill_filter = st.selectbox(
                "Filter by Skills",
                ["All"] + sorted(skills_set),
                key="skill_filter",
            )
        with cols[1]:
            exp_filter = st.selectbox(
                "Experience",
                ["All", "Fresher", "1-2 years", "2-5 years", "5+ years"],
                key="experience_filter",
            )
        with cols[2]:
            avail_filter = st.selectbox(
                "Availability",
                ["All", "available", "busy", "not_available"],
                key="availability_filter",
            )
        return skill_filter, exp_filter, avail_filter
    
    def get_status_styling(self, status):
        """Get styling information for seeker status."""
        if status == "available":
            return "🟢", "#d4edda", "#155724", "#4CAF50", "Available"
        elif status == "busy":
            return "🟡", "#fff3cd", "#856404", "#FF9800", "Busy"
        else:
            return "🔴", "#f8d7da", "#721c24", "#f44336", "Not Available"
    
    def render_seeker_card(self, seeker):
        """Render individual seeker card with styling."""
        status = seeker.get("availability_status", "available")
        name = str(seeker["name"])
        phone = str(seeker.get("phone", "N/A"))
        experience = str(seeker.get("experience", "Not specified"))
        salary = str(seeker.get("expected_salary", "Not specified"))
        city = str(seeker.get("city", "Not specified"))

        icon, badge_bg, badge_color, card_bg, status_txt = self.get_status_styling(status)

        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#f8f9fa 0%,#ffffff 100%);
                border-radius:18px;padding:30px;margin:20px 0;
                box-shadow:0 6px 20px rgba(0,0,0,0.15);
                border-left:6px solid {card_bg};min-height:180px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                <h3 style="margin:0;font-size:1.3rem;font-weight:600;">👤 {name}</h3>
                <span style="background:{badge_bg};color:{badge_color};padding:6px 12px;
                              border-radius:12px;font-weight:bold;font-size:0.9rem;">
                  {icon} {status_txt}
                </span>
              </div>
              <div style="font-size:0.95rem;color:#495057;line-height:1.8;">
                <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:20px;">
                  <div>
                    <strong style="color:#666;font-size:1rem;">💼 Experience</strong><br>
                    <div style="margin-top:8px;">⏱️ {experience}</div>
                    <div style="margin-top:5px;">💰 ₹{salary}</div>
                  </div>
                  <div style="border-left:3px solid #e0e0e0;height:80px;"></div>
                  <div>
                    <strong style="color:#666;font-size:1rem;">📞 Contact</strong><br>
                    <div style="margin-top:8px;">📱 {phone}</div>
                    <div style="margin-top:5px;">🏙️ {city}</div>
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    def render_action_buttons(self, seeker, user, all_offers):
        """Render action buttons for each seeker with improved offer logic."""
        status = seeker.get("availability_status", "available")
        
        # Get offer information using the new manager
        offer_info = self.offer_manager.get_recent_offer_info(
            all_offers, user["id"], seeker["id"]
        )
        
        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if status != "available":
                st.button(
                    "❌ Not Available",
                    disabled=True,
                    use_container_width=True,
                    key=f"disabled_{seeker['id']}",
                )
            else:
                should_disable = self.offer_manager.should_disable_offer_button(offer_info)
                
                if should_disable:
                    # Show time-based message for recent pending offers
                    if offer_info['hours_ago'] < 24:
                        st.button(
                            f"⌛ Offered ({offer_info['hours_ago']}h ago)",
                            disabled=True,
                            use_container_width=True,
                            key=f"recent_{seeker['id']}",
                            help="Wait 24 hours before sending another offer"
                        )
                    else:
                        # This shouldn't happen due to logic, but safety fallback
                        st.button(
                            "💼 Offer Job",
                            type="primary",
                            use_container_width=True,
                            key=f"offer_{seeker['id']}",
                        )
                else:
                    # Show different button text based on offer history
                    button_text = "💼 Offer Job"
                    if offer_info['exists']:
                        if offer_info['is_expired']:
                            button_text = "🔄 Offer Again"  # Previous offer expired
                        elif not offer_info['is_pending']:
                            button_text = "🔄 New Offer"    # Previous offer was responded to
                    
                    if st.button(
                        button_text,
                        type="primary",
                        use_container_width=True,
                        key=f"offer_{seeker['id']}",
                    ):
                        st.session_state.selected_candidate = seeker
                        st.session_state.page = "offer_job"
                        st.rerun()

        with action_col2:
            details_key = f"show_details_{seeker['id']}"
            if details_key not in st.session_state:
                st.session_state[details_key] = False
            if st.button(
                "👁️ Details",
                use_container_width=True,
                key=f"details_btn_{seeker['id']}",
            ):
                st.session_state[details_key] = not st.session_state[details_key]
    
    def render_seeker_details(self, seeker):
        """Render detailed information about a seeker."""
        details_key = f"show_details_{seeker['id']}"
        if st.session_state.get(details_key, False):
            with st.expander("📋 Full Details", expanded=True):
                tab1, tab2, tab3 = st.tabs(["📧 Contact", "💼 Professional", "🚨 Emergency"])

                with tab1:
                    st.write(f"**📧 Email:** {seeker.get('email', 'N/A')}")
                    st.write(f"**📱 Phone:** {seeker.get('phone', 'N/A')}")
                    st.write(f"**🏠 Address:** {seeker.get('address', 'Not provided')}")
                    st.write(f"**🏙️ City:** {seeker.get('city', 'Not specified')}")

                with tab2:
                    st.write(f"**🎓 Education:** {seeker.get('education', 'Not specified')}")
                    st.write(f"**⏱️ Experience:** {seeker.get('experience', 'Not specified')}")
                    st.write(f"**💰 Expected Salary:** {seeker.get('expected_salary', 'Not specified')}")
                    st.write(f"**📅 Notice Period:** {seeker.get('notice_period', 'Not specified')}")
                    st.write("**🛠️ All Skills:**")
                    skills = self.skills_processor.split_skills(seeker.get("job_types"))
                    st.write("\n".join(f"• {s}" for s in skills) if skills else "No skills listed")

                with tab3:
                    st.write(f"**👤 Name:** {seeker.get('emergency_name', 'Not provided')}")
                    st.write(f"**📞 Contact:** {seeker.get('emergency_contact', 'Not provided')}")
    
    def render_seekers_grid(self, filtered_seekers, user, all_offers):
        """Render grid of seeker cards."""
        for i in range(0, len(filtered_seekers), 2):
            cols = st.columns(2, gap="medium")
            for j, col in enumerate(cols):
                if i + j >= len(filtered_seekers):
                    continue

                seeker = filtered_seekers[i + j]
                with col:
                    self.render_seeker_card(seeker)
                    self.render_action_buttons(seeker, user, all_offers)
                    self.render_seeker_details(seeker)

class BrowseJobSeekersPage:
    """Main controller for browse job seekers page."""
    
    def __init__(self):
        self.data_manager = JobSeekersDataManager()
        self.filter_manager = JobSeekersFilter()
        self.renderer = JobSeekersRenderer()
    
    def display(self):
        """Main method to display the complete browse job seekers page."""
        user = st.session_state.current_user

        # Render header
        self.renderer.render_header()

        # Get data
        seekers = self.data_manager.get_job_seekers()
        if not seekers:
            st.info("No job seekers with complete profiles found.")
            return

        # Get skills for filters
        skills_set = self.data_manager.get_all_skills_from_seekers(seekers)

        # Render filters
        skill_filter, exp_filter, avail_filter = self.renderer.render_filters(skills_set)

        # Apply filters
        filtered_seekers = self.filter_manager.apply_all_filters(
            seekers, skill_filter, exp_filter, avail_filter
        )

        st.write(f"**Found {len(filtered_seekers)} job seekers**")

        # Get offers data
        all_offers = get_job_offers()

        # Render seekers grid
        self.renderer.render_seekers_grid(filtered_seekers, user, all_offers)

# Preserve original function signatures - NO CHANGES to existing code needed
def safe_parse_date(date_value):
    """Wrapper function to maintain backward compatibility."""
    return DateHelper.safe_parse_date(date_value)

def split_skills(value):
    """Wrapper function to maintain backward compatibility."""
    return SkillsProcessor.split_skills(value)

def get_job_seekers():
    """Wrapper function to maintain backward compatibility."""
    manager = JobSeekersDataManager()
    return manager.get_job_seekers()

def browse_job_seekers_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = BrowseJobSeekersPage()
    page.display()
