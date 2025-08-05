# pages/contact.py

import streamlit as st
from datetime import datetime


class ContactInfo:
    """Handles contact information data and formatting."""
    
    def __init__(self):
        self.phone = "+91-9876543210"
        self.email = "support@jobHub.com"
        self.address = "IT park near yash technologies, Indore, India"
        self.business_hours = {
            "Monday - Friday": "9:00 AM - 6:00 PM",
            "Saturday": "10:00 AM - 4:00 PM",
            "Sunday": "Closed"
        }
    
    def get_contact_details(self):
        """Return formatted contact details."""
        return f"""
        **Phone:** {self.phone}  
        **Email:** {self.email}  
        **Address:** {self.address}
        
        **Business Hours:**  
        Monday - Friday: {self.business_hours["Monday - Friday"]}  
        Saturday: {self.business_hours["Saturday"]}  
        Sunday: {self.business_hours["Sunday"]}
        """


class ReviewsManager:
    """Handles customer reviews and testimonials."""
    
    def __init__(self):
        self.reviews = [
            {
                "name": "Priya Sharma",
                "role": "Job Seeker",
                "rating": 5,
                "review": "Found my dream job within a week! The platform is user-friendly and employers respond quickly.",
                "date": "2024-01-15"
            },
            {
                "name": "Rajesh Kumar",
                "role": "Employer",
                "rating": 5,
                "review": "Excellent platform for hiring skilled workers. Found the perfect candidate for our company.",
                "date": "2024-01-10"
            },
            {
                "name": "Anita Patel",
                "role": "Job Seeker",
                "rating": 4,
                "review": "Great experience! Got multiple job offers and the support team is very helpful.",
                "date": "2024-01-08"
            },
            {
                "name": "Vikram Singh",
                "role": "Employer",
                "rating": 5,
                "review": "JobConnect made our recruitment process so much easier. Highly recommended!",
                "date": "2024-01-05"
            }
        ]
    
    def get_reviews(self):
        """Return all reviews."""
        return self.reviews
    
    def get_average_rating(self):
        """Calculate and return average rating."""
        if not self.reviews:
            return 0
        return sum(review["rating"] for review in self.reviews) / len(self.reviews)


class FeedbackManager:
    """Handles feedback and suggestions from users."""
    
    def __init__(self):
        self.feedback_categories = [
            "Platform Improvement",
            "New Feature Request",
            "User Experience",
            "Bug Report",
            "General Suggestion"
        ]
    
    def get_feedback_categories(self):
        """Return feedback categories."""
        return self.feedback_categories
    
    def save_feedback(self, feedback_data):
        """Save feedback (placeholder for database integration)."""
        # In a real application, this would save to database
        return True


class ContactFormHandler:
    """Handles contact form operations and validation."""
    
    def __init__(self):
        self.subjects = ["General Inquiry", "Technical Support", "Account Issues", "Feedback", "Partnership"]
    
    def get_subjects(self):
        """Return available contact subjects."""
        return self.subjects
    
    def validate_form(self, name, email, message):
        """Validate contact form data."""
        return bool(name and email and message)
    
    def save_contact_message(self, contact_data):
        """Save contact message (placeholder for database integration)."""
        # In a real application, this would save to database
        return True


class SessionStateManager:
    """Handles session state management for forms."""
    
    @staticmethod
    def init_feedback_session_state():
        """Initialize feedback form session state."""
        if 'feedback_submitted' not in st.session_state:
            st.session_state.feedback_submitted = False
        if 'feedback_submission_time' not in st.session_state:
            st.session_state.feedback_submission_time = None
    
    @staticmethod
    def init_contact_session_state():
        """Initialize contact form session state."""
        if 'contact_submitted' not in st.session_state:
            st.session_state.contact_submitted = False
        if 'contact_submission_time' not in st.session_state:
            st.session_state.contact_submission_time = None
    
    @staticmethod
    def check_and_reset_feedback_form():
        """Check if feedback form should be reset (after 5 minutes)."""
        if (st.session_state.feedback_submitted and 
            st.session_state.feedback_submission_time and
            (datetime.now() - st.session_state.feedback_submission_time).seconds > 300):
            st.session_state.feedback_submitted = False
            st.session_state.feedback_submission_time = None
    
    @staticmethod
    def mark_feedback_submitted():
        """Mark feedback as submitted."""
        st.session_state.feedback_submitted = True
        st.session_state.feedback_submission_time = datetime.now()
    
    @staticmethod
    def mark_contact_submitted():
        """Mark contact form as submitted."""
        st.session_state.contact_submitted = True
        st.session_state.contact_submission_time = datetime.now()


class ContactPageRenderer:
    """Handles rendering of contact page UI components."""
    
    def __init__(self):
        self.contact_info = ContactInfo()
        self.reviews_manager = ReviewsManager()
        self.feedback_manager = FeedbackManager()
        self.form_handler = ContactFormHandler()
        self.session_manager = SessionStateManager()
        
        # Initialize session state
        self.session_manager.init_feedback_session_state()
        self.session_manager.init_contact_session_state()
    
    def render_header(self):
        """Render page header."""
        st.title("📞 Contact Us")
        st.markdown("""
        ### Get in Touch with JobConnect Team
        
        We're here to help you with any questions or concerns!
        """)
    
    def render_contact_info(self):
        """Render contact information section."""
        st.markdown("#### 📍 Contact Information")
        st.markdown(self.contact_info.get_contact_details())
    
    def render_contact_form(self):
        """Render contact form."""
        st.markdown("#### 💬 Send us a Message")
        
        with st.form("contact_form"):
            name = st.text_input("Your Name", 
                               disabled=st.session_state.contact_submitted,
                               key="contact_name")
            email = st.text_input("Email Address", 
                                disabled=st.session_state.contact_submitted,
                                key="contact_email")
            subject = st.selectbox("Subject", self.form_handler.get_subjects(), 
                                 disabled=st.session_state.contact_submitted,
                                 key="contact_subject")
            message = st.text_area("Message", height=100, 
                                 disabled=st.session_state.contact_submitted,
                                 key="contact_message",
                                 placeholder="Your message..." if not st.session_state.contact_submitted else "Thank you for your message!")
            
            # Dynamic button for contact form
            if st.session_state.contact_submitted:
                button_text = "✅ Message Sent"
                button_type = "secondary"
            else:
                button_text = "📤 Send Message"
                button_type = "primary"
            
            if st.form_submit_button(button_text, type=button_type, disabled=st.session_state.contact_submitted):
                if self.form_handler.validate_form(name, email, message):
                    contact_data = {
                        "name": name,
                        "email": email,
                        "subject": subject,
                        "message": message,
                        "timestamp": datetime.now()
                    }
                    if self.form_handler.save_contact_message(contact_data):
                        st.success("✅ Message sent successfully! We'll get back to you soon.")
                        self.session_manager.mark_contact_submitted()
                        st.rerun()
                    else:
                        st.error("Failed to send message. Please try again.")
                else:
                    st.error("Please fill all required fields")
        
        # Reset button for contact form (optional)
        if st.session_state.contact_submitted:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Send Another Message", use_container_width=True, key="reset_contact"):
                    st.session_state.contact_submitted = False
                    st.session_state.contact_submission_time = None
                    st.rerun()
    
    def render_reviews_section(self):
        """Render customer reviews section."""
        st.markdown("---")
        st.markdown("### ⭐ What Our Users Say")
        
        reviews = self.reviews_manager.get_reviews()
        avg_rating = self.reviews_manager.get_average_rating()
        
        # Display average rating
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #a9b7f3 0%, #a9b7f3 100%); 
                        border-radius: 15px; color: white; margin-bottom: 20px;">
                <h2 style="margin: 0; color: white;">⭐ {avg_rating:.1f}/5.0</h2>
                <p style="margin: 5px 0 0 0; color: #f0f0f0;">Average Rating from {len(reviews)} Reviews</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display reviews in grid
        for i in range(0, len(reviews), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(reviews):
                    review = reviews[i + j]
                    with col:
                        self.render_review_card(review)
    
    def render_review_card(self, review):
        """Render individual review card."""
        stars = "⭐" * review["rating"]
        badge_color = "#28a745" if review["role"] == "Job Seeker" else "#007bff"
        
        st.markdown(f"""
        <div style="border: 2px solid #e9ecef; border-radius: 15px; padding: 20px; margin: 10px 0;
                    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #2c3e50;">👤 {review["name"]}</h4>
                <span style="background: {badge_color}; color: white; padding: 4px 8px; 
                            border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
                    {review["role"]}
                </span>
            </div>
            <div style="font-size: 1.2rem; margin-bottom: 10px;">{stars}</div>
            <p style="color: #495057; font-style: italic; margin-bottom: 10px; line-height: 1.5;">
                "{review["review"]}"
            </p>
            <small style="color: #6c757d;">📅 {review["date"]}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def render_feedback_section(self):
        """Render feedback and suggestions section with disabled state after submission."""
        st.markdown("---")
        st.markdown("### 💡 Feedback & Suggestions")
        st.markdown("Help us improve JobConnect by sharing your valuable feedback!")
        
        # Check if enough time has passed to reset form (optional - 5 minutes)
        self.session_manager.check_and_reset_feedback_form()
        
        with st.form("feedback_form"):
            col1, col2 = st.columns(2)
            with col1:
                feedback_name = st.text_input("Your Name (Optional)", 
                                            disabled=st.session_state.feedback_submitted,
                                            key="feedback_name")
                feedback_category = st.selectbox("Category", 
                                               self.feedback_manager.get_feedback_categories(),
                                               disabled=st.session_state.feedback_submitted,
                                               key="feedback_category")
            with col2:
                feedback_email = st.text_input("Email (Optional)", 
                                             disabled=st.session_state.feedback_submitted,
                                             key="feedback_email")
                feedback_rating = st.slider("Rate Your Experience", 1, 5, 4, 
                                           disabled=st.session_state.feedback_submitted,
                                           key="feedback_rating")
            
            feedback_message = st.text_area("Your Feedback/Suggestion", height=120, 
                                           disabled=st.session_state.feedback_submitted,
                                           key="feedback_message",
                                           placeholder="Tell us what you think about our platform..." if not st.session_state.feedback_submitted else "Thank you for your feedback!")
            
            # Dynamic button text and state for feedback form
            if st.session_state.feedback_submitted:
                button_text = "✅ Feedback Submitted"
                button_type = "secondary"
            else:
                button_text = "🚀 Submit Feedback"
                button_type = "primary"
            
            if st.form_submit_button(button_text, type=button_type, disabled=st.session_state.feedback_submitted):
                if feedback_message:
                    feedback_data = {
                        "name": feedback_name or "Anonymous",
                        "email": feedback_email,
                        "category": feedback_category,
                        "rating": feedback_rating,
                        "message": feedback_message,
                        "timestamp": datetime.now()
                    }
                    if self.feedback_manager.save_feedback(feedback_data):
                        st.success("🎉 Thank you for your feedback! We appreciate your input.")
                        st.balloons()
                        # Mark as submitted
                        self.session_manager.mark_feedback_submitted()
                        st.rerun()
                    else:
                        st.error("Failed to submit feedback. Please try again.")
                else:
                    st.error("Please provide your feedback message")
        
        # Reset button for feedback form (optional)
        if st.session_state.feedback_submitted:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Submit Another Feedback", use_container_width=True, key="reset_feedback"):
                    st.session_state.feedback_submitted = False
                    st.session_state.feedback_submission_time = None
                    st.rerun()
    
    def render_faq_section(self):
        """Render frequently asked questions section."""
        st.markdown("---")
        st.markdown("### ❓ Frequently Asked Questions")
        
        faqs = [
            {
                "question": "How do I create an account?",
                "answer": "Click on 'I Want a Job' or 'I Want to Hire' from the home page, then select 'Sign Up' to create your account."
            },
            {
                "question": "Is JobConnect free to use?",
                "answer": "Yes! JobConnect is completely free for both job seekers and employers. We believe in connecting talent with opportunities without barriers."
            },
            {
                "question": "How long does it take to get hired?",
                "answer": "It varies by role and employer response time. Many users find jobs within 1-2 weeks of completing their profile."
            },
            {
                "question": "Can I edit my profile after creating it?",
                "answer": "Absolutely! You can update your profile anytime by going to your dashboard and clicking on 'Complete/Edit Profile'."
            },
            {
                "question": "How do I know if an employer viewed my application?",
                "answer": "You'll receive notifications on your dashboard when employers view or respond to your applications."
            }
        ]
        
        for i, faq in enumerate(faqs):
            with st.expander(f"🔍 {faq['question']}"):
                st.markdown(faq['answer'])


class ContactPage:
    """Main contact page controller that orchestrates all contact components."""
    
    def __init__(self):
        self.renderer = ContactPageRenderer()
    
    def display(self):
        """Main method to display the complete contact page."""
        # Render header
        self.renderer.render_header()
        
        # Main contact section
        col1, col2 = st.columns(2)
        
        with col1:
            self.renderer.render_contact_info()
        
        with col2:
            self.renderer.render_contact_form()
        
        # Additional sections
        self.renderer.render_reviews_section()
        self.renderer.render_feedback_section()
        self.renderer.render_faq_section()


# Preserve the original function signature - NO CHANGES to existing code needed
def contact_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = ContactPage()
    page.display()
