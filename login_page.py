import streamlit as st
from auth import login, signup

def show_login_page():
    st.set_page_config(
        page_title="Medical FAQ Chatbot - Login",
        page_icon="🩺",
        layout="centered"
    )
    
    # Center the form with custom styling
    st.markdown("""
        <style>
        .main { display: flex; justify-content: center; }
        .block-container { max-width: 450px; padding-top: 80px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center'>🩺 Medical FAQ Chatbot</h1>", unsafe_allow_html=True)
    #st.markdown("---")

    # Tab switcher for Login / Sign Up
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    # ── LOGIN TAB ──────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Welcome back!")
        login_username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_user"
        )
        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_pass"
        )

        if st.button("Login", use_container_width=True, type="primary"):
            if login_username and login_password:
                success, message = login(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username  = login_username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields.")

    # ── SIGN UP TAB ────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Create an account")
        new_username = st.text_input(
            "Choose a Username",
            placeholder="At least 3 characters",
            key="signup_user"
        )
        new_password = st.text_input(
            "Choose a Password",
            type="password",
            placeholder="At least 6 characters",
            key="signup_pass"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Repeat your password",
            key="signup_confirm"
        )

        if st.button("Create Account", use_container_width=True, type="primary"):
            success, message = signup(new_username, new_password, confirm_password)
            if success:
                st.success(message)
                st.info("Please go to the Login tab to sign in.")
            else:
                st.error(message)