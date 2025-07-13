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
        df = pd.DataFrame(columns=['Username', 'Password', 'Name', 'Mobile', 'Email'])
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
            new_user = pd.DataFrame([[username, password, name, mobile, email]], columns=['Username', 'Password', 'Name', 'Mobile', 'Email'])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("✅ Account Created Successfully")
            st.session_state.show_signup = False
            st.experimental_rerun()

# -------------------- Login Page --------------------
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

# -------------------- Dashboard --------------------
def show_dashboard():
    st.markdown("""<h2 style='text-align:center;'>📊 Dashboard</h2>""", unsafe_allow_html=True)
    df = load_data()
    df = df[df['Username'] == st.session_state.username]

    col1, col2, col3 = st.columns(3)
    with col1:
        income = df[df['Type'] == 'Income']['Amount'].sum()
        st.markdown(f"<div style='background:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 8px gray'><h4>Total Income</h4><h2 style='color:green;'>₹{income:,.2f}</h2></div>", unsafe_allow_html=True)
    with col2:
        expense = df[df['Type'] == 'Expense']['Amount'].sum()
        st.markdown(f"<div style='background:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 8px gray'><h4>Total Expense</h4><h2 style='color:red;'>₹{expense:,.2f}</h2></div>", unsafe_allow_html=True)
    with col3:
        balance = income - expense
        st.markdown(f"<div style='background:#e3f2fd;padding:20px;border-radius:15px;box-shadow:2px 4px 8px gray'><h4>Net Balance</h4><h2>₹{balance:,.2f}</h2></div>", unsafe_allow_html=True)

    if not df.empty:
        st.markdown("<br><h4>📈 Trend (Choose Range)</h4>", unsafe_allow_html=True)
        range_opt = st.selectbox("Select", ["Daily", "Monthly", "Yearly"])
        if range_opt == "Monthly":
            df['Period'] = df['Date'].dt.to_period('M').astype(str)
        elif range_opt == "Yearly":
            df['Period'] = df['Date'].dt.to_period('Y').astype(str)
        else:
            df['Period'] = df['Date'].dt.date.astype(str)

        chart = df.groupby(['Period', 'Type'])['Amount'].sum().reset_index()
        fig = px.line(chart, x='Period', y='Amount', color='Type', markers=True)
        fig.update_traces(line=dict(width=2))
        fig.update_layout(xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br><h4>🧾 Recent Transactions</h4>", unsafe_allow_html=True)
    st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)

# -------------------- Add Entry --------------------
def add_transaction():
    st.markdown("<h2>➕ Add Transaction</h2>", unsafe_allow_html=True)
    df = load_data()
    cat_df = load_categories()
    user_cats = cat_df[cat_df['Username'] == st.session_state.username]

    with st.form("entry_form", clear_on_submit=True):
        t_type = st.selectbox("Type", ["Income", "Expense", "Loan"])
        existing = user_cats[user_cats['Type'] == t_type]['Category'].unique().tolist()
        category = st.selectbox("Category", existing + ["+ Add New"])
        if category == "+ Add New":
            category = st.text_input("New Category")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        note = st.text_input("Note")
        date = st.date_input("Date", datetime.today())

        submitted = st.form_submit_button("Save Entry")
        if submitted:
            new_entry = pd.DataFrame([[st.session_state.username, date, t_type, category, amount, note]], columns=df.columns)
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)

            if category not in existing:
                cat_df = pd.concat([cat_df, pd.DataFrame([[st.session_state.username, t_type, category]], columns=cat_df.columns)], ignore_index=True)
                save_categories(cat_df)

            st.success("✅ Entry Saved!")
            st.experimental_rerun()

# -------------------- Profile --------------------
def profile_page():
    users = load_users()
    user_data = users[users['Username'] == st.session_state.username].iloc[0]
    st.markdown("<h2>👤 Profile</h2>", unsafe_allow_html=True)
    name = st.text_input("Name", value=user_data['Name'])
    mobile = st.text_input("Mobile", value=user_data['Mobile'])
    email = st.text_input("Email", value=user_data['Email'])
    if st.button("Save Profile"):
        users.loc[users['Username'] == st.session_state.username, ['Name', 'Mobile', 'Email']] = [name, mobile, email]
        save_users(users)
        st.success("✅ Profile Updated")

# -------------------- Main App --------------------
def main_app():
    with st.sidebar:
        st.markdown("""
        <style>
        .css-1oe5cao, .stRadio > div {
            flex-direction: column !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:center;margin-bottom:10px">
            <div style="border-radius:50%;padding:8px;width:40px;height:40px;background:#f0f0f0;text-align:center;">
                <b>≡</b>
            </div>
        </div>""", unsafe_allow_html=True)
        menu = st.radio("Menu", ["Home", "Wallet", "Add", "Report", "Profile", "Logout"])

    if menu == "Home":
        show_dashboard()
    elif menu == "Add":
        add_transaction()
    elif menu == "Wallet":
        show_dashboard()
    elif menu == "Report":
        show_dashboard()
    elif menu == "Profile":
        profile_page()
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("🔒 Logged out!")
        st.experimental_rerun()

    # Bottom Floating Nav
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
        }
        .floating-bar div {
            text-align: center;
            font-size: 20px;
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
            <div>🏠</div>
            <div>📊</div>
            <div class='plus-button'>+</div>
            <div>📁</div>
            <div>⚙️</div>
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
