# pages/profile.py

import streamlit as st
from utils.auth import calculate_profile_completion, update_user_profile
from utils.validation import validate_email, validate_phone, validate_aadhaar


class ProfileDataProcessor:
    """Handles processing and sanitization of profile data."""
    
    @staticmethod
    def safe_list_value(raw_value, options_list):
        """Safely process list values with fallback to valid options."""
        if isinstance(raw_value, str):
            raw_value = [x.strip() for x in raw_value.split(",") if x.strip()]
        return [item.strip().title() for item in raw_value if item.strip().title() in options_list]
    
    @staticmethod
    def safe_single_value(value, options_list, default):
        """Safely process single values with fallback to default."""
        if value not in options_list:
            return default
        return value
    
    @staticmethod
    def safe_salary_value(salary, min_val=5000, max_val=100000, default=15000):
        """Safely process salary value with range validation."""
        if not isinstance(salary, (int, float)) or salary < min_val:
            return default
        elif salary > max_val:
            return max_val
        return int(salary)


class JobSeekerFormRenderer:
    """Handles rendering of job seeker profile form components."""
    
    def __init__(self):
        self.data_processor = ProfileDataProcessor()
        self.job_type_options = ["Maid", "Cook", "Driver", "Cleaner", "Babysitter", "Gardener", "Security Guard", "Electrician", "Plumber"]
        self.availability_options = ["Full Time", "Part Time", "Weekends", "Night Shifts"]
        self.language_options = ["Hindi", "English", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati"]
        self.experience_options = ["Fresher", "1-2 years", "2-5 years", "5+ years"]
        self.education_options = ["Primary", "Secondary", "Higher Secondary", "Graduate", "Post Graduate"]
        self.gender_options = ["Male", "Female", "Other"]
        self.state_options = ["Maharashtra", "Madhya Pradesh", "Karnataka", "Gujarat", "West Bengal"]
    
    def render_personal_info_tab(self, user):
        """Render personal information tab."""
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=user.get('name', ''), key="profile_name")
            phone = st.text_input("Phone Number", value=user.get('phone', ''), key="profile_phone")
            email = st.text_input("Email", value=user.get('email', ''), key="profile_email")
        
        with col2:
            user_gender = self.data_processor.safe_single_value(
                user.get('gender', 'Male'), self.gender_options, 'Male'
            )
            gender = st.selectbox("Gender", self.gender_options, 
                                index=self.gender_options.index(user_gender), key="profile_gender")
            
            aadhaar = st.text_input("Aadhaar Number", value=user.get('aadhaar', ''), 
                                  placeholder="12-digit number", key="profile_aadhaar")
            date_of_birth = st.date_input("Date of Birth", key="profile_dob")
        
        return {
            'name': name, 'phone': phone, 'email': email, 'gender': gender, 'aadhaar': aadhaar
        }
    
    def render_professional_info_tab(self, user):
        """Render professional information tab."""
        st.subheader("Professional Information")
        
        col1, col2 = st.columns(2)
        with col1:
            user_exp = self.data_processor.safe_single_value(
                user.get('experience', 'Fresher'), self.experience_options, 'Fresher'
            )
            experience = st.selectbox("Experience Level", self.experience_options,
                                    index=self.experience_options.index(user_exp), key="profile_experience")
            
            default_job_types = self.data_processor.safe_list_value(
                user.get("job_types", []), self.job_type_options
            )
            job_types = st.multiselect("Job Types/Skills", 
                                     self.job_type_options,
                                     default=default_job_types, key="profile_job_types")
        
        with col2:
            user_salary = self.data_processor.safe_salary_value(user.get('expected_salary', 15000))
            expected_salary = st.number_input("Expected Monthly Salary (₹)", 
                                            min_value=5000, max_value=100000, 
                                            value=user_salary, step=1000, key="profile_salary")
            
            default_availability = self.data_processor.safe_list_value(
                user.get("availability", []), self.availability_options
            )
            availability = st.multiselect("Availability", 
                                        self.availability_options,
                                        default=default_availability, key="profile_availability")
        
        user_edu = self.data_processor.safe_single_value(
            user.get('education', 'Secondary'), self.education_options, 'Secondary'
        )
        education = st.selectbox("Education Level", self.education_options,
                               index=self.education_options.index(user_edu), key="profile_education")
        
        default_languages = self.data_processor.safe_list_value(
            user.get("languages", []), self.language_options
        )
        languages = st.multiselect("Languages Known", 
                                 self.language_options,
                                 default=default_languages, key="profile_languages")
        
        return {
            'experience': experience, 'job_types': job_types, 'expected_salary': expected_salary,
            'availability': availability, 'education': education, 'languages': languages
        }
    
    def render_location_contact_tab(self, user):
        """Render location and contact tab."""
        st.subheader("Location & Contact")
        
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_area("Full Address", value=user.get('address', ''), key="profile_address")
            city = st.text_input("City", value=user.get('city', ''), key="profile_city")
            
            user_state = self.data_processor.safe_single_value(
                user.get('state', 'Maharashtra'), self.state_options, 'Maharashtra'
            )
            state = st.selectbox("State", self.state_options,
                               index=self.state_options.index(user_state), key="profile_state")
        
        with col2:
            pincode = st.text_input("PIN Code", value=user.get('pincode', ''), key="profile_pincode")
            emergency_contact = st.text_input("Emergency Contact", value=user.get('emergency_contact', ''), key="profile_emergency_contact")
            emergency_name = st.text_input("Emergency Contact Name", value=user.get('emergency_name', ''), key="profile_emergency_name")
        
        return {
            'address': address, 'city': city, 'state': state, 'pincode': pincode,
            'emergency_contact': emergency_contact, 'emergency_name': emergency_name
        }


class EmployerFormRenderer:
    """Handles rendering of employer profile form components."""
    
    def __init__(self):
        self.data_processor = ProfileDataProcessor()
        self.gender_options = ["Male", "Female", "Other"]
        self.company_type_options = ["Family", "Small Business", "Medium Enterprise", "Large Corporation"]
        self.industry_options = ["Domestic Services", "Healthcare", "Technology", "Manufacturing", "Retail", "Other"]
        self.size_options = ["1-10", "11-50", "51-200", "200+"]
        self.state_options = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal"]
    
    def render_personal_info_tab(self, user):
        """Render personal information tab for employer."""
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=user.get('name', ''), key="employer_name")
            phone = st.text_input("Phone Number", value=user.get('phone', ''), key="employer_phone")
            email = st.text_input("Email", value=user.get('email', ''), key="employer_email")
        
        with col2:
            user_gender = self.data_processor.safe_single_value(
                user.get('gender', 'Male'), self.gender_options, 'Male'
            )
            gender = st.selectbox("Gender", self.gender_options,
                                index=self.gender_options.index(user_gender), key="employer_gender")
            
            designation = st.text_input("Designation", value=user.get('designation', ''), key="employer_designation")
        
        return {
            'name': name, 'phone': phone, 'email': email, 'gender': gender, 'designation': designation
        }
    
    def render_company_info_tab(self, user):
        """Render company information tab."""
        st.subheader("Company Information")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value=user.get('company_name', ''), key="employer_company_name")
            
            user_company_type = self.data_processor.safe_single_value(
                user.get('company_type', 'Family'), self.company_type_options, 'Family'
            )
            company_type = st.selectbox("Company Type", self.company_type_options,
                                      index=self.company_type_options.index(user_company_type), key="employer_company_type")
        
        with col2:
            user_industry = self.data_processor.safe_single_value(
                user.get('industry', 'Domestic Services'), self.industry_options, 'Domestic Services'
            )
            industry = st.selectbox("Industry", self.industry_options,
                                  index=self.industry_options.index(user_industry), key="employer_industry")
            
            user_size = self.data_processor.safe_single_value(
                user.get('company_size', '1-10'), self.size_options, '1-10'
            )
            company_size = st.selectbox("Company Size", self.size_options,
                                      index=self.size_options.index(user_size), key="employer_company_size")
        
        business_description = st.text_area("Business Description", value=user.get('business_description', ''), key="employer_business_description")
        
        return {
            'company_name': company_name, 'company_type': company_type, 'industry': industry,
            'company_size': company_size, 'business_description': business_description
        }
    
    def render_location_tab(self, user):
        """Render business location tab."""
        st.subheader("Business Location")
        
        col1, col2 = st.columns(2)
        with col1:
            address = st.text_area("Company Address", value=user.get('address', ''), key="employer_address")
            city = st.text_input("City", value=user.get('city', ''), key="employer_city")
            
            user_state = self.data_processor.safe_single_value(
                user.get('state', 'Maharashtra'), self.state_options, 'Maharashtra'
            )
            state = st.selectbox("State", self.state_options,
                               index=self.state_options.index(user_state), key="employer_state")
        
        with col2:
            pincode = st.text_input("PIN Code", value=user.get('pincode', ''), key="employer_pincode")
            website = st.text_input("Website (Optional)", value=user.get('website', ''), key="employer_website")
        
        return {
            'address': address, 'city': city, 'state': state, 'pincode': pincode, 'website': website
        }


class ProfileValidator:
    """Handles profile data validation."""
    
    @staticmethod
    def validate_job_seeker_profile(phone, aadhaar):
        """Validate job seeker profile data."""
        phone_valid = validate_phone(phone)
        aadhaar_valid = not aadhaar or validate_aadhaar(aadhaar)
        return phone_valid and aadhaar_valid
    
    @staticmethod
    def validate_employer_profile(phone):
        """Validate employer profile data."""
        return validate_phone(phone)


class ProfileManager:
    """Handles profile operations and updates."""
    
    def __init__(self):
        self.validator = ProfileValidator()
    
    def save_job_seeker_profile(self, user_id, profile_data):
        """Save job seeker profile with validation."""
        phone = profile_data.get('phone', '')
        aadhaar = profile_data.get('aadhaar', '')
        
        if self.validator.validate_job_seeker_profile(phone, aadhaar):
            updated_user = update_user_profile(user_id, profile_data)
            if updated_user:
                st.session_state.current_user = updated_user
                st.success("✅ Profile saved successfully!")
                st.balloons()
                st.rerun()
                return True
            else:
                st.error("Failed to save profile")
                return False
        else:
            st.error("Please check phone number and Aadhaar format")
            return False
    
    def save_employer_profile(self, user_id, profile_data):
        """Save employer profile with validation."""
        phone = profile_data.get('phone', '')
        
        if self.validator.validate_employer_profile(phone):
            updated_user = update_user_profile(user_id, profile_data)
            if updated_user:
                st.session_state.current_user = updated_user
                st.success("✅ Profile saved successfully!")
                st.balloons()
                st.rerun()
                return True
            else:
                st.error("Failed to save profile")
                return False
        else:
            st.error("Please check phone number format")
            return False


class JobSeekerProfile:
    """Handles job seeker profile display and management."""
    
    def __init__(self):
        self.form_renderer = JobSeekerFormRenderer()
        self.profile_manager = ProfileManager()
    
    def display(self, user):
        """Display job seeker profile form."""
        tab1, tab2, tab3 = st.tabs(["📋 Personal Info", "💼 Professional Info", "📍 Location & Contact"])
        
        with tab1:
            personal_data = self.form_renderer.render_personal_info_tab(user)
        
        with tab2:
            professional_data = self.form_renderer.render_professional_info_tab(user)
        
        with tab3:
            location_data = self.form_renderer.render_location_contact_tab(user)
        
        # Save button
        if st.button("💾 Save Profile", type="primary", use_container_width=True, key="save_job_profile"):
            profile_data = {**personal_data, **professional_data, **location_data}
            self.profile_manager.save_job_seeker_profile(user['id'], profile_data)


class EmployerProfile:
    """Handles employer profile display and management."""
    
    def __init__(self):
        self.form_renderer = EmployerFormRenderer()
        self.profile_manager = ProfileManager()
    
    def display(self, user):
        """Display employer profile form."""
        tab1, tab2, tab3 = st.tabs(["📋 Personal Info", "🏢 Company Info", "📍 Business Location"])
        
        with tab1:
            personal_data = self.form_renderer.render_personal_info_tab(user)
        
        with tab2:
            company_data = self.form_renderer.render_company_info_tab(user)
        
        with tab3:
            location_data = self.form_renderer.render_location_tab(user)
        
        # Save button
        if st.button("💾 Save Profile", type="primary", use_container_width=True, key="save_employer_profile"):
            profile_data = {**personal_data, **company_data, **location_data}
            self.profile_manager.save_employer_profile(user['id'], profile_data)


class ProfilePage:
    """Main controller for profile page."""
    
    def __init__(self):
        self.job_seeker_profile = JobSeekerProfile()
        self.employer_profile = EmployerProfile()
    
    def display(self):
        """Main method to display the appropriate profile based on user role."""
        user = st.session_state.current_user
        st.title("👤 My Profile")
        
        if user['role'] == 'job':
            self.job_seeker_profile.display(user)
        else:
            self.employer_profile.display(user)


# Preserve original function signatures - NO CHANGES to existing code needed
def job_seeker_profile():
    """Wrapper function to maintain backward compatibility."""
    user = st.session_state.current_user
    profile = JobSeekerProfile()
    profile.display(user)


def employer_profile():
    """Wrapper function to maintain backward compatibility."""
    user = st.session_state.current_user
    profile = EmployerProfile()
    profile.display(user)


def profile_page():
    """Original function - now uses OOP internally but maintains exact same behavior."""
    page = ProfilePage()
    page.display()
