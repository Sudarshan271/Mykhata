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

# -------------------- File Paths --------------------
data_file = "mykhata_data.csv"
users_file = "users_public_details.csv"

# -------------------- Data Load/Save --------------------
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file, parse_dates=['Date'])
    else:
        df = pd.DataFrame(columns=['Date', 'Type', 'Category', 'Amount', 'Note'])
        df.to_csv(data_file, index=False)
        return df

def save_data(df):
    df.to_csv(data_file, index=False)

def load_users():
    if os.path.exists(users_file):
        return pd.read_csv(users_file)
    else:
        df = pd.DataFrame(columns=['Username', 'Password', 'Name', 'Mobile', 'Email'])
        df.to_csv(users_file, index=False)
        return df

def save_users(df):
    df.to_csv(users_file, index=False)

# -------------------- Signup --------------------
def signup_page():
    st.markdown("""
        <div style='text-align:center;'>
            <h2>🚀 Create New MyKhata Account</h2>
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
            new_user = pd.DataFrame([[username, password, name, mobile, email]], columns=['Username', 'Password', 'Name', 'Mobile', 'Email'])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("✅ Account Created Successfully")
            st.session_state.show_signup = False
            st.experimental_rerun()

# -------------------- Login --------------------
def login_page():
    st.markdown("""
        <div style='text-align:center;'>
            <h2>🔐 Login to MyKhata</h2>
        </div>
    """, unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user_match = users[(users['Username'] == username) & (users['Password'] == password)]
        if not user_match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login Successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid Username or Password")

    if st.button("New Here? Create Account"):
        st.session_state.show_signup = True
        st.experimental_rerun()

# -------------------- Home Dashboard --------------------
def show_dashboard():
    st.markdown("<h2 style='text-align:center;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    data = load_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='background-color:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 10px rgba(0,0,0,0.2);'><h4>Total Income</h4><h2 style='color:green;'>₹{:,.2f}</h2></div>".format(data[data['Type']=='Income']['Amount'].sum()), unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='background-color:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 10px rgba(0,0,0,0.2);'><h4>Total Expense</h4><h2 style='color:red;'>₹{:,.2f}</h2></div>".format(data[data['Type']=='Expense']['Amount'].sum()), unsafe_allow_html=True)
    with col3:
        balance = data[data['Type']=='Income']['Amount'].sum() - data[data['Type']=='Expense']['Amount'].sum()
        st.markdown("<div style='background-color:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 10px rgba(0,0,0,0.2);'><h4>Net Balance</h4><h2>₹{:,.2f}</h2></div>".format(balance), unsafe_allow_html=True)

    if not data.empty:
        st.markdown("<br><h4>📈 Income vs Expense (Monthly)</h4>", unsafe_allow_html=True)
        data['Month'] = data['Date'].dt.to_period('M').astype(str)
        chart = data.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
        fig = px.line(chart, x='Month', y='Amount', color='Type', markers=True)
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br><h4>📃 Recent Transactions</h4>", unsafe_allow_html=True)
    st.dataframe(data.sort_values("Date", ascending=False).head(10), use_container_width=True)

# -------------------- Add Entry --------------------
def add_transaction():
    st.markdown("<h2>➕ Add Transaction</h2>", unsafe_allow_html=True)
    data = load_data()
    with st.form("entry_form"):
        t_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        note = st.text_input("Note")
        date = st.date_input("Date", datetime.today())
        submitted = st.form_submit_button("Save Entry")
        if submitted:
            new_row = pd.DataFrame([[date, t_type, category, amount, note]], columns=data.columns)
            data = pd.concat([data, new_row], ignore_index=True)
            save_data(data)
            st.success("✅ Transaction Saved")
            st.experimental_rerun()

# -------------------- Profile --------------------
def profile_page():
    users = load_users()
    user_data = users[users['Username'] == st.session_state.username].iloc[0]
    st.markdown("<h2>👤 Profile</h2>", unsafe_allow_html=True)
    st.text_input("Full Name", value=user_data['Name'], disabled=True)
    st.text_input("Username", value=user_data['Username'], disabled=True)
    st.text_input("Mobile", value=user_data['Mobile'], disabled=True)
    st.text_input("Email", value=user_data['Email'], disabled=True)

# -------------------- Main App --------------------
def main_app():
    with st.sidebar:
        st.markdown("""
            <div style="display:flex;justify-content:center;">
                <div style="border:1px solid #ccc;border-radius:50%;padding:8px;width:40px;height:40px;background-color:#f0f0f0;text-align:center;">
                    ☰
                </div>
            </div>
        """, unsafe_allow_html=True)
        menu = ["Home", "Add", "Reports", "Profile", "Logout"]
        selected = st.radio("", menu)

    if selected == "Home":
        show_dashboard()
    elif selected == "Add":
        add_transaction()
    elif selected == "Reports":
        st.markdown("<h2>📑 Reports Coming Soon</h2>", unsafe_allow_html=True)
    elif selected == "Profile":
        profile_page()
    elif selected == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("🔒 Logged out!")
        st.experimental_rerun()

# -------------------- App Launch --------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main_app()
