import streamlit as st
import yaml
import os
from yaml.loader import SafeLoader
from passlib.hash import pbkdf2_sha256

# --- CONFIG PATH ---
CONFIG_PATH = "config.yaml"

# --- Load or create user config file ---
if not os.path.exists(CONFIG_PATH):
    default_config = {
        "credentials": {"usernames": {}},
        "cookie": {
            "name": "auth_cookie",
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

# --- TOGGLE VIEW ---
def switch_to_register():
    st.session_state.view_state = "register"
    st.rerun()

def switch_to_login():
    st.session_state.view_state = "login"
    st.rerun()

# --- MAIN APP LOGIC ---
if st.session_state["authentication_status"]:
    st.title("✅ You are logged in!")
    st.write(f"Welcome, {st.session_state['name']}!")
    st.button("Logout") # This button is for visual representation, actual logout logic is complex

else:
    if st.session_state.view_state == "login":
        st.title("🔐 Login Test")
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
        st.title("📝 Register New User Test")
        st.markdown("---")

        with st.form("register_form"):
            new_name = st.text_input("👤 Full Name", key="reg_name")
            new_username = st.text_input("💻 Username", key="reg_username")
            new_password = st.text_input("🔒 Password", type="password", key="reg_password")

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