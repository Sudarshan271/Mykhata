import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import re

st.set_page_config(page_title="MyKhata Modern", layout="wide")

# -------------------- Session Init --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "account_created" not in st.session_state:
    st.session_state.account_created = False
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# -------------------- File Paths --------------------
data_file = "mykhata_data.csv"
users_file = "users_public_details.csv"
categories_file = "category_memory.csv"

# -------------------- Load/Save Functions --------------------
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file, parse_dates=['Date'])
    else:
        df = pd.DataFrame(columns=['Username', 'Date', 'Type', 'Category', 'Amount', 'Note'])
        df.to_csv(data_file, index=False)
        return df

def save_data(df):
    df.to_csv(data_file, index=False)

def load_users():
    if os.path.exists(users_file):
        return pd.read_csv(users_file)
    else:
        df = pd.DataFrame(columns=['Username', 'Password', 'Name', 'Mobile', 'Email', 'ProfilePic', 'MainAccount'])
        df.to_csv(users_file, index=False)
        return df

def save_users(df):
    df.to_csv(users_file, index=False)

def load_categories():
    if os.path.exists(categories_file):
        return pd.read_csv(categories_file)
    else:
        df = pd.DataFrame(columns=['Username', 'Type', 'Category'])
        df.to_csv(categories_file, index=False)
        return df

def save_categories(df):
    df.to_csv(categories_file, index=False)

# -------------------- Signup Page --------------------
def signup_page():
    st.markdown("""
        <div style='text-align:center;'>
            <h2>🚀 Welcome to MyKhata</h2>
            <p>Create a new account below</p>
        </div>
    """, unsafe_allow_html=True)
    name = st.text_input("Your Full Name")
    username = st.text_input("Create Username (Start with uppercase & alphanumeric)")
    password = st.text_input("Create Password (Start with uppercase, alphanumeric, special char)", type="password")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email")

    if st.button("Create Account"):
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
            st.error("❌ Invalid Username Format")
            return
        if not re.match(r"^[A-Z][A-Za-z0-9@#$%^&+=!]+$", password):
            st.error("❌ Invalid Password Format")
            return

        users = load_users()
        if username in users['Username'].values:
            st.error("⚠️ Username already exists")
        else:
            new_user = pd.DataFrame([[username, password, name, mobile, email, "", ""]], columns=['Username', 'Password', 'Name', 'Mobile', 'Email', 'ProfilePic', 'MainAccount'])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("✅ Account Created Successfully! Please login below.")
            st.session_state.show_signup = False
            st.session_state.account_created = True

# -------------------- Login Page --------------------
def login_page():
    st.markdown("""
        <div style='text-align:center;'>
            <h2>🔐 Login to MyKhata</h2>
            <p>🎉 Welcome to MyKhata – Manage your money smartly.</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("account_created"):
        st.success("✅ Account created. Please login.")
        st.session_state.account_created = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user_match = users[(users['Username'] == username) & (users['Password'] == password)]
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login Successful! Redirecting...")
            st.session_state.active_page = "Home"
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password")

    if st.button("New Here? Create Account"):
        st.session_state.show_signup = True
        st.rerun()

# -------------------- Main Pages --------------------
def show_dashboard():
    st.write("📊 Dashboard page (Will include card + graph + filters + transactions)")

def add_transaction():
    st.write("➕ Add transaction form")

def profile_page():
    st.write("👤 Profile & invite page")

def report_page():
    st.write("📈 Reports by category/date")

def wallet_page():
    st.write("💼 Wallet overview")

# -------------------- App Framework --------------------
def main_app():
    # Top bar or sidebar nav with hide logic
    menu = st.sidebar.radio("Menu", ["Home", "Add", "Wallet", "Report", "Profile", "Logout"])
    st.session_state.active_page = menu

    if menu == "Home": show_dashboard()
    elif menu == "Add": add_transaction()
    elif menu == "Wallet": wallet_page()
    elif menu == "Report": report_page()
    elif menu == "Profile": profile_page()
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    # Floating Nav Bar
    st.markdown("""
    <style>
        .floating-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #e3f2fd;
            display: flex;
            justify-content: space-around;
            padding: 10px;
            box-shadow: 0 -2px 8px gray;
            z-index: 999;
        }
        .floating-bar div {
            text-align: center;
            font-size: 22px;
        }
        .plus-button {
            background: #2196F3;
            color: white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 30px;
            text-align: center;
            line-height: 60px;
            margin-top: -30px;
        }
    </style>
    <div class='floating-bar'>
        <div onclick='window.location.reload()'>🏠</div>
        <div onclick='window.location.reload()'>📊</div>
        <div class='plus-button' onclick='window.location.reload()'>+</div>
        <div onclick='window.location.reload()'>📁</div>
        <div onclick='window.location.reload()'>⚙️</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Launch --------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main_app()
