# mykhata_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Initialize session states
if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "categories" not in st.session_state:
    st.session_state.categories = {
        "income": ["Salary", "Freelance"],
        "expense": ["Food", "Clothes", "Transport"],
        "loan": ["EMI", "Society Interest"]
    }

# ----- Styling -----
st.set_page_config(page_title="MyKhata", layout="centered")
st.markdown("""
    <style>
    .big-font { font-size: 28px !important; font-weight: bold; }
    .balance-box { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 25px; border-radius: 20px; text-align: center; }
    .balance-text { font-size: 36px; font-weight: 700; color: #333; }
    .section-header { font-size: 20px; font-weight: 600; margin-top: 30px; }
    </style>
""", unsafe_allow_html=True)

# ---------- Login Simulation ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to MyKhata")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user and pwd:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Please enter both username and password")
    st.stop()

# ---------- Main App ----------
st.sidebar.title("📋 MyKhata Menu")
menu = st.sidebar.radio("Go to", ["Dashboard", "Add Transaction", "Categories", "Download Report"])

# ---------- Helper Functions ----------
def get_balance():
    df = pd.DataFrame(st.session_state.transactions)
    if df.empty:
        return 0, 0, 0
    income = df[df['type'] == 'income']['amount'].sum()
    expense = df[df['type'] == 'expense']['amount'].sum()
    loan = df[df['type'] == 'loan']['amount'].sum()
    return income, expense, income - expense - loan

# ---------- Dashboard ----------
if menu == "Dashboard":
    st.markdown("<div class='balance-box'>", unsafe_allow_html=True)
    st.markdown("<div class='big-font'>Hello, 👋 User!</div>", unsafe_allow_html=True)
    income, expense, balance = get_balance()
    st.markdown(f"<div class='balance-text'>Total Balance: ₹{balance:,.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<p>Income: ₹{income:,.2f} | Expense: ₹{expense:,.2f}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.transactions)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')

        st.markdown("<div class='section-header'>📊 Monthly Summary</div>", unsafe_allow_html=True)
        fig = px.bar(df, x='month', y='amount', color='type', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='section-header'>📒 Latest Transactions</div>", unsafe_allow_html=True)
        st.dataframe(df[['date', 'type', 'category', 'amount', 'desc']].sort_values(by='date', ascending=False).head(5))
    else:
        st.info("No transactions yet. Start by adding one!")

# ---------- Add Transaction ----------
elif menu == "Add Transaction":
    st.header("➕ Add New Transaction")
    t_type = st.selectbox("Type", ["income", "expense", "loan"])
    cat = st.selectbox("Category", st.session_state.categories[t_type])
    new_cat = st.text_input("+ Add New Category (optional)")
    amt = st.number_input("Amount", min_value=0.0, step=0.5)
    desc = st.text_input("Description")
    date = st.date_input("Date", value=datetime.today())
    if st.button("Save Transaction"):
        if new_cat:
            st.session_state.categories[t_type].append(new_cat)
            cat = new_cat
        st.session_state.transactions.append({
            "type": t_type, "category": cat, "amount": amt, "desc": desc, "date": date
        })
        st.success("Transaction added successfully ✅")

# ---------- Category Manager ----------
elif menu == "Categories":
    st.header("🗂️ Manage Categories")
    for t in ["income", "expense", "loan"]:
        st.subheader(f"{t.capitalize()} Categories")
        st.write(", ".join(st.session_state.categories[t]))

# ---------- Download Report ----------
elif menu == "Download Report":
    df = pd.DataFrame(st.session_state.transactions)
    if df.empty:
        st.info("No data available to download")
    else:
        st.download_button("📥 Download as CSV", data=df.to_csv(index=False), file_name="mykhata_report.csv", mime="text/csv")
