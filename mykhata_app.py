import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime

# ------------------- Setup Page -------------------
st.set_page_config(page_title="MyKhata", layout="wide")
st.markdown("""<style>footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ------------------- File Paths -------------------
data_file = "mykhata_data.csv"
users_file = "users_public_details.csv"

# ------------------- Session State -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# ------------------- Data Functions -------------------
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file, parse_dates=['Date'])
    else:
        return pd.DataFrame(columns=['Username', 'Date', 'Type', 'Category', 'Amount', 'Note'])

def save_data(df):
    df.to_csv(data_file, index=False)

def load_users():
    if os.path.exists(users_file):
        return pd.read_csv(users_file)
    else:
        return pd.DataFrame(columns=['Username', 'Password'])

def save_users(df):
    df.to_csv(users_file, index=False)

# ------------------- Signup Page -------------------
def signup():
    st.title("📝 Create Account")
    uname = st.text_input("Username (Start with capital letter, alphanumeric)")
    passwd = st.text_input("Password (Start with capital letter, alphanumeric & special char)", type="password")

    if st.button("Create"):
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", uname):
            st.warning("Username must start with uppercase and be alphanumeric")
            return
        if not re.match(r"^[A-Z][A-Za-z0-9@#$%^&+=!]+$", passwd):
            st.warning("Password must start with uppercase and have special character")
            return

        users = load_users()
        if uname in users['Username'].values:
            st.warning("Username already exists")
        else:
            users = users.append({'Username': uname, 'Password': passwd}, ignore_index=True)
            save_users(users)
            st.success("Account created! Please login.")
            st.session_state.show_signup = False

    if st.button("Back to Login"):
        st.session_state.show_signup = False

# ------------------- Login Page -------------------
def login():
    st.title("🔐 Login to MyKhata")
    uname = st.text_input("Username")
    passwd = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        match = users[(users['Username'] == uname) & (users['Password'] == passwd)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    if st.button("Create New Account"):
        st.session_state.show_signup = True

# ------------------- App Layout -------------------
def show_navbar():
    st.markdown("""
        <style>
            .nav-bar {
                position: fixed;
                bottom: 0;
                width: 100%;
                background: #e3f2fd;
                display: flex;
                justify-content: space-around;
                padding: 10px;
                box-shadow: 0 -2px 8px gray;
                z-index: 100;
            }
            .nav-icon {
                font-size: 24px;
                cursor: pointer;
            }
            .plus-btn {
                background: #2196F3;
                color: white;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                text-align: center;
                font-size: 32px;
                line-height: 60px;
                margin-top: -25px;
            }
        </style>
        <div class="nav-bar">
            <div class="nav-icon" onclick="window.location.hash='#Home'">🏠</div>
            <div class="nav-icon" onclick="window.location.hash='#Report'">📊</div>
            <div class="plus-btn" onclick="window.location.hash='#Add'">+</div>
            <div class="nav-icon" onclick="window.location.hash='#Balance'">💼</div>
            <div class="nav-icon" onclick="window.location.hash='#Profile'">👤</div>
        </div>
    """, unsafe_allow_html=True)

# ------------------- Pages -------------------
def dashboard():
    st.markdown("<h3>📊 Dashboard</h3>", unsafe_allow_html=True)
    df = load_data()
    user_df = df[df['Username'] == st.session_state.username]

    if user_df.empty:
        st.info("No transactions yet")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", user_df[user_df['Type'] == 'Income']['Amount'].sum())
    col2.metric("Total Expense", user_df[user_df['Type'] == 'Expense']['Amount'].sum())
    col3.metric("Net", user_df['Amount'].sum())

    fig = px.line(user_df, x='Date', y='Amount', color='Type', title="Monthly Overview")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("All Transactions")
    st.dataframe(user_df.sort_values('Date', ascending=False))

def add_transaction():
    st.subheader("➕ Add Transaction")
    with st.form("add_form"):
        ttype = st.selectbox("Type", ["Income", "Expense", "Loan"])
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0)
        note = st.text_area("Note")
        date = st.date_input("Date", datetime.now())
        submitted = st.form_submit_button("Save")

        if submitted:
            df = load_data()
            new_entry = pd.DataFrame.from_dict([{
                "Username": st.session_state.username,
                "Date": date,
                "Type": ttype,
                "Category": category,
                "Amount": amount,
                "Note": note
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success("Transaction saved!")


def report_page():
    st.subheader("📈 Reports")
    df = load_data()
    user_df = df[df['Username'] == st.session_state.username]
    if user_df.empty:
        st.info("No data to report")
        return
    fig = px.bar(user_df, x='Category', y='Amount', color='Type')
    st.plotly_chart(fig, use_container_width=True)

def profile_page():
    st.subheader("👤 Your Profile")
    st.write("Username:", st.session_state.username)
    st.button("Logout", on_click=lambda: logout())

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# ------------------- Main Logic -------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup()
    else:
        login()
else:
    page = st.sidebar.selectbox("Menu", ["Home", "Add", "Report", "Profile"], index=0)
    if page == "Home":
        dashboard()
    elif page == "Add":
        add_transaction()
    elif page == "Report":
        report_page()
    elif page == "Profile":
        profile_page()
    show_navbar()
