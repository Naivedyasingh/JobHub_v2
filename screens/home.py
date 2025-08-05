# pages/home.py

import streamlit as st
from db.models import User


class StatCard:
    """Handles creation of statistics cards with optional deltas."""
    
    def __init__(self):
        self.colors = {
            "green": "#28a745", 
            "red": "#dc3545", 
            "blue": "#007bff", 
            "orange": "#fd7e14", 
            "gray": "#e8f4fd"
        }
    
    def create(self, value, label, delta=None, delta_color="green"):
        """Create a statistics card with optional delta"""
        delta_html = f"<div style='color: {self.colors.get(delta_color, '#28a745')}; font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem;'>{delta}</div>" if delta else ""
        return f"""<div style='text-align: center; padding: 1.5rem; background-color: #e8f4fd; border-radius: 10px; margin: 1rem 0; border-left: 5px solid #6495ed;'>
            <div style='font-size: 1.8rem; font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem;'>{value}</div>
            <div style='color: #666; font-size: 0.9rem;'>{label}</div>{delta_html}</div>"""


class InfoCard:
    """Handles creation of information cards."""
    
    @staticmethod
    def create(title, content, bg_color, border_color, title_color, icon):
        """Create an information card"""
        return f"""<div style='padding: 2rem; background-color: {bg_color}; border-radius: 15px; margin: 1rem 0; border-left: 5px solid {border_color};'>
            <h4 style='text-align: center; margin-bottom: 1.5rem; color: {title_color};'>{icon} <strong>{title}</strong></h4>
            <div style='color: #2c3e50; line-height: 1.8;'>{content}</div></div>"""


class PlatformStats:
    """Handles fetching and processing of platform statistics."""
    
    def __init__(self):
        self.user_model = User
    
    def get_stats(self):
        """Fetch platform statistics from database"""
        with self.user_model.db.cursor() as cur:
            cur.execute("SELECT role, city, job_types FROM users WHERE role IN ('job', 'hire')")
            users = cur.fetchall()
        
        job_seekers = [u for u in users if u.get('role') == 'job']
        employers = [u for u in users if u.get('role') == 'hire']
        
        cities = set(u.get('city', '').lower() for u in users if u.get('city'))
        cities_count = len(cities) if cities else 5
        
        skills = set()
        for u in job_seekers:
            job_types = u.get('job_types', [])
            if isinstance(job_types, list):
                skills.update(job_types)
            elif isinstance(job_types, str):
                skills.add(job_types)
        skills_count = len(skills) if skills else 15
        
        return len(job_seekers), len(employers), cities_count, skills_count


class HomePage:
    """Handles the home page display and interactions."""
    
    def __init__(self):
        self.stat_card = StatCard()
        self.info_card = InfoCard()
        self.platform_stats = PlatformStats()
    
    def _apply_custom_css(self):
        """Apply custom CSS styles."""
        st.markdown("""
        <style>
          #MainMenu {visibility: hidden;}
          header {visibility: hidden;}
          footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    def _render_hero_section(self):
        """Render the hero section with logo and tagline."""
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.image(r".streamlit/public/title_logo.png", width=500)
            st.markdown("""
            <div style='text-align: center; padding: 0; margin: 0;'>
              <h3 style='color: #000000; font-weight: 500; margin: 0;padding:0;'>Connecting Dreams with Opportunities</h3><br><br><br><br><br><br>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_cta_section(self):
        """Render the call-to-action section."""
        st.markdown("<h3 style='text-align: center; color: #2c3e50; margin-bottom: 1.5rem;'>🚀 <strong>Get Started Today!</strong></h3>", unsafe_allow_html=True)
        
        st.markdown("""
            <style>
            div.stButton > button {
                height: 55px;
                font-size: 60rem;
                padding: 10px 24px;
                border: 1.5px solid #000;
                border-radius: 10px;
                background-color: #fff;
                color: #000;
                font-weight: 900;
            }
            div.stButton > button:hover {
                background-color: #dcdcdc ;
                border-color: #999;
            }
            .info-div {
                text-align: center;
                padding: 1rem;
                background-color: #e8f4fd;
                border-left: 5px solid #6495ed;
                border-radius: 10px;
                margin-top: 0.5rem;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)
    
    def _render_action_buttons(self):
        """Render the main action buttons."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 I WANT A JOB ", key="job_button", use_container_width=True, type="secondary"):
                st.session_state.role = "job"
                st.session_state.page = "auth_choice"
                st.rerun()
            st.markdown("""
                <div class="info-div">
                    <strong>Perfect for:</strong><br>🔧 Skilled workers<br>🏠 Household helpers<br>🚀 Service providers
                </div>""", unsafe_allow_html=True)
        
        with col2:
            if st.button("🏢 I WANT TO HIRE ", key="hire_button", use_container_width=True, type="secondary"):
                st.session_state.role = "hire"
                st.session_state.page = "auth_choice"
                st.rerun()
            st.markdown("""
                <div class="info-div">
                    <strong>Perfect for:</strong><br>🏢 Companies<br>🚀 Startups<br>🏭 Organizations
                </div>""", unsafe_allow_html=True)
    
    def _render_platform_stats(self):
        """Render platform statistics section."""
        st.markdown("\n")
        st.markdown("".join(["─"] * 97))
        
        # Get platform statistics from database
        job_seekers_count, employers_count, cities_count, skills_count = self.platform_stats.get_stats()
        
        # Platform Impact Statistics
        st.markdown("### 📊 **Platform Impact**")
        col1, col2, col3, col4 = st.columns(4)
        stats = [
            (job_seekers_count, "Job Seekers", "Active", "green"), 
            (employers_count, "Employers", "Hiring", "blue"), 
            (job_seekers_count * 2, "Connections", "+12%", "green"), 
            ("85%" if (job_seekers_count + employers_count) > 5 else "Growing", "Success Rate", "High", "orange")
        ]
        
        for col, (value, label, delta, delta_color) in zip([col1, col2, col3, col4], stats):
            with col:
                st.markdown(self.stat_card.create(value, label, delta, delta_color), unsafe_allow_html=True)
    
    def _render_impact_section(self):
        """Render the impact comparison section."""
        st.markdown("".join(["─"] * 97))
        st.markdown("### 🔄 **Our Impact on Employment**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(self.info_card.create("Before JobConnect", "• Job seekers struggled to find reliable work<br>• Employers had difficulty finding trusted help<br>• Time-consuming manual searching process<br>• High agency fees and commissions<br>• Limited job visibility and opportunities<br>• No proper verification system", "#f9ecec", "#e74c3c", "#c0392b", "😔"), unsafe_allow_html=True)
        with col2:
            st.markdown(self.info_card.create("After JobConnect", "• Easy access to verified job opportunities<br>• Secure platform with identity verification<br>• Digital profiles showcase skills & experience<br>• Fair salary expectations and transparency<br>• Quick job matching and applications<br>• Direct communication between parties", "#e9f4ec", "#27ae60", "#27ae60", "🌟"), unsafe_allow_html=True)
    
    def _render_growth_section(self):
        """Render the platform growth section."""
        st.markdown("".join(["─"] * 97))
        st.markdown("\n### 🎉 **Platform Growth**")
        
        job_seekers_count, employers_count, cities_count, skills_count = self.platform_stats.get_stats()
        experience_level = "Expert" if job_seekers_count > 0 else "All"
        
        st.markdown(f"""<div style='text-align: center; padding: 2rem; background-color: #f0f0ff; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #1f77b4;'>
            <h4 style='color: #1f77b4; margin-bottom: 1.5rem;'>📊 Our Growing Community</h4>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap;'>
                <div style='margin: 0.5rem;'><div style='font-size: 1.5rem; font-weight: bold; color: #2c3e50;'>{cities_count}+</div><div style='color: #666; font-size: 0.9rem;'>Cities Covered</div></div>
                <div style='margin: 0.5rem;'><div style='font-size: 1.5rem; font-weight: bold; color: #2c3e50;'>{skills_count}+</div><div style='color: #666; font-size: 0.9rem;'>Skills Available</div></div>
                <div style='margin: 0.5rem;'><div style='font-size: 1.5rem; font-weight: bold; color: #2c3e50;'>{experience_level}</div><div style='color: #666; font-size: 0.9rem;'>Experience Levels</div></div>
            </div><p style='margin-top: 1rem; color: #666; font-style: italic;'>"Connecting talent with opportunities across the region"</p></div>""", unsafe_allow_html=True)
    
    def _render_footer(self):
        """Render the footer section."""
        st.markdown("".join(["─"] * 97))
        st.markdown("""
        <div style='text-align: center; color: #333; font-size: 0.9rem;'>
            💡 <strong>Why Choose JobConnect?</strong><br>
            ✅ Verified profiles • 🔒 Secure platform • 💰 Fair pricing • ⭐ Quality assurance<br>
            🤝 Personalized support • 🧑‍💻 Easy job posting & application • ⚡ Fast response times<br><br>
            <span style='font-size: 1.1rem; color: #2c3e50; font-weight: 600;'>
                📱 Contact us: <a href="mailto:support@JobHub.com" style="color: #2c3e50;">support@JubHub.com</a> | 📞 +91-91114-39303
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    def display(self):
        """Main method to display the complete home page."""
        self._apply_custom_css()
        self._render_hero_section()
        self._render_cta_section()
        self._render_action_buttons()
        self._render_platform_stats()
        self._render_impact_section()
        self._render_growth_section()
        self._render_footer()


# Preserve original function signatures - NO CHANGES to existing code needed
def stat_card(value, label, delta=None, delta_color="green"):
    """Wrapper function to maintain backward compatibility."""
    card = StatCard()
    return card.create(value, label, delta, delta_color)


def info_card(title, content, bg_color, border_color, title_color, icon):
    """Wrapper function to maintain backward compatibility."""
    return InfoCard.create(title, content, bg_color, border_color, title_color, icon)


def get_platform_stats():
    """Wrapper function to maintain backward compatibility."""
    stats = PlatformStats()
    return stats.get_stats()


def home_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = HomePage()
    page.display()
