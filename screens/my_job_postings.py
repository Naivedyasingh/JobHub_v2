# screens/my_job_postings.py

import streamlit as st
from utils.job_management import JobManager
from datetime import datetime

def my_job_postings_page():
    """Display the My Job Posts page with all functionality integrated."""
    # Check if user is authenticated
    if not st.session_state.get("current_user"):
        st.error("Please login to access this page.")
        st.session_state.page = "login"
        st.rerun()
        return
    
    user = st.session_state.current_user
    
    # Initialize JobManager (using your existing utils/job_management.py)
    job_manager = JobManager()
    
    # Page header (NO back button here)
    st.title("📊 My Job Posts")
    st.markdown("---")
    
    # Main render logic
    try:
        posts = job_manager.get_employer_posts_with_applications(user["id"])
        
        if not posts:
            st.info("🎯 You haven't posted any jobs yet. Start hiring top talent!")
            if st.button("➕ Post Your First Job", use_container_width=True, type="primary"):
                st.session_state.page = "post_job"
                st.rerun()
            # NO back button here - will be at the end
        else:
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
                # NO back button here either - will be at the end
            else:
                # Sort posts by creation date (newest first)
                posts_sorted = sorted(posts, 
                                    key=lambda x: x.get('posted_date', ''), 
                                    reverse=True)
                
                # Render all job posts
                for post in posts_sorted:
                    render_post_card(post, job_manager, user["id"])
            
    except Exception as e:
        st.error(f"❌ Error loading job posts: {str(e)}")
        # NO back button here either - will be at the end
    
    # Back button ONLY at the VERY END (after everything else)
    st.markdown("---")
    st.markdown("")  # Add some spacing
    if st.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_final"):
        st.session_state.page = "hire_dashboard"
        st.rerun()

def render_post_card(post, job_manager, employer_id):
    """Render individual post card with applications and actions."""
    required = post.get('required_candidates', 1)
    hired = post.get('hired_count', 0)
    remaining = post.get('remaining_slots', 0)
    app_count = post.get('application_count', 0)
    post_status = post.get('post_status', 'open')
    
    # Determine status colors based on your JobManager logic
    status_config = {
        'open': {"color": "#28a745", "text": f"🟢 Open (0/{required})", "bg": "#d4edda"},
        'partially_filled': {"color": "#ffc107", "text": f"🟡 Partial ({hired}/{required})", "bg": "#fff3cd"},
        'filled': {"color": "#17a2b8", "text": f"🔵 Filled ({hired}/{required})", "bg": "#d1ecf1"},
        'auto_closed': {"color": "#6c757d", "text": "🔒 Auto Closed", "bg": "#e2e3e5"},
        'manually_closed': {"color": "#6c757d", "text": "🔒 Closed", "bg": "#e2e3e5"},
        'deleted': {"color": "#dc3545", "text": "🗑️ Deleted", "bg": "#f8d7da"}
    }
    
    config = status_config.get(post_status, status_config['open'])
    
    # Enhanced job card
    st.markdown(f"""
        <div style="border: 1px solid {config['color']}; border-left: 4px solid {config['color']};
                    border-radius: 12px; padding: 20px; margin: 15px 0; 
                    background-color: {config['bg']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #333; font-size: 20px;">{post.get('title', 'Untitled Job')}</h4>
                    <p style="margin: 8px 0; color: #666; font-size: 17px;">
                        📍 {post.get('location', 'N/A')} • 💰 ₹{post.get('salary', 0):,}/month • 💼 {post.get('job_type', 'N/A')}
                    </p>
                    <div style="margin: 0px 0; padding: 19px; background: white; border-radius: 6px;">
                        <p style="margin: 2px 0; color: #555; font-size: 15px;">
                            <strong>👥 Required:</strong> {required} • <strong>✅ Hired:</strong> {hired} • 
                            <strong>📨 Applications:</strong> {app_count} • <strong>⏳ Remaining:</strong> {remaining}
                        </p>
                    </div>
                </div>
                <div style="text-align: right; margin-left: 20px;">
                    <span style="background: {config['color']}; color: white; padding: 8px 15px; 
                                 border-radius: 20px; font-size: 12px; font-weight: bold;">
                        {config['text']}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons (only show for non-deleted posts)
    if post_status != 'deleted':
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            if st.button(f"👀 View Applications ({app_count})", 
                       key=f"view_apps_{post['id']}", use_container_width=True, type="secondary"):
                st.session_state[f"show_apps_{post['id']}"] = not st.session_state.get(f"show_apps_{post['id']}", False)
                st.rerun()
        
        with col2:
            if st.button("📊 Stats", key=f"stats_{post['id']}", use_container_width=True):
                show_job_stats(post)
        
        with col3:
            if not post.get('is_closed', False):
                if st.button("🔒 Close", key=f"close_{post['id']}", use_container_width=True, type="secondary"):
                    close_job_post(post, job_manager, employer_id)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{post['id']}", 
                       use_container_width=True, type="secondary", 
                       help="Delete this job posting"):
                show_delete_confirmation(post)
        
        # Show delete confirmation if needed
        if st.session_state.get(f"confirm_delete_{post['id']}", False):
            render_delete_confirmation(post, job_manager, employer_id)
        
        # Show applications if toggled
        if st.session_state.get(f"show_apps_{post['id']}", False):
            render_post_applications(post, job_manager, employer_id)

def show_delete_confirmation(post):
    """Show delete confirmation dialog."""
    st.session_state[f"confirm_delete_{post['id']}"] = True
    st.rerun()

def render_delete_confirmation(post, job_manager, employer_id):
    """Render delete confirmation dialog."""
    st.markdown("---")
    st.warning(f"⚠️ **Are you sure you want to delete '{post.get('title', 'this job')}'?**")
    st.markdown("This action cannot be undone. All applications for this job will also be affected.")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Yes, Delete", key=f"confirm_yes_{post['id']}", 
                   use_container_width=True, type="primary"):
            delete_job_post(post, job_manager, employer_id)
    
    with col2:
        if st.button("❌ Cancel", key=f"confirm_no_{post['id']}", 
                   use_container_width=True):
            st.session_state[f"confirm_delete_{post['id']}"] = False
            st.rerun()

def delete_job_post(post, job_manager, employer_id):
    """Delete a job posting using your JobManager."""
    success, message = job_manager.delete_job_posting(post['id'], employer_id)
    
    if success:
        st.success(f"✅ {message}")
        # Clear confirmation state
        if f"confirm_delete_{post['id']}" in st.session_state:
            del st.session_state[f"confirm_delete_{post['id']}"]
        st.rerun()
    else:
        st.error(f"❌ {message}")

def close_job_post(post, job_manager, employer_id):
    """Close a job posting using your JobManager."""
    success, message = job_manager.close_job_posting(post['id'], employer_id)
    
    if success:
        st.success(f"🔒 {message}")
        st.rerun()
    else:
        st.error(f"❌ {message}")

def show_job_stats(post):
    """Show detailed statistics for a job post."""
    with st.expander("📊 Detailed Statistics", expanded=True):
        # Progress bar based on your JobManager data
        required = post.get('required_candidates', 1)
        hired = post.get('hired_count', 0)
        if required > 0:
            progress = hired / required
            st.progress(progress, text=f"Hiring Progress: {hired}/{required}")

def render_post_applications(post, job_manager, employer_id):
    """Render applications for a specific post."""
    st.markdown("---")
    st.markdown("#### 📨 Applications for this Job")
    
    applications = post.get('applications', [])
    if not applications:
        st.info("📭 No applications received for this job yet.")
        return
    
    # Group applications by status
    pending_apps = [app for app in applications if app.get('status') == 'pending']
    accepted_apps = [app for app in applications if app.get('status') == 'accepted']
    rejected_apps = [app for app in applications if app.get('status') == 'rejected']
    
    # Show hiring progress for multi-candidate jobs
    required = post.get('required_candidates', 1)
    hired = post.get('hired_count', 0)
    if required > 1:
        progress = hired / required
        st.progress(progress, text=f"Hiring Progress: {hired}/{required} positions filled")
    
    # Show pending applications first
    if pending_apps:
        st.markdown("**⏳ Pending Applications:**")
        for app in pending_apps:
            render_application_item(app, post, job_manager, employer_id, allow_actions=True)
    
    # Show accepted applications
    if accepted_apps:
        st.markdown("**✅ Accepted Applications:**")
        for app in accepted_apps:
            render_application_item(app, post, job_manager, employer_id, allow_actions=False)
    
    # Show rejected applications (collapsible)
    if rejected_apps:
        with st.expander(f"❌ Rejected Applications ({len(rejected_apps)})", expanded=False):
            for app in rejected_apps:
                render_application_item(app, post, job_manager, employer_id, allow_actions=False)
    
    # Hide applications button
    if st.button("🔼 Hide Applications", key=f"hide_apps_{post['id']}", use_container_width=True):
        st.session_state[f"show_apps_{post['id']}"] = False
        st.rerun()

def render_application_item(app, post, job_manager, employer_id, allow_actions=True):
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
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
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
                    accept_application(app, post, job_manager, employer_id)
            else:
                st.button("✅ Accept", disabled=True, 
                        help="All positions filled", use_container_width=True)
        
        with col2:
            if st.button("❌ Reject", key=f"reject_{app.get('id')}_{post['id']}", 
                       use_container_width=True, type="secondary"):
                reject_application(app, job_manager)

def accept_application(application, post, job_manager, employer_id):
    """Accept an application using your JobManager."""
    success, message = job_manager.accept_application(
        application.get('id'), post['id'], employer_id
    )
    
    if success:
        st.success(message)
        st.rerun()
    else:
        st.error(message)

def reject_application(application, job_manager):
    """Reject an application using your JobManager."""
    success, message = job_manager.reject_application(application.get('id'))
    
    if success:
        st.success(message)
        st.rerun()
    else:
        st.error(message)
