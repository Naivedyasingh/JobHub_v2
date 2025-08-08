# main.py
import streamlit as st
import os
import base64
from components.sidebar import render_sidebar
from screens.home import home_page 
from screens.auth_choice import auth_choice_page
from screens.login import login_page
from screens.signup import signup_page
from screens.job_dashboard import job_dashboard
from screens.hire_dashboard import hire_dashboard
from screens.browse_seekers import browse_job_seekers_page
from screens.offer_job import offer_job_page
from screens.post_job import post_job_page
from screens.my_applications import my_applications_page
from screens.view_applications import view_applications_page
from screens.profile import profile_page
from screens.contact import contact_page
from db.models import DatabaseManager, init_models
from screens.my_job_postings import my_job_postings_page




class StyleManager:
    """Handles application styling and CSS management."""
    
    @staticmethod
    def apply_transparent_header():
        """Apply transparent header styling."""
        transparent_header_style = """
        <style>
        .st-emotion-cache-1ffuo7c {
            background: transparent !important;
        }

        /* Backup selectors in case the emotion class changes */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0) !important;
        }
        </style>
        """
        st.markdown(transparent_header_style, unsafe_allow_html=True)
    
    @staticmethod
    def apply_background_video(video_b64):
        """Apply background video with CSS styling."""
        st.markdown(
            f"""
            <style>
                #bgvid {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    object-fit: cover;
                    z-index: -1;
                    filter: blur(13px) brightness(0.92);
                    pointer-events: none;
                }}

                /* keep Streamlit widgets transparent over the video */
                .stApp, .block-container {{
                    background: transparent !important;
                }}

                /* Optional: sidebar background */
                .css-1d391kg {{       /* auto-generated class name may differ on new Streamlit versions */
                    background-color: #f8f9fa;
                }}
            </style>

            <video id="bgvid" autoplay muted loop>
                <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
            """,
            unsafe_allow_html=True,
        )


class DatabaseService:
    """Handles database initialization and management."""
    
    def __init__(self):
        self.config = {
            'host': "localhost",
            'user': "root",
            'password': "root",
            'db': "jobhub_db",
            'port': 3306
        }
    
    def setup_database(self):
        """Initialize and setup database connection."""
        try:
            db = DatabaseManager(**self.config)
            schema_file = os.path.join(os.path.dirname(__file__), "db", "schema.sql")
            db.init_schema(schema_file)
            init_models(db)
            return db
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            st.stop()


class SessionStateManager:
    """Manages Streamlit session state initialization and defaults."""
    
    @staticmethod
    def ensure_session_defaults():
        """Initialize session state with default values."""
        defaults = {
            "page": "home",
            "role": None,
            "current_user": None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


class BackgroundManager:
    """Handles background video loading and processing."""
    
    def __init__(self):
        self.video_path = os.path.join(".streamlit", "public", "background_video.mp4")
    
    def validate_video_exists(self):
        """Check if background video file exists."""
        if not os.path.exists(self.video_path):
            st.error(f"Video file not found: {self.video_path}")
            st.stop()
            return False
        return True
    
    def load_video_as_base64(self):
        """Load video file and convert to base64."""
        try:
            with open(self.video_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            st.error(f"Error loading video file: {e}")
            st.stop()


class PageRouter:
    """Handles page routing and navigation."""
    
    def __init__(self):
        self.routes = {
            "home": home_page,
            "auth_choice": auth_choice_page,
            "login": login_page,
            "signup": signup_page,
            "job_dashboard": job_dashboard,
            "hire_dashboard": hire_dashboard,
            "browse_job_seekers": browse_job_seekers_page,
            "offer_job": offer_job_page,
            "post_job": post_job_page,
            "my_applications": my_applications_page,
            "view_applications": view_applications_page,
            "my_job_postings": my_job_postings_page, 
            "profile": profile_page,
            "contact": contact_page
        }
    
    def route_to_page(self, page_name):
        """Route to the specified page."""
        if page_name in self.routes:
            self.routes[page_name]()
        else:
            # Fallback to home page for invalid routes
            st.session_state.page = "home"
            self.routes["home"]()


class ConfigurationManager:
    """Handles Streamlit page configuration."""
    
    @staticmethod
    def configure_page():
        """Set up Streamlit page configuration."""
        st.set_page_config(
            page_title="JobHub Portal",
            page_icon="💼",
            layout="wide",
            initial_sidebar_state="expanded"
        )


class SidebarManager:
    """Manages sidebar rendering logic."""
    
    @staticmethod
    def render_if_authenticated():
        """Render sidebar only if user is authenticated."""
        if st.session_state.get("current_user"):
            render_sidebar()


class JobHubApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.session_manager = SessionStateManager()
        self.background_manager = BackgroundManager()
        self.style_manager = StyleManager()
        self.page_router = PageRouter()
        self.config_manager = ConfigurationManager()
        self.sidebar_manager = SidebarManager()
        
        # Initialize application
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize the application with all required components."""
        self.db = self.db_service.setup_database()
        self.session_manager.ensure_session_defaults()
    
    def _setup_styling(self):
        """Setup all application styling."""
        self.style_manager.apply_transparent_header()
        self._load_background_video()
    
    def _load_background_video(self):
        """Load and apply background video."""
        if self.background_manager.validate_video_exists():
            video_b64 = self.background_manager.load_video_as_base64()
            if video_b64:
                self.style_manager.apply_background_video(video_b64)
    
    def _configure_page(self):
        """Configure Streamlit page settings."""
        self.config_manager.configure_page()
    
    def _render_sidebar(self):
        """Render sidebar if user is authenticated."""
        self.sidebar_manager.render_if_authenticated()
    
    def _route_pages(self):
        """Handle page routing based on session state."""
        current_page = st.session_state.get("page", "home")
        self.page_router.route_to_page(current_page)
    
    def run(self):
        """Main application entry point."""
        self._setup_styling()
        self._configure_page()
        self._render_sidebar()
        self._route_pages()


class ApplicationFactory:
    """Factory class for creating and configuring the application."""
    
    @staticmethod
    def create_app():
        """Create and return a configured JobHub application instance."""
        return JobHubApp()


# Application entry point
if __name__ == "__main__":
    app = ApplicationFactory.create_app()
    app.run()
