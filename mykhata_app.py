import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import re

st.set_page_config(page_title="MyKhata", layout="wide")

# -------------------- Login --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 MyKhata Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    def validate_username(name):
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]+$", name))

    def validate_password(pw):
        return bool(re.match(r"^[A-Z][a-zA-Z0-9@#$%^&+=]{5,}$", pw))

    if st.button("Login"):
        if validate_username(username) and validate_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.warning("Username must be alphanumeric with first letter capitalized. Password must be alphanumeric with one special character and first letter capitalized.")
    st.stop()

# -------------------- File Path --------------------
data_file = "mykhata_data.csv"

# -------------------- Load or Create Data --------------------
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file, parse_dates=['Date'])
    else:
        df = pd.DataFrame(columns=['Date', 'Type', 'Category', 'Amount', 'Note'])
        df.to_csv(data_file, index=False)
        return df

# -------------------- Save Data --------------------
def save_data(df):
    df.to_csv(data_file, index=False)

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
        st.rerun()

# -------------------- Dashboard --------------------
def show_dashboard():
    st.title("📊 Dashboard")
    total_income = data[data['Type'] == "Income"]["Amount"].sum()
    total_expense = data[data['Type'] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.markdown(f"""
    <div style='background: #f5f7fa; border-radius: 12px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 20px;'>
        <h3>Hello, <b>{st.session_state.username}</b> 👋</h3>
        <h1>₹{balance:.2f}</h1>
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
    st.info("Share your dashboard or invite others to contribute.")
    st.text_input("Invite User Email")
    st.button("Send Invite")

# -------------------- Menu --------------------
data = load_data()
menu = st.sidebar.radio("📚 Menu", ["Home", "Add", "Reports", "Settings"])

if menu == "Home":
    show_dashboard()
elif menu == "Add":
    add_transaction()
elif menu == "Reports":
    show_reports()
elif menu == "Settings":
    show_settings()

# -------------------- Bottom Nav --------------------
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
    }
    .bottom-nav i {
        font-size: 24px;
    }
</style>
<div class='bottom-nav'>
    <i>🏠</i>
    <i>📁</i>
    <i style='font-size:36px;'>➕</i>
    <i>📊</i>
    <i>⚙️</i>
</div>
""", unsafe_allow_html=True)
