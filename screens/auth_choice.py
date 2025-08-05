# auth_choice.py

import streamlit as st
from streamlit_lottie import st_lottie
import json


class LottieLoader:
    """Handles loading of Lottie animation files."""
    
    @staticmethod
    def load_lottie(filepath: str):
        """Load a local Lottie file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


class AuthChoicePage:
    """Handles the authentication choice page display and interactions."""
    
    def __init__(self):
        self.lottie_loader = LottieLoader()
    
    def display(self):
        """Main method to display the auth choice page - preserves exact original logic."""
        role_name = "Job Seeker" if st.session_state.role == "job" else "Employer"
        
        st.markdown("""
        <style>
          #MainMenu {visibility: hidden;}
          header {visibility: hidden;}
          footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1f77b4; font-size: 2.5rem;">{role_name} – Authentication</h1>
            <p style="color: #333; font-size: 1.2rem; margin-top: 0.25rem;">
                What would you like to do?
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Load and display Lottie animation above the buttons
        lottie = self.lottie_loader.load_lottie("D:\\JobHub\\.streamlit\\public\\Login.json")  
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st_lottie(
                lottie,
                speed=1,
                loop=True,
                quality="high",
                height=400,
                key="auth_lottie"
            )
        st.markdown("\n")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            if st.button("🔑 Login", type="primary", use_container_width=True, key="auth_login"):
                st.session_state.page = "login"
                st.rerun()
        with col2:
            if st.button("✨ Sign Up", type="primary", use_container_width=True, key="auth_signup"):
                st.session_state.page = "signup"
                st.rerun()

        st.markdown("<br>\n", unsafe_allow_html=True)

        # Increase column width and use container width
        _, back_col, _ = st.columns([4, 8, 4])  # Wider middle column
        with back_col:
            if st.button("← Back", use_container_width=True, type="secondary"):
                st.session_state.page = "home"
                st.session_state.role = None
                st.rerun()


# Preserve the original function signature - NO CHANGES to existing code needed
def load_lottie(filepath: str):
    """Wrapper function to maintain backward compatibility."""
    return LottieLoader.load_lottie(filepath)


def auth_choice_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = AuthChoicePage()
    page.display()
