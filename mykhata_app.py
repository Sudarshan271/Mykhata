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
                    st.stop()
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
        signup_page()
    st.stop()

# -------------------- Add Transaction --------------------
def add_transaction():
    st.subheader("➕ Add Transaction")
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.selectbox("Type", ["Income", "Expense", "Loan"])
        date = st.date_input("Date", datetime.today())
    with col2:
        category_list = list(data[data['Type'] == t_type]['Category'].unique())
        category = st.selectbox("Category", category_list + ["+ Add new"])
        if category == "+ Add new":
            category = st.text_input("Enter New Category")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    note = st.text_input("Note")

    if st.button("💾 Save Transaction"):
        new_data = pd.DataFrame({
            'Date': [pd.to_datetime(date)],
            'Type': [t_type],
            'Category': [category],
            'Amount': [amount],
            'Note': [note]
        })
        updated = pd.concat([data, new_data], ignore_index=True)
        save_data(updated)
        st.success("Transaction Added Successfully!")
        st.experimental_rerun()

# -------------------- Dashboard --------------------
def show_dashboard():
    st.markdown(f"""
    <div style='background: #e6f2ff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px;'>
        <h3>Hello, <b>{st.session_state.username}</b> 👋</h3>
        <h1>Balance: ₹{balance:.2f}</h1>
        <p style='color:green;'>Income: ₹{total_income:.2f} &nbsp;&nbsp;&nbsp; <span style='color:red;'>Expense: ₹{total_expense:.2f}</span></p>
    </div>
    """, unsafe_allow_html=True)

    filter_option = st.selectbox("Filter", ["Monthly", "Daily", "Yearly"])
    if filter_option == "Monthly":
        data['Period'] = data['Date'].dt.to_period('M').astype(str)
    elif filter_option == "Daily":
        data['Period'] = data['Date'].dt.to_period('D').astype(str)
    else:
        data['Period'] = data['Date'].dt.to_period('Y').astype(str)
    chart_data = data.groupby(['Period', 'Type'])['Amount'].sum().reset_index()
    fig = px.bar(chart_data, x='Period', y='Amount', color='Type', barmode='group', title=f"{filter_option} Overview")
    fig.update_traces(marker_line_width=0.5)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧾 All Transactions")
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)

# -------------------- Reports --------------------
def show_reports():
    st.subheader("📁 Reports")
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)
    st.download_button("⬇️ Download CSV", data.to_csv(index=False), "mykhata_report.csv")

# -------------------- Settings --------------------
def show_settings():
    st.subheader("⚙️ Settings")
    st.text_input("Name")
    st.text_input("Email")
    st.text_input("Mobile Number")
    st.file_uploader("Upload Profile Picture")
    st.markdown("---")
    st.subheader("👥 Invite User")
    invite_mobile = st.text_input("Invite via Mobile")
    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password")
    if st.button("Send Invite"):
        users = load_users()
        if invite_mobile in users['Mobile'].values:
            st.error("Mobile number already registered.")
        else:
            users = pd.concat([users, pd.DataFrame([[invite_mobile, new_user, new_pass, '', '']], columns=['Mobile', 'Username', 'Password', 'Name', 'Email'])], ignore_index=True)
            save_users(users)
            st.success("User Invited Successfully")

# -------------------- Logout --------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()

# -------------------- Auth Check --------------------
if not st.session_state.logged_in:
    login_page()

# -------------------- Load Data --------------------
data = load_data()
total_income = data[data['Type'] == "Income"]["Amount"].sum()
total_expense = data[data['Type'] == "Expense"]["Amount"].sum()
balance = total_income - total_expense

# -------------------- Sidebar Menu --------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2922/2922510.png", width=80)
st.sidebar.markdown(f"### Welcome, {st.session_state.username}")
menu = st.sidebar.radio("📚 Menu", ["Home", "Add", "Reports", "Settings", "Logout"])

if menu == "Home":
    show_dashboard()
elif menu == "Add":
    add_transaction()
elif menu == "Reports":
    show_reports()
elif menu == "Settings":
    show_settings()
elif menu == "Logout":
    logout()

# -------------------- Bottom Navigation --------------------
st.markdown("""
<style>
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #fff;
    padding: 10px;
    box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-around;
    z-index: 9999;
}
.bottom-nav i {
    font-size: 22px;
    color: #333;
}
.plus-icon {
    font-size: 36px;
    background: #66ccff;
    border-radius: 50%;
    padding: 6px 14px;
    color: white;
    margin-top: -10px;
}
</style>
<div class='bottom-nav'>
    <i>🏠</i>
    <i>📊</i>
    <i class='plus-icon'>➕</i>
    <i>💼</i>
    <i>⚙️</i>
</div>
""", unsafe_allow_html=True)
