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
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

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
        df = pd.DataFrame(columns=['Username', 'Password', 'Name'])
        df.to_csv(users_file, index=False)
        return df

def save_users(df):
    df.to_csv(users_file, index=False)

# -------------------- Sign Up --------------------
def signup_page():
    st.title("👋 Welcome to MyKhata")
    st.subheader("Create a New Account")

    name = st.text_input("Full Name")
    username = st.text_input("Create Username (Start with uppercase & alphanumeric)")
    password = st.text_input("Create Password (Uppercase start, alphanumeric & special char)")

    if st.button("Create Account"):
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
            st.error("Invalid username format. Must start with uppercase and be alphanumeric.")
            return
        if not re.match(r"^[A-Z][A-Za-z0-9@#$%^&+=!]+$", password):
            st.error("Invalid password format. Must start with uppercase and include a special character.")
            return

        users = load_users()
        if username in users['Username'].values:
            st.error("Username already exists. Please choose another one.")
        else:
            new_user = pd.DataFrame([[username, password, name]], columns=['Username', 'Password', 'Name'])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("🎉 Account Created! You can now log in.")
            st.session_state.show_signup = False
            st.experimental_rerun()
    st.stop()

# -------------------- Login Page --------------------
def login_page():
    st.title("👋 Welcome to MyKhata")
    st.subheader("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user_match = users[(users['Username'] == username) & (users['Password'] == password)]
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Incorrect Username or Password")

    if st.button("New User? Create an Account"):
        st.session_state.show_signup = True
        st.experimental_rerun()
    st.stop()

# -------------------- Main App Pages --------------------
def main_app():
    st.sidebar.title("MyKhata Menu")
    choice = st.sidebar.radio("Go to", ["Home", "Reports", "Balance", "Settings", "Logout"])
    st.session_state.active_page = choice

    if choice == "Home":
        st.title("📊 Dashboard")
        data = load_data()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"₹{data[data['Type']=='Income']['Amount'].sum():,.2f}")
        with col2:
            st.metric("Total Expenses", f"₹{data[data['Type']=='Expense']['Amount'].sum():,.2f}")
        with col3:
            balance = data[data['Type']=='Income']['Amount'].sum() - data[data['Type']=='Expense']['Amount'].sum()
            st.metric("Net Balance", f"₹{balance:,.2f}")

        st.subheader("Monthly Overview")
        if not data.empty:
            data['Month'] = data['Date'].dt.to_period('M').astype(str)
            chart = data.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
            fig = px.line(chart, x='Month', y='Amount', color='Type', markers=True, title="Income vs Expense Over Time")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent Transactions")
        st.dataframe(data.sort_values("Date", ascending=False).head(10), use_container_width=True)

    elif choice == "Reports":
        st.title("📈 Reports")
        st.info("Detailed reports will be available here.")

    elif choice == "Balance":
        st.title("💰 Balance Sheet")
        st.info("Detailed balance sheet coming soon.")

    elif choice == "Settings":
        st.title("⚙️ Settings")
        st.info("User settings and profile options will be here.")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully!")
        st.experimental_rerun()

# -------------------- Auth Check --------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
    st.stop()

# -------------------- Run Main App --------------------
main_app()
