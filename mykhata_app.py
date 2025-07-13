import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import re

st.set_page_config(page_title="MyKhata", layout="wide")

# -------------------- Session Init --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# -------------------- File Path --------------------
data_file = "mykhata_data.csv"
users_file = "users_public_details.csv"

# -------------------- Load or Create Data --------------------
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file, parse_dates=['Date'])
    else:
        df = pd.DataFrame(columns=['Date', 'Type', 'Category', 'Amount', 'Note'])
        df.to_csv(data_file, index=False)
        return df

def save_data(df):
    df.to_csv(data_file, index=False)

# -------------------- Load Users --------------------
def load_users():
    if os.path.exists(users_file):
        return pd.read_csv(users_file)
    else:
        df = pd.DataFrame(columns=['Mobile', 'Username', 'Password', 'Name', 'Email'])
        df.to_csv(users_file, index=False)
        return df

def save_users(df):
    df.to_csv(users_file, index=False)

# -------------------- Sign Up --------------------
def signup_page():
    st.title("📱 Register via Mobile OTP")
    mobile = st.text_input("Mobile Number")
    if st.button("Send OTP"):
        st.success("OTP sent successfully to " + mobile)
        otp = st.text_input("Enter OTP")
        if otp == "123456":
            st.success("Mobile Verified!")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            username = st.text_input("Create Username (Start with uppercase & alphanumeric)")
            password = st.text_input("Create Password (Uppercase start, alphanumeric & special char)")

            if st.button("Create Account"):
                if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
                    st.error("Invalid username format.")
                    return
                if not re.match(r"^[A-Z][A-Za-z0-9@#$%^&+=!]+$", password):
                    st.error("Invalid password format.")
                    return

                users = load_users()
                if mobile in users['Mobile'].values:
                    st.error("Account already exists with this mobile number.")
                else:
                    new_user = pd.DataFrame([[mobile, username, password, name, email]], columns=['Mobile', 'Username', 'Password', 'Name', 'Email'])
                    users = pd.concat([users, new_user], ignore_index=True)
                    save_users(users)
                    st.success("Account Created! You can now log in.")
                    st.session_state.show_signup = False
                    st.experimental_rerun()
    st.stop()

# -------------------- Login Page --------------------
def login_page():
    st.title("🔐 MyKhata Login")
    mobile = st.text_input("Mobile Number")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user_match = users[(users['Mobile'] == mobile) & (users['Password'] == password)]
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.username = user_match.iloc[0]['Username']
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Incorrect Mobile Number or Password")

    if st.button("Create New Account"):
        st.session_state.show_signup = True
        st.experimental_rerun()
    st.stop()

# -------------------- Auth Check --------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
    st.stop()
