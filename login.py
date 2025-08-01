
import streamlit as st
import pyrebase
from firebase_config import firebaseConfig

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

st.title("🔐 Lab Login")

choice = st.selectbox("Login or Sign Up", ["Login", "Sign Up"])
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if choice == "Login":
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success(f"Welcome, {email}!")
            st.session_state['user'] = user['email']
        except:
            st.error("Login failed. Please check your credentials.")
else:
    if st.button("Create Account"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("Account created! You can now login.")
        except:
            st.error("Signup failed. Try a different email.")
