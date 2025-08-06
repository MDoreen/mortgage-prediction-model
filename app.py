import streamlit as st
import pandas as pd
import numpy as np
import pickle
import yaml
import os
import shutil
from datetime import datetime
from yaml.loader import SafeLoader
from passlib.hash import pbkdf2_sha256

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nairobi Smart Mortgage", layout="wide")

# --- CONFIG PATH ---
CONFIG_PATH = "config.yaml"

# --- Load or create user config file ---
if not os.path.exists(CONFIG_PATH):
    default_config = {
        "credentials": {"usernames": {}},
        "cookie": {
            "name": "mortgage_cookie",
            "key": "signature_key",
            "expiry_days": 30
        }
    }
    with open(CONFIG_PATH, "w") as file:
        yaml.dump(default_config, file)

with open(CONFIG_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- SESSION STATE CONTROL ---
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = None
if "view_state" not in st.session_state:
    st.session_state.view_state = "login"
if "name" not in st.session_state:
    st.session_state.name = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- LOGOUT ---
def logout_user():
    st.session_state.authentication_status = None
    st.session_state.view_state = "login"
    st.session_state.name = None
    st.session_state.username = None
    st.success("You have been logged out.")
    st.rerun()

# --- TOGGLE VIEW ---
def switch_to_register():
    st.session_state.view_state = "register"
    st.rerun()

def switch_to_login():
    st.session_state.view_state = "login"
    st.rerun()

# --- MAIN APP LOGIC ---
if st.session_state["authentication_status"]:
    # --- LOGGED IN USER VIEW (Your original prediction app) ---
    st.sidebar.title(f"Welcome, {st.session_state['name']}! 🎉")
    st.sidebar.button("🔓 Logout", on_click=logout_user)

    # --- ADMIN CONTROL TO CLEAR USERS ---
    if st.session_state["username"] and st.session_state["username"].lower() == "doreen":
        st.sidebar.markdown("### 🔧 Admin Controls")
        with st.sidebar.expander("🧹 Clear User Logins", expanded=False):
            st.info("This will delete all user accounts except for the admin.")
            confirm = st.checkbox("Yes, I'm sure I want to clear users")
            keep_admin = st.checkbox("✅ Keep my (admin) account", value=True)

            if st.button("🗑️ Clear Users"):
                if confirm:
                    backup_name = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                    shutil.copy(CONFIG_PATH, backup_name)

                    if keep_admin:
                        admin_data = config['credentials']['usernames'].get("doreen")
                        config['credentials']['usernames'] = {"doreen": admin_data}
                    else:
                        config['credentials']['usernames'] = {}

                    with open(CONFIG_PATH, "w") as file:
                        yaml.dump(config, file)

                    st.success(f"✅ Users cleared. Backup saved as `{backup_name}`")
                else:
                    st.warning("⚠️ Please confirm before deleting users.")

    # --- Your Original Mortgage Predictor App Content ---
    with open("MortgageApp_model.pkl", "rb") as f:
        model = pickle.load(f)

    expected_features = model.feature_names_in_

    location_options = [
        'Karen', 'Kiambu Road', 'Kileleshwa', 'Kilimani', 'Kitisuru', 'Kyuna',
        'Lavington', 'Loresho', 'Lower Kabete', 'Mombasa Rd', 'Muthaiga',
        'Muthaiga North', 'Nairobi West', 'Ngong Rd', 'Nyari', 'Ongata Rongai',
        'Parklands', 'Riverside', 'Rosslyn', 'Runda', 'Syokimau', 'Thigiri',
        'Thome', 'Waithaka', 'Westlands', 'Kabete'
    ]

    st.title("🏠 Nairobi Smart Mortgage Price Predictor")

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### 📌 About this App")
        st.markdown("""
        This interactive tool uses a **Random Forest Regression model** to estimate mortgage property prices in Nairobi.

        #### 🔍 Key Features:
        - 🛏️ Bedrooms
        - 🚿 Bathrooms
        - 📐 House Size (m²)
        - 🌍 Land Size (acres)
        - 📍 Location

        ---
        🛠️ *Built as part of a project titled:*
        **A Predictive Model for Mortgage Prices Using Random Forest Regression**
        """)

    with right_col:
        st.markdown("### 💼 Enter Property Features")

        with st.form("input_form"):
            bedroom = st.slider("Number of Bedrooms", 1, 10, 3)
            bathroom = st.slider("Number of Bathrooms", 1, 10, 2)
            house_size = st.number_input("House Size (m²)", min_value=10.0, value=100.0)
            land_size = st.number_input("Land Size (acres)", min_value=0.01, value=0.25)
            location = st.selectbox("Select Location", location_options)
            submitted = st.form_submit_button("Predict Price")

        if submitted:
            input_dict = {
                "Bedroom": bedroom,
                "bathroom": bathroom,
                "House size": house_size,
                "Land size": land_size,
            }
            for loc in location_options:
                input_dict[f"Location_{loc}"] = 1 if loc == location else 0

            input_df = pd.DataFrame([input_dict])
            for col in expected_features:
                if col not in input_df.columns:
                    input_df[col] = 0
            input_df = input_df[expected_features]

            try:
                log_price = model.predict(input_df)[0]
                price = np.exp(log_price)
                st.success(f"💰 **Estimated Property Price:** KSh {price:,.0f}")
            except Exception as e:
                st.error(f"❌ Prediction failed: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚠️ Disclaimer")
    st.sidebar.info(
        "This app provides **estimated property prices** based on historical data.\n\n"
        "Actual prices may vary depending on market conditions, developer, and timing.\n\n"
        "**Designed by: Doreen Machoni**"
    )

else:
    # --- LOGIN/REGISTER VIEW ---
    if st.session_state.view_state == "login":
        st.title("🔐 Login")
        st.markdown("---")
        
        with st.form(key="login_form"):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

        if login_button:
            usernames = config['credentials']['usernames']
            if username_input in usernames:
                stored_password_hash = usernames[username_input]['password']
                
                if pbkdf2_sha256.verify(password_input, stored_password_hash):
                    st.session_state.authentication_status = True
                    st.session_state.name = usernames[username_input]['name']
                    st.session_state.username = username_input
                    st.success(f"Welcome, {st.session_state.name}!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")
            else:
                st.error("❌ Incorrect username or password")
        
        st.markdown("---")
        st.info("Don't have an account?")
        if st.button("📝 Register Now", on_click=switch_to_register):
            pass

    elif st.session_state.view_state == "register":
        st.title("📝 Register New User")
        st.markdown("---")
        st.write("Join the platform to get your personalized property price predictions.")

        with st.form("register_form"):
            new_name = st.text_input("👤 Full Name", key="reg_name", placeholder="e.g., John Doe")
            new_username = st.text_input("💻 Username", key="reg_username", placeholder="e.g., johndoe")
            new_password = st.text_input("🔒 Password", type="password", key="reg_password", placeholder="Enter a secure password")
            
            st.markdown("---")
            submit = st.form_submit_button("✅ Register Now")

            if submit:
                if new_username in config['credentials']['usernames']:
                    st.error("🚫 Username already exists")
                elif not (new_name and new_username and new_password):
                    st.warning("⚠️ Please fill in all fields")
                else:
                    try:
                        hashed_pw = pbkdf2_sha256.hash(new_password)
                        
                        config['credentials']['usernames'][new_username] = {
                            "name": new_name,
                            "password": hashed_pw
                        }
                        with open(CONFIG_PATH, "w") as file:
                            yaml.dump(config, file)
                        st.success("✅ Registered successfully! Please login.")
                        switch_to_login()
                    except Exception as e:
                        st.error(f"An error occurred during registration: {e}")
                        
        st.markdown("---")
        st.info("Already have an account?")
        if st.button("🔐 Login Now", on_click=switch_to_login):
            pass