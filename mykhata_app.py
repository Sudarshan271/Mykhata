import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="MyKhata Dashboard", layout="wide")

# --- SIDEBAR MENU ---
st.sidebar.title("📘 MyKhata")
menu = st.sidebar.radio("Navigate", ["🏠 Dashboard", "➕ Add Entry", "📊 Reports", "ℹ️ About"])

# --- INITIALIZE DATA ---
@st.cache_data
def load_data():
    return pd.DataFrame(columns=["Date", "Month", "Year", "Type", "Category", "Amount"])

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- MENU: ADD ENTRY ---
if menu == "➕ Add Entry":
    st.title("➕ Add Income or Expense")

    entry_type = st.selectbox("Type", ["Income", "Expense", "Loan"])
    category = st.text_input("Category (e.g., Salary, Rent, Shopping, EMI)")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    date = st.date_input("Date", datetime.today())

    if st.button("Add Entry"):
        new_row = {
            "Date": date,
            "Month": date.strftime("%B"),
            "Year": date.year,
            "Type": entry_type,
            "Category": category,
            "Amount": amount
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ Entry added!")

# --- MENU: DASHBOARD ---
elif menu == "🏠 Dashboard":
    st.title("📊 Monthly Summary Dashboard")

    df = st.session_state.data
    if df.empty:
        st.info("No data yet. Go to ➕ Add Entry to get started.")
    else:
        # --- Summary Cards ---
        col1, col2, col3, col4 = st.columns(4)
        income = df[df.Type == "Income"]["Amount"].sum()
        expense = df[df.Type == "Expense"]["Amount"].sum()
        loan = df[df.Type == "Loan"]["Amount"].sum()
        balance = income - expense - loan

        col1.metric("🟢 Total Income", f"₹ {income:,.2f}")
        col2.metric("🔴 Total Expenses", f"₹ {expense:,.2f}")
        col3.metric("🏦 Loan Outflow", f"₹ {loan:,.2f}")
        col4.metric("💰 Balance", f"₹ {balance:,.2f}")

        # --- Monthly Trend Chart ---
        df['Year-Month'] = pd.to_datetime(df['Date']).dt.to_period('M').astype(str)
        monthly = df.groupby(['Year-Month', 'Type'])['Amount'].sum().reset_index()
        fig = px.line(monthly, x='Year-Month', y='Amount', color='Type', markers=True, title="📈 Monthly Trends")
        st.plotly_chart(fig, use_container_width=True)

# --- MENU: REPORTS ---
elif menu == "📊 Reports":
    st.title("📋 Detailed Report")
    df = st.session_state.data
    if df.empty:
        st.info("No data yet.")
    else:
        with st.expander("🔍 Filter Options"):
            year_filter = st.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
            type_filter = st.multiselect("Type", df["Type"].unique(), default=df["Type"].unique())
            df = df[(df["Year"].isin(year_filter)) & (df["Type"].isin(type_filter))]

        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

        pie = df.groupby("Type")["Amount"].sum().reset_index()
        fig2 = px.pie(pie, values='Amount', names='Type', title='Expense vs Income Distribution')
        st.plotly_chart(fig2, use_container_width=True)

# --- ABOUT ---
elif menu == "ℹ️ About":
    st.title("ℹ️ About MyKhata")
    st.markdown("""
        **MyKhata** is a simple, modern personal expense tracking app built with Streamlit.

        **Features:**
        - Add & categorize income, expenses, and loans
        - View beautiful charts and summaries
        - Track spending over time
        - Mobile-friendly and installable as PWA

        💡 *Made by Sudarshan Nayak*
    """)
