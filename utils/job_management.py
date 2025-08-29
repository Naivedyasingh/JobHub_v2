from datetime import datetime
from db.models import JobPosting, Application
import streamlit as st

class JobManager:
    """Handles job posting management operations."""
    
    def __init__(self):
        self.job_model = JobPosting()
        self.app_model = Application()
    
    def get_employer_posts_with_applications(self, employer_id, include_deleted=False):
        """Get all posts for employer with application counts and details."""
        try:
            all_posts = list(self.job_model.list_by_user(employer_id))
            
            if not include_deleted:
                posts = [post for post in all_posts if post.get('status', 'active') != 'deleted']
            else:
                posts = all_posts
                
            all_applications = self.app_model.stream_all()
            
            posts_with_apps = []
            for post in posts:
                job_applications = [
                    app for app in all_applications 
                    if str(app.get("job_id")) == str(post.get("id"))
                ]
                
                required_candidates = post.get('required_candidates', 1)
                hired_count = post.get('hired_count', 0)
                is_closed = post.get('is_closed', False)
                
                remaining_slots = max(0, required_candidates - hired_count)
                post_status = self._determine_post_status(post, hired_count, required_candidates)
                
                post_data = dict(post)
                post_data.update({
                    'applications': job_applications,
                    'application_count': len(job_applications),
                    'hired_count': hired_count,
                    'required_candidates': required_candidates,
                    'remaining_slots': remaining_slots,
                    'is_closed': is_closed,
                    'post_status': post_status
                })
                posts_with_apps.append(post_data)
            
            return posts_with_apps
        except Exception as e:
            st.error(f"Error loading posts: {str(e)}")
            return []
    
    def _determine_post_status(self, post, hired_count, required_candidates):
        """Determine the current status of a job post."""
        if post.get('status') == 'deleted':
            return 'deleted'
        elif post.get('is_closed', False):
            if post.get('auto_closed', False):
                return 'auto_closed'
            return 'manually_closed'
        elif hired_count >= required_candidates:
            return 'filled'
        elif hired_count > 0:
            return 'partially_filled'
        else:
            return 'open'
    
    def accept_application(self, application_id, job_id, employer_id):
        """Accept an application and update job post status if needed."""
        try:
            success = self.app_model.update_status(application_id, "accepted")
            if not success:
                return False, "Failed to update application status"
            
            job = self.job_model.get_by_id(job_id)
            if not job or str(job.get('user_id')) != str(employer_id):
                return False, "Job not found or unauthorized"
            
            current_hired = job.get('hired_count', 0)
            new_hired_count = current_hired + 1
            required_candidates = job.get('required_candidates', 1)
            
            update_data = {'hired_count': new_hired_count}
            
            if new_hired_count >= required_candidates:
                update_data.update({
                    'is_closed': True,
                    'auto_closed': True,
                    'closed_date': datetime.now()
                })
            
            job_updated = self.job_model.update(job_id, update_data)
            
            if job_updated:
                if new_hired_count >= required_candidates:
                    return True, f"Application accepted! Job post automatically closed (all {required_candidates} positions filled)."
                else:
                    remaining = required_candidates - new_hired_count
                    return True, f"Application accepted! {remaining} more position(s) needed."
            else:
                return False, "Application accepted but failed to update job status"
                
        except Exception as e:
            return False, f"Error accepting application: {str(e)}"
    
    def reject_application(self, application_id):
        """Reject an application."""
        try:
            success = self.app_model.update_status(application_id, "rejected")
            return success, "Application rejected successfully" if success else "Failed to reject application"
        except Exception as e:
            return False, f"Error rejecting application: {str(e)}"
    
    def close_job_posting(self, job_id, employer_id):
        """Manually close a job posting."""
        try:
            job = self.job_model.get_by_id(job_id)
            if not job or str(job.get('user_id')) != str(employer_id):
                return False, "Job not found or unauthorized"
            
            update_data = {
                'is_closed': True,
                'closed_date': datetime.now(),
                'auto_closed': False
            }
            
            job_updated = self.job_model.update(job_id, update_data)
            
            if job_updated:
                return True, "Job posting closed successfully"
            else:
                return False, "Failed to close job posting"
                
        except Exception as e:
            return False, f"Error closing job posting: {str(e)}"
    
    def delete_job_posting(self, job_id, employer_id):
        """Delete a job posting (soft delete by marking as inactive)."""
        try:
            job = self.job_model.get_by_id(job_id)
            if not job or str(job.get('user_id')) != str(employer_id):
                return False, "Job not found or unauthorized"
            
            update_data = {'status': 'deleted'}
            
            job_updated = self.job_model.update(job_id, update_data)
            
            if job_updated:
                return True, "Job posting deleted successfully"
            else:
                return False, "Failed to delete job posting"
                
        except Exception as e:
            return False, f"Error deleting job posting: {str(e)}"
