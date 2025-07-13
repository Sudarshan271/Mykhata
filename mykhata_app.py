
import streamlit as st

st.set_page_config(page_title='MyKhata - Smart Expense Tracker', layout='centered')
st.title('📘 MyKhata - Personal Expense Manager')

# Income
st.header('💰 Income')
salary = st.number_input('Monthly Salary (₹)', min_value=0)
extra = st.number_input('Extra Income (₹)', min_value=0)
total_income = salary + extra
st.success(f'Total Income: ₹ {total_income}')

# Loan / EMI
st.header('🏦 Loan / EMI / Interest')
loan_type = st.selectbox('Loan Type', ['None', 'EMI Only', 'Interest Only', 'EMI + Interest', 'Society Loan'])
emi = interest = deposit = 0

if loan_type == 'EMI Only':
    emi = st.number_input('EMI Amount (₹)', min_value=0)
elif loan_type == 'Interest Only':
    interest = st.number_input('Interest Amount (₹)', min_value=0)
elif loan_type == 'EMI + Interest':
    emi = st.number_input('EMI Amount (₹)', min_value=0)
    interest = st.number_input('Interest Amount (₹)', min_value=0)
elif loan_type == 'Society Loan':
    deposit = st.number_input('Society Deposit (₹)', min_value=0)
    interest = st.number_input('Interest Paid (₹)', min_value=0)

loan_total = emi + interest + deposit
st.info(f'Loan Related Outflow: ₹ {loan_total}')

# Expenses
st.header('🧾 Monthly Expenses')
categories = ['Vegetables', 'Food', 'Petrol', 'Electricity Bill', 'Gas', 'Travel', 'Shopping', 'Rent', 'Medical', 'Others']
expenses = {cat: st.number_input(f'{cat} (₹)', min_value=0) for cat in categories}
total_expenses = sum(expenses.values())
total_outflow = total_expenses + loan_total
balance = total_income - total_outflow

st.warning(f'Total Household Expenses: ₹ {total_expenses}')
st.error(f'Total Outflow: ₹ {total_outflow}')

# Summary
st.header('📌 Summary')
st.markdown(f'**💵 Income:** ₹ {total_income}')
st.markdown(f'**📉 Expenses:** ₹ {total_expenses}')
st.markdown(f'**🏦 Loan Payments:** ₹ {loan_total}')
st.markdown(f'**💰 Final Balance:** ₹ {balance}')

if balance > 0:
    st.success("You're in surplus this month 🎉")
else:
    st.error("You're in deficit. Try reducing some expenses. 😓")

st.caption('Made with ❤️ using Streamlit — MyKhata')
