import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# --- App Config ---
st.set_page_config(page_title="MyKhata Modern", layout="wide")

# --- Session State Setup ---
for key in ["logged_in", "username", "show_signup", "account_created", "active_page"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else ""

# --- File Paths ---
DATA_FILE = "mykhata_data.csv"
USERS_FILE = "users_public_details.csv"

# --- Load Functions ---
def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        df = pd.DataFrame(columns=["Username", "Password", "Name", "Mobile", "Email"])
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# --- Login Page ---
def login_page():
    st.markdown("## 🎉 Welcome to MyKhata – Manage your money smartly.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        match = users[(users["Username"] == username) & (users["Password"] == password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login Successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

    if st.button("Create a new account"):
        st.session_state.show_signup = True
        st.experimental_rerun()

# --- Signup Page ---
def signup_page():
    st.markdown("## 📝 Create New Account")

    name = st.text_input("Your Name")
    username = st.text_input("Username (Start with uppercase)")
    password = st.text_input("Password (Start with uppercase, include symbol)", type="password")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email Address")

    if st.button("Create Account"):
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
            st.error("Username must start with uppercase & be alphanumeric")
            return
        if not re.match(r"^[A-Z].*[!@#$%^&*]", password):
            st.error("Password must start with uppercase and include a special character")
            return

        users = load_users()
        if username in users["Username"].values:
            st.error("Username already exists")
        else:
            new_user = pd.DataFrame([[username, password, name, mobile, email]],
                columns=["Username", "Password", "Name", "Mobile", "Email"])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("Account created successfully!")
            st.session_state.show_signup = False
            st.session_state.account_created = True
            st.experimental_rerun()

# --- Navigation Bar ---
def bottom_navbar():
    st.markdown("""
    <style>
    .bottom-bar {
        position: fixed;
        bottom: 0;
        width: 100%;
        display: flex;
        justify-content: space-around;
        background: #e3f2fd;
        padding: 10px 0;
        box-shadow: 0 -2px 8px gray;
        z-index: 999;
    }
    .icon-button {
        font-size: 24px;
        cursor: pointer;
    }
    .plus-btn {
        font-size: 28px;
        color: white;
        background: #2196F3;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        line-height: 50px;
        text-align: center;
        margin-top: -25px;
    }
    </style>
    <div class="bottom-bar">
        <div onclick="window.location.href='/?nav=Home'" class="icon-button">🏠</div>
        <div onclick="window.location.href='/?nav=Wallet'" class="icon-button">💰</div>
        <div onclick="window.location.href='/?nav=Add'" class="plus-btn">+</div>
        <div onclick="window.location.href='/?nav=Report'" class="icon-button">📊</div>
        <div onclick="window.location.href='/?nav=Profile'" class="icon-button">⚙️</div>
    </div>
    """, unsafe_allow_html=True)

# --- Pages ---
def dashboard():
    st.markdown(f"## 👋 Hello, {st.session_state.username}")
    st.markdown("""
        <div style='background-color:#e3f2fd;padding:20px;border-radius:10px;box-shadow:2px 2px 10px #ccc;'>
            <h4>📈 Your financial summary will be here.</h4>
            <p>Charts and balances with filter coming soon...</p>
        </div>
    """, unsafe_allow_html=True)

def add_transaction():
    st.header("➕ Add Transaction")
    st.success("Transaction form coming soon...")

def wallet():
    st.header("💼 Wallet Overview")
    st.info("Balance data coming soon...")

def report():
    st.header("📊 Reports")
    st.info("Report filters and graphs coming soon...")

def profile():
    st.header("👤 Profile Settings")
    st.info("Invite users & update profile coming soon...")

# --- Main App ---
def main():
    nav = st.query_params.get("nav") or "Home"
    st.session_state.active_page = nav

    if nav == "Home":
        dashboard()
    elif nav == "Add":
        add_transaction()
    elif nav == "Wallet":
        wallet()
    elif nav == "Report":
        report()
    elif nav == "Profile":
        profile()

    bottom_navbar()

# --- Launch App ---
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main()
