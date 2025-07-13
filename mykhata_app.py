import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="MyKhata", layout="centered")

# -------------------- Login --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 MyKhata Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.rerun()  # ✅ Replaced experimental_rerun with rerun
        else:
            st.warning("Enter both username and password")
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
    st.title("📊 MyKhata Dashboard")
    total_income = data[data['Type'] == "Income"]["Amount"].sum()
    total_expense = data[data['Type'] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.markdown("""
    <div style='background: linear-gradient(to right, #a1c4fd, #c2e9fb); padding: 20px; border-radius: 10px;'>
        <h3 style='margin: 0;'>Hello, <b>Sudarshan</b> 👋</h3>
        <h1 style='margin: 10px 0;'>₹{:.2f}</h1>
        <div style='display: flex; justify-content: space-between;'>
            <span style='color: green;'>Income: ₹{:.2f}</span>
            <span style='color: red;'>Expense: ₹{:.2f}</span>
        </div>
    </div>
    <br>
    """.format(balance, total_income, total_expense), unsafe_allow_html=True)

    # Charts
    data['Month'] = data['Date'].dt.strftime('%b %Y')
    monthly = data.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
    fig = px.bar(monthly, x='Month', y='Amount', color='Type', barmode='group', title="Monthly Overview")
    st.plotly_chart(fig, use_container_width=True)

    # Recent Transactions
    st.subheader("🧾 Recent Transactions")
    st.dataframe(data.sort_values(by="Date", ascending=False).head(5), use_container_width=True)

# -------------------- Reports --------------------
def show_reports():
    st.subheader("📁 All Transactions")
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)
    st.download_button("⬇️ Download CSV", data.to_csv(index=False), "mykhata_report.csv")

# -------------------- Menu --------------------
data = load_data()
menu = st.sidebar.selectbox("📚 Menu", ["Dashboard", "Add Transaction", "Reports"])
if menu == "Dashboard":
    show_dashboard()
elif menu == "Add Transaction":
    add_transaction()
elif menu == "Reports":
    show_reports()
