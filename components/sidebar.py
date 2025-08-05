# components/sidebar.py

import streamlit as st
from utils.auth import calculate_profile_completion, update_user_profile


class UserAvatarRenderer:
    """Handles rendering of user avatars based on gender and role."""
    
    @staticmethod
    def get_job_seeker_avatar(gender):
        """Get avatar emoji for job seeker based on gender."""
        return {
            'Male': "👨‍💼",
            'Female': "👩‍💼"
        }.get(gender, "🧑‍💼")
    
    @staticmethod
    def get_employer_avatar(gender):
        """Get avatar emoji for employer based on gender."""
        return {
            'Male': "👨‍💼",
            'Female': "👩‍💼"
        }.get(gender, "🏢")


class StatusManager:
    """Handles job seeker availability status management."""
    
    def __init__(self):
        self.status_info = {
            'available': ('🟢', '#28a745', 'Ready to Work'),
            'busy': ('🟡', '#ffc107', 'Currently Busy'),
            'not_available': ('🔴', '#dc3545', 'Not Available')
        }
    
    def get_status_info(self, status):
        """Get status information (icon, color, text)."""
        return self.status_info.get(status, self.status_info['available'])
    
    def get_all_statuses(self):
        """Get all available status options."""
        return list(self.status_info.keys())
    
    def format_status_option(self, status):
        """Format status option for display."""
        icon, _, text = self.status_info[status]
        return f"{icon} {text}"


class ProfileRenderer:
    """Handles rendering of user profile components in sidebar."""
    
    def __init__(self):
        self.avatar_renderer = UserAvatarRenderer()
        self.status_manager = StatusManager()
    
    def render_job_seeker_profile(self, user):
        """Render job seeker profile with status management."""
        avatar = self.avatar_renderer.get_job_seeker_avatar(user.get('gender'))
        current_status = user.get('availability_status', 'available')
        icon, color, text = self.status_manager.get_status_info(current_status)

        # Render profile card
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 1rem;
            border: 2px solid {color};
            border-radius: 15px;
            background: linear-gradient(135deg, {color}15, {color}25);
        ">
            <div style="font-size: 4rem;">{avatar}</div>
            <h3>{user['name']}</h3>
            <p style="color: #666;">Job Seeker</p>
            <div style="
                background: {color};
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                margin: 5px 0;
            ">
                <strong>{icon} {text}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Status change selector
        self._render_status_changer(user, current_status)
    
    def render_employer_profile(self, user):
        """Render employer profile."""
        avatar = self.avatar_renderer.get_employer_avatar(user.get('gender'))
        color = '#6c757d'  # Light gray color for employers
        
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 1rem;
            border: 2px solid {color};
            border-radius: 15px;
            background: linear-gradient(135deg, {color}15, {color}25);
        ">
            <div style="font-size: 4rem;">{avatar}</div>
            <h3>{user['name']}</h3>
            <p style="color: #666;">Employer</p>
            <div style="
                background: {color};
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                margin: 5px 0;
            ">
                <strong>🏢 Hiring Manager</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_status_changer(self, user, current_status):
        """Render status change selector for job seekers."""
        all_statuses = self.status_manager.get_all_statuses()
        current_index = all_statuses.index(current_status)
        
        new_status = st.selectbox(
            "Change Status:",
            all_statuses,
            index=current_index,
            format_func=self.status_manager.format_status_option,
            key="sidebar_status_change"
        )
        
        if new_status != current_status:
            self._update_user_status(user, new_status)
    
    def _update_user_status(self, user, new_status):
        """Update user availability status."""
        updated_user = update_user_profile(user['id'], {'availability_status': new_status})
        if updated_user:
            st.session_state.current_user = updated_user
            st.success("Status updated!")
            st.rerun()


class ProfileCompletionRenderer:
    """Handles rendering of profile completion indicator."""
    
    @staticmethod
    def render_completion_indicator(user):
        """Render profile completion progress."""
        completion = calculate_profile_completion(user)
        
        st.markdown(f"""
        <div style=" margin: 10px 0; padding: 8px; background: #f0f2f6; border-radius: 8px;">
            <div style="font-size: 1rem; color: #666; margin-bottom: 2px;">Profile Completion</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #1f77b4;">{completion}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(completion / 100)


class NavigationRenderer:
    """Handles rendering of navigation buttons."""
    
    def render_common_navigation(self, user):
        """Render navigation buttons common to all users."""
        if st.button("🏠 Dashboard", use_container_width=True, key="sidebar_dashboard"):
            st.session_state.page = f"{user['role']}_dashboard"
            st.rerun()

        if st.button("👤 My Profile", use_container_width=True, key="sidebar_profile"):
            st.session_state.page = "profile"
            st.rerun()
    
    def render_job_seeker_navigation(self):
        """Render navigation buttons specific to job seekers."""
        if st.button("📋 My Applications", use_container_width=True, key="sidebar_my_applications"):
            st.session_state.page = "my_applications"
            st.rerun()
    
    def render_employer_navigation(self):
        """Render navigation buttons specific to employers."""
        if st.button("👥 Browse Job Seekers", use_container_width=True, key="sidebar_browse_seekers"):
            st.session_state.page = "browse_job_seekers"
            st.rerun()
        
        if st.button("📝 Post Job", use_container_width=True, key="sidebar_post_job"):
            st.session_state.page = "post_job"
            st.rerun()
        
        if st.button("📋 Applications", use_container_width=True, key="sidebar_view_applications"):
            st.session_state.page = "view_applications"
            st.rerun()
    
    def render_footer_navigation(self):
        """Render footer navigation (contact, logout)."""
        if st.button("📞 Contact Us", use_container_width=True, key="sidebar_contact"):
            st.session_state.page = "contact"
            st.rerun()

        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary", key="sidebar_logout"):
            st.session_state.current_user = None
            st.session_state.page = "home"
            st.rerun()


class SidebarRenderer:
    """Main sidebar renderer that orchestrates all sidebar components."""
    
    def __init__(self):
        self.profile_renderer = ProfileRenderer()
        self.completion_renderer = ProfileCompletionRenderer()
        self.navigation_renderer = NavigationRenderer()
    
    def render_sidebar(self):
        """Main method to render the complete sidebar."""
        # Don't render anything for guests
        if st.session_state.current_user is None:
            return

        user = st.session_state.current_user

        with st.sidebar:
            # Render user profile section
            if user['role'] == 'job':
                self.profile_renderer.render_job_seeker_profile(user)
            else:
                self.profile_renderer.render_employer_profile(user)

            # Render profile completion
            self.completion_renderer.render_completion_indicator(user)

            # Render navigation
            st.markdown("---")
            st.subheader("🧭 Navigation")

            # Common navigation
            self.navigation_renderer.render_common_navigation(user)

            # Role-specific navigation
            if user['role'] == 'job':
                self.navigation_renderer.render_job_seeker_navigation()
            else:
                self.navigation_renderer.render_employer_navigation()

            # Footer navigation
            self.navigation_renderer.render_footer_navigation()


# Create renderer instance for use by public function
_sidebar_renderer = SidebarRenderer()


# Public interface function - maintaining backward compatibility
def render_sidebar():
    """Render the sidebar component."""
    _sidebar_renderer.render_sidebar()
