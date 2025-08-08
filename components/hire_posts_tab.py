# components/hire_posts_tab.py

import streamlit as st
from utils.job_management import JobManager
from datetime import datetime

class HirePostsTab:
    """Handles the My Posts tab in hire dashboard."""
    
    def __init__(self):
        self.job_manager = JobManager()
    
    def render(self, employer_id):
        """Main render method for the posts tab."""
        try:
            posts = self.job_manager.get_employer_posts_with_applications(employer_id)
            
            if not posts:
                st.info("🎯 You haven't posted any jobs yet. Start hiring top talent!")
                if st.button("➕ Post Your First Job", use_container_width=True, type="primary"):
                    st.session_state.page = "post_job"
                    st.rerun()
                return
            
            # Enhanced header with stats
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"### 📋 Your Job Postings ({len(posts)} total)")
            with col2:
                open_posts = len([p for p in posts if p['post_status'] in ['open', 'partially_filled']])
                st.metric("Open Jobs", open_posts)
            with col3:
                filter_option = st.selectbox("Filter:", 
                                           ["All Posts", "Open", "Closed", "Filled"],
                                           key="posts_filter")
            
            # Filter posts based on selection
            if filter_option == "Open":
                posts = [p for p in posts if p['post_status'] in ['open', 'partially_filled']]
            elif filter_option == "Closed":
                posts = [p for p in posts if p['post_status'] in ['auto_closed', 'manually_closed']]
            elif filter_option == "Filled":
                posts = [p for p in posts if p['post_status'] in ['filled', 'auto_closed']]
            
            if not posts:
                st.info(f"📭 No {filter_option.lower()} posts found.")
                return
            
            # Sort posts by creation date (newest first)
            posts_sorted = sorted(posts, 
                                key=lambda x: x.get('posted_date', ''), 
                                reverse=True)
            
            for post in posts_sorted:
                self.render_post_card(post)
                
        except Exception as e:
            st.error(f"❌ Error loading job posts: {str(e)}")
    
    def render_post_card(self, post):
        """Render individual post card with applications and actions."""
        required = post.get('required_candidates', 1)
        hired = post.get('hired_count', 0)
        remaining = max(0, required - hired)
        app_count = post.get('application_count', 0)
        
        # Determine status and colors
        if post.get('is_closed', False):
            status_color = "#6c757d"
            status_text = "🔒 Closed"
            bg_color = "#e2e3e5"
        elif hired >= required:
            status_color = "#17a2b8"
            status_text = f"🔵 Filled ({hired}/{required})"
            bg_color = "#d1ecf1"
        elif hired > 0:
            status_color = "#ffc107"
            status_text = f"🟡 Partial ({hired}/{required})"
            bg_color = "#fff3cd"
        else:
            status_color = "#28a745"
            status_text = f"🟢 Open (0/{required})"
            bg_color = "#d4edda"
        
        # Enhanced job card with better spacing
        st.markdown(f"""
            <div style="border: 1px solid {status_color}; border-left: 4px solid {status_color};
                        border-radius: 12px; padding: 20px; margin: 15px 0; 
                        background-color: {bg_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333; font-size: 18px;">{post.get('title', 'Untitled Job')}</h4>
                        <p style="margin: 8px 0; color: #666; font-size: 14px;">
                            📍 {post.get('location', 'N/A')} • 💰 ₹{post.get('salary', 0):,}/month • 💼 {post.get('job_type', 'N/A')}
                        </p>
                        <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 6px;">
                            <p style="margin: 2px 0; color: #555; font-size: 13px;">
                                <strong>👥 Required:</strong> {required} • <strong>✅ Hired:</strong> {hired} • 
                                <strong>📨 Applications:</strong> {app_count} • <strong>⏳ Remaining:</strong> {remaining}
                            </p>
                        </div>
                    </div>
                    <div style="text-align: right; margin-left: 20px;">
                        <span style="background: {status_color}; color: white; padding: 8px 15px; 
                                     border-radius: 20px; font-size: 12px; font-weight: bold;">
                            {status_text}
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Enhanced action buttons
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            if st.button(f"👀 View Applications ({app_count})", 
                       key=f"view_apps_{post['id']}", use_container_width=True, type="secondary"):
                st.session_state[f"show_apps_{post['id']}"] = not st.session_state.get(f"show_apps_{post['id']}", False)
                st.rerun()
        
        with col2:
            if st.button("📊 Stats", key=f"stats_{post['id']}", use_container_width=True):
                self.show_job_stats(post)
        
        with col3:
            if not post.get('is_closed', False):
                if st.button("🔒 Close", key=f"close_{post['id']}", use_container_width=True, type="secondary"):
                    self.close_job_post(post)
        
        with col4:
            # ← NEW: Delete button with confirmation
            if st.button("🗑️ Delete", key=f"delete_{post['id']}", 
                       use_container_width=True, type="secondary", 
                       help="Delete this job posting"):
                self.show_delete_confirmation(post)
        
        # Show delete confirmation if needed
        if st.session_state.get(f"confirm_delete_{post['id']}", False):
            self.render_delete_confirmation(post)
        
        # Show applications if toggled
        if st.session_state.get(f"show_apps_{post['id']}", False):
            self.render_post_applications(post)
    
    def show_delete_confirmation(self, post):
        """Show delete confirmation dialog."""
        st.session_state[f"confirm_delete_{post['id']}"] = True
        st.rerun()
    
    def render_delete_confirmation(self, post):
        """Render delete confirmation dialog."""
        st.markdown("---")
        st.warning(f"⚠️ **Are you sure you want to delete '{post.get('title', 'this job')}'?**")
        st.markdown("This action cannot be undone. All applications for this job will also be affected.")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🗑️ Yes, Delete", key=f"confirm_yes_{post['id']}", 
                       use_container_width=True, type="primary"):
                self.delete_job_post(post)
        
        with col2:
            if st.button("❌ Cancel", key=f"confirm_no_{post['id']}", 
                       use_container_width=True):
                st.session_state[f"confirm_delete_{post['id']}"] = False
                st.rerun()
    
    def delete_job_post(self, post):
        """Delete a job posting."""
        employer_id = st.session_state.current_user["id"]
        success, message = self.job_manager.delete_job_posting(post['id'], employer_id)
        
        if success:
            st.success(f"✅ {message}")
            # Clear confirmation state
            if f"confirm_delete_{post['id']}" in st.session_state:
                del st.session_state[f"confirm_delete_{post['id']}"]
            st.rerun()
        else:
            st.error(f"❌ {message}")
    
    def close_job_post(self, post):
        """Close a job posting manually."""
        employer_id = st.session_state.current_user["id"]
        success, message = self.job_manager.close_job_posting(post['id'], employer_id)
        
        if success:
            st.success(f"🔒 Job posting closed successfully!")
            st.rerun()
        else:
            st.error("Failed to close job posting")
    
    def show_job_stats(self, post):
        """Show detailed statistics for a job post."""
        with st.expander("📊 Detailed Statistics", expanded=True):
            # col1, col2, col3, col4 = st.columns(4)
            
            # with col1:
            #     st.metric("Required", post['required_candidates'])
            # with col2:
            #     st.metric("Hired", post['hired_count'])
            # with col3:
            #     st.metric("Applications", post['application_count'])
            # with col4:
            #     st.metric("Remaining", post.get('remaining_slots', 0))
            
            # Progress bar
            if post['required_candidates'] > 0:
                progress = post['hired_count'] / post['required_candidates']
                st.progress(progress, text=f"Hiring Progress: {post['hired_count']}/{post['required_candidates']}")
    
    def render_post_applications(self, post):
        """Render applications for a specific post."""
        st.markdown("---")
        st.markdown("#### 📨 Applications for this Job")
        
        if not post.get('applications', []):
            st.info("📭 No applications received for this job yet.")
            return
        
        # Group applications by status
        pending_apps = [app for app in post['applications'] if app.get('status') == 'pending']
        accepted_apps = [app for app in post['applications'] if app.get('status') == 'accepted']
        rejected_apps = [app for app in post['applications'] if app.get('status') == 'rejected']
        
        # Show hiring progress for multi-candidate jobs
        if post['required_candidates'] > 1:
            progress = post['hired_count'] / post['required_candidates']
            st.progress(progress, text=f"Hiring Progress: {post['hired_count']}/{post['required_candidates']} positions filled")
        
        # Show pending applications first
        if pending_apps:
            st.markdown("**⏳ Pending Applications:**")
            for app in pending_apps:
                self.render_application_item(app, post, allow_actions=True)
        
        # Show accepted applications
        if accepted_apps:
            st.markdown("**✅ Accepted Applications:**")
            for app in accepted_apps:
                self.render_application_item(app, post, allow_actions=False)
        
        # Show rejected applications (collapsible)
        if rejected_apps:
            with st.expander(f"❌ Rejected Applications ({len(rejected_apps)})", expanded=False):
                for app in rejected_apps:
                    self.render_application_item(app, post, allow_actions=False)
        
        # Hide applications button
        if st.button("🔼 Hide Applications", key=f"hide_apps_{post['id']}", use_container_width=True):
            st.session_state[f"show_apps_{post['id']}"] = False
            st.rerun()
    
    def render_application_item(self, app, post, allow_actions=True):
        """Render individual application item."""
        name = app.get('applicant_name', 'N/A')
        email = app.get('applicant_email', 'N/A')
        phone = app.get('applicant_phone', 'N/A')
        experience = app.get('applicant_experience', 'N/A')
        skills = app.get('applicant_skills', 'Not specified')
        status = app.get('status', 'pending')
        
        status_colors = {"pending": "#ffc107", "accepted": "#28a745", "rejected": "#dc3545"}
        
        # Enhanced application card
        st.markdown(f"""
            <div style="border: 1px solid {status_colors.get(status, '#ffc107')}; 
                        border-radius: 8px; padding: 15px; margin: 10px 0; 
                        background-color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: #333; font-size: 16px;">{name}</h5>
                    <span style="background: {status_colors.get(status, '#ffc107')}; color: white; 
                                 padding: 4px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">
                        {status.upper()}
                    </span>
                </div>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">
                    📧 {email} | 📱 {phone}
                </p>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">
                    <strong>Experience:</strong> {experience}
                </p>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">
                    <strong>Skills:</strong> {skills}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Action buttons for pending applications
        if allow_actions and status == "pending":
            remaining_slots = post.get('remaining_slots', 0)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if remaining_slots > 0:
                    if st.button("✅ Accept", key=f"accept_{app.get('id')}_{post['id']}", 
                               use_container_width=True, type="primary"):
                        self.accept_application(app, post)
                else:
                    st.button("✅ Accept", disabled=True, 
                            help="All positions filled", use_container_width=True)
            
            with col2:
                if st.button("❌ Reject", key=f"reject_{app.get('id')}_{post['id']}", 
                           use_container_width=True, type="secondary"):
                    self.reject_application(app)
    
    def accept_application(self, application, post):
        """Accept an application."""
        employer_id = st.session_state.current_user["id"]
        success, message = self.job_manager.accept_application(
            application.get('id'), post['id'], employer_id
        )
        
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
    
    def reject_application(self, application):
        """Reject an application."""
        success, message = self.job_manager.reject_application(application.get('id'))
        
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
