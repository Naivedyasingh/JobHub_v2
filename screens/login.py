import streamlit as st
from utils.auth import authenticate


class LoginPageStyles:
    """Handles CSS styling for the login page."""
    
    @staticmethod
    def get_custom_css():
        """Return custom CSS styles for the login page."""
        return """<style>
          .main>div{padding-left:0;padding-right:0;}
          h2{color:#1f77b4!important;}
          .stTextInput{width:860px!important;margin:0 auto!important;}
          .stTextInput>div{width:860px!important;max-width:860px!important;margin:0 auto!important;}
          .stTextInput>div>div>input{width:860px!important;max-width:860px!important;height:40px!important;font-size:1.2rem!important;padding:0.65rem 0.75rem!important;margin:0 auto!important;}
          .stTextInput>label{font-size:2rem!important;font-weight:800!important;margin-bottom:0.5rem!important;width:900px!important;margin-left:auto!important;margin-right:auto!important;color:#2c3e50!important;}
          .stButton>button[kind="primary"]{height:46px!important;width:500px!important;max-width:400px!important;font-size:0.9rem!important;padding:0.4rem 1.2rem!important;margin:0 auto!important;display:block!important;}
          .error-message{background:#f8d7da;color:#721c24;padding:0.6rem 0.9rem;border-radius:3px;border-left:3px solid #dc3545;margin:0.8rem auto;font-size:0.9rem;font-weight:600;max-width:600px;text-align:center;}
        </style>"""


class LoginFormRenderer:
    """Handles rendering of login form elements."""
    
    def __init__(self):
        self.styles = LoginPageStyles()
    
    def render_header(self, role):
        """Render the login page header with role-specific content."""
        role_name = "Job Seeker" if role == "job" else "Employer"
        role_icon = "🔍" if role == "job" else "🏢"
        
        st.markdown(f"""<div style='text-align:center;margin-bottom:1.5rem;'><h2>{role_icon} {role_name} Login</h2><p style='color:#222;margin-top:0.5rem;'>Sign in to access your dashboard</p></div>""", unsafe_allow_html=True)
    
    def render_form_fields(self):
        """Render the login form input fields."""
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.markdown('<label style="font-size:1.1rem;font-weight:800;color:#2c3e50;margin-bottom:0.5rem;display:block;width:850px;margin:0 auto;">Name or Phone</label>', unsafe_allow_html=True)
        identifier = st.text_input("", key="login_identifier", placeholder="Enter name / phone", label_visibility="collapsed")
        st.markdown('<label style="font-size:1.1rem;font-weight:800;color:#2c3e50;margin-bottom:0.5rem;display:block;width:850px;margin:0 auto;">Password</label>', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", key="login_password", placeholder="Enter password", label_visibility="collapsed")
        return identifier, pwd
    
    def render_error_message(self, message):
        """Render an error message with consistent styling."""
        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    
    def render_action_buttons(self):
        """Render the secondary action buttons (forgot password, create account, home)."""
        st.markdown("".join(["─"] * 97))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔑 Forgot Password", use_container_width=True):
                st.info("Please contact support to reset your password.")
        with col2:
            if st.button("📝 Create Account", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()
        with col3:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()


class LoginAuthenticator:
    """Handles login authentication logic."""
    
    @staticmethod
    def authenticate_user(identifier, password, role):
        """Authenticate user with given credentials."""
        return authenticate(identifier.strip(), password.strip(), role)
    
    @staticmethod
    def handle_successful_login(user):
        """Handle successful login by updating session state."""
        st.success(f"Welcome back, {user['name']}!")
        st.session_state.current_user = user
        st.session_state.page = f"{user['role']}_dashboard"
        st.rerun()


class LoginPage:
    """Main login page controller that orchestrates all login components."""
    
    def __init__(self):
        self.form_renderer = LoginFormRenderer()
        self.authenticator = LoginAuthenticator()
    
    def _validate_inputs(self, identifier, password):
        """Validate login form inputs."""
        return bool(identifier and password)
    
    def _process_login_attempt(self, identifier, password, role):
        """Process the login attempt and handle the result."""
        if not self._validate_inputs(identifier, password):
            self.form_renderer.render_error_message("⚠️ Please fill in all fields.")
            return
        
        user = self.authenticator.authenticate_user(identifier, password, role)
        if user:
            self.authenticator.handle_successful_login(user)
        else:
            self.form_renderer.render_error_message("❌ Invalid credentials. Please try again.")
    
    def display(self):
        """Main method to display the complete login page."""
        st.markdown(self.form_renderer.styles.get_custom_css(), unsafe_allow_html=True)
        self.form_renderer.render_header(st.session_state.role)   
        identifier, pwd = self.form_renderer.render_form_fields()
        
        st.markdown("\n")
        _, col, _ = st.columns([1.3, 2, 1])
        with col:
            if st.button("🚀 Login", key="login_submit", type="primary"):
                self._process_login_attempt(identifier, pwd, st.session_state.role)

        
        st.markdown('</div>', unsafe_allow_html=True)
        self.form_renderer.render_action_buttons()

def login_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = LoginPage()
    page.display()
