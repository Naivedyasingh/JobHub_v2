# pages/signup.py

import streamlit as st
from utils.validation import validate_email, validate_phone, validate_password
from utils.auth import next_user_id
from db.models import User
from datetime import datetime


class SignupPageStyles:
    """Handles CSS styling for the signup page."""
    
    @staticmethod
    def get_custom_css():
        """Return custom CSS styles for the signup page."""
        return """<style>.terms-checkbox{margin-top:-10px;margin-bottom:20px;}.back-button{margin-top:20px;}</style>"""


class SignupFormRenderer:
    """Handles rendering of signup form elements."""
    
    def __init__(self):
        self.styles = SignupPageStyles()
    
    def render_header(self, role):
        """Render the signup page header with role-specific content."""
        role_name = "Job Seeker" if role == "job" else "Employer"
        st.markdown(f"<h1 style='text-align:center;color:#1f77b4;'>✨ {role_name} Sign Up</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align:center;color:#222;margin-top:-10px;font-weight:400;'>Create your account and start your journey today.</h4><br><br><br><br>", unsafe_allow_html=True)
    
    def render_form_fields(self, role):
        """Render the signup form input fields and return the form data."""
        with st.container():
            col1, col2 = st.columns(2, gap="large")
            with col1:
                name = st.text_input("📛 Full Name", key="signup_name")
                phone = st.text_input("📱 Phone Number", key="signup_phone")
                email = st.text_input("📧 Email", key="signup_email")
            with col2:
                gender = st.selectbox("👤 Gender", ["Select", "Male", "Female", "Other"], key="signup_gender")
                pwd = st.text_input("🔒 Password", type="password", key="signup_password")
                cpwd = st.text_input("🔒 Confirm Password", type="password", key="signup_confirm_password")

            company_name = ""
            if role == "hire":
                company_name = st.text_input("🏢 Company Name", key="signup_company_name")

            agree = st.checkbox("I agree to the Terms and Conditions", key="signup_agree")
            
            return {
                'name': name,
                'phone': phone,
                'email': email,
                'gender': gender,
                'password': pwd,
                'confirm_password': cpwd,
                'company_name': company_name,
                'agree': agree
            }
    
    def render_action_buttons(self):
        """Render the secondary action buttons (back, login, home)."""
        st.markdown("\n")
        st.markdown("".join(["─"] * 97))
        st.markdown("\n")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.page = "auth_choice"
                st.rerun()
        with col2:
            if st.button("📝 Already have Account", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        with col3:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()


class SignupValidator:
    """Handles validation of signup form data."""
    
    @staticmethod
    def validate_form_data(form_data, role):
        """Validate all form data and return validation result and error message."""
        required = [form_data['name'].strip(), form_data['phone'].strip(), 
                   form_data['email'].strip(), form_data['password'].strip(), 
                   form_data['confirm_password'].strip()]
        
        if role == "hire":
            required.append(form_data['company_name'].strip())
        
        if not all(required) or form_data['gender'] == "Select":
            return False, "Please fill all required fields and select gender."
        elif not form_data['agree']:
            return False, "You must accept the Terms and Conditions."
        elif form_data['password'] != form_data['confirm_password']:
            return False, "Passwords do not match."
        elif not validate_phone(form_data['phone']):
            return False, "Phone number must be exactly 10 digits."
        elif not validate_email(form_data['email']):
            return False, "Invalid email address."
        elif not validate_password(form_data['password']):
            return False, "Password does not meet complexity requirements."
        
        return True, None


class SignupUserManager:
    """Handles user creation and database operations."""
    
    def __init__(self):
        self.user_model = User()
    
    def check_existing_user(self, phone, email):
        """Check if user already exists with given phone or email."""
        with User.db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE phone = %s OR email = %s", (phone, email.lower()))
            return cur.fetchone()
    
    def get_next_user_id(self):
        """Get the next available user ID."""
        with User.db.cursor() as cur:
            cur.execute("SELECT MAX(id) as max_id FROM users")
            result = cur.fetchone()
            return (result['max_id'] or 0) + 1
    
    def create_user_data(self, form_data, role, user_id):
        """Create user data dictionary for database insertion."""
        user_data = {
            "id": user_id,
            "role": role,
            "name": form_data['name'].strip(),
            "phone": form_data['phone'].strip(),
            "email": form_data['email'].strip(),
            "gender": form_data['gender'],
            "password": form_data['password'].strip(),
            "availability_status": "available",
            "created_at": datetime.now()
        }
        
        if role == "hire" and form_data['company_name'].strip():
            user_data["company_name"] = form_data['company_name'].strip()
        
        return user_data
    
    def create_new_user(self, user_data):
        """Create new user in database and return created user."""
        new_user_id = self.user_model.create(user_data)
        if new_user_id:
            return self.user_model.get(new_user_id)
        return None


class SignupPage:
    """Main signup page controller that orchestrates all signup components."""
    
    def __init__(self):
        self.form_renderer = SignupFormRenderer()
        self.validator = SignupValidator()
        self.user_manager = SignupUserManager()
    
    def _handle_signup_attempt(self, form_data, role):
        """Process the signup attempt and handle the result."""
        # Validate form data
        is_valid, error_message = self.validator.validate_form_data(form_data, role)
        if not is_valid:
            st.error(error_message)
            return
        
        # Check for existing users
        existing_user = self.user_manager.check_existing_user(form_data['phone'], form_data['email'])
        if existing_user:
            st.error("Phone number or email already registered.")
            return
        
        # Create new user
        next_id = self.user_manager.get_next_user_id()
        user_data = self.user_manager.create_user_data(form_data, role, next_id)
        created_user = self.user_manager.create_new_user(user_data)
        
        if created_user:
            st.success("Account created successfully!")
            st.session_state.current_user = created_user
            st.session_state.page = f"{created_user['role']}_dashboard"
            st.rerun()
        else:
            st.error("Failed to create account. Please try again.")
    
    def display(self):
        """Main method to display the complete signup page."""
        # Apply custom styles
        st.markdown(self.form_renderer.styles.get_custom_css(), unsafe_allow_html=True)
        
        # Render header
        self.form_renderer.render_header(st.session_state.role)
        
        # Render form fields
        form_data = self.form_renderer.render_form_fields(st.session_state.role)
        
        # Handle signup button
        if st.button("🚀 Create Account", use_container_width=True, type="primary", key="signup_submit"):
            self._handle_signup_attempt(form_data, st.session_state.role)
        
        # Render action buttons
        self.form_renderer.render_action_buttons()


# Preserve the original function signature - NO CHANGES to existing code needed
def signup_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = SignupPage()
    page.display()
