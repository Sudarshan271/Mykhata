import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import hashlib # For password hashing
import altair as alt # For charts

# --- App Config ---
st.set_page_config(page_title="MyKhata Modern", layout="wide")

# --- Custom CSS for Mobile Optimization and Styling ---
st.markdown("""
    <style>
    /* Hide Streamlit branding and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* General body styling for mobile */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #f0f2f6;
        margin: 0;
        padding: 0;
    }

    /* Streamlit specific elements adjustments */
    .stApp {
        padding-bottom: 80px; /* Space for bottom nav */
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Custom Card Styling */
    .stCard {
        background-color: #e3f2fd; /* Light blue */
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 15px;
        border: none;
    }
    .stCard > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .stCard h3 {
        color: #1976D2; /* Darker blue for headings */
        margin-bottom: 5px;
    }
    .stCard p {
        font-size: 1.5em;
        font-weight: bold;
        color: #424242;
    }

    /* Bottom Navigation Bar Styling */
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: #e3f2fd; /* Light blue */
        padding: 8px 0;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        color: #555;
        font-size: 0.8em;
        font-weight: 600;
        transition: color 0.3s ease;
        padding: 5px; /* Add padding for better touch target */
    }
    .nav-item:hover {
        color: #2196F3;
    }
    .nav-item .icon {
        font-size: 24px;
        margin-bottom: 3px;
    }
    .plus-btn {
        font-size: 32px; /* Larger plus icon */
        color: white;
        background: #2196F3; /* Bright blue for add button */
        border-radius: 50%;
        width: 60px; /* Larger circle */
        height: 60px;
        line-height: 60px;
        text-align: center;
        margin-top: -30px; /* Pull up to float */
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: background 0.3s ease;
    }
    .plus-btn:hover {
        background: #1976D2;
    }

    /* Hide hamburger menu (sidebar toggle) */
    .css-1lcbmhc {
        visibility: hidden;
    }

    /* Adjust Streamlit columns for mobile responsiveness */
    div[data-testid="stVerticalBlock"] > div {
        gap: 1rem; /* Adjust vertical spacing */
    }
    div[data-testid="stHorizontalBlock"] > div {
        gap: 1rem; /* Adjust horizontal spacing */
    }

    /* Chart specific styling */
    .stPlotlyChart {
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 10px;
        background-color: white;
    }

    /* Form input styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }
    .stButton>button {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }

    /* Message box styling */
    .st-emotion-cache-1c7y2kd { /* This class might change, but targets success/error messages */
        border-radius: 8px;
    }

    /* Profile Page image upload */
    .stFileUploader {
        border: 2px dashed #2196F3;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #e3f2fd;
    }
    </style>
""", unsafe_allow_html=True)


# --- Session State Setup ---
for key in ["logged_in", "username", "user_role", "parent_username", "show_signup", "account_created", "active_page", "current_user_data", "transaction_df", "category_df"]:
    if key not in st.session_state:
        if key == "logged_in": st.session_state[key] = False
        elif key == "show_signup": st.session_state[key] = False
        elif key == "account_created": st.session_state[key] = False
        elif key == "active_page": st.session_state[key] = "Home"
        elif key == "user_role": st.session_state[key] = "Main" # Default role
        else: st.session_state[key] = None

# --- File Paths ---
DATA_FILE = "mykhata_data.csv"
USERS_FILE = "users_public_details.csv"
CATEGORY_FILE = "category_memory.csv"

# --- Utility Functions ---

def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Loads user data from CSV or creates an empty DataFrame."""
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # Added 'ParentUsername' column for sub-users
        df = pd.DataFrame(columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    """Saves user data to CSV."""
    df.to_csv(USERS_FILE, index=False)

def load_transactions(effective_username):
    """Loads transaction data for a specific effective_username or creates an empty DataFrame."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Ensure 'Username' column exists and filter by effective_username
        if 'Username' not in df.columns:
            df['Username'] = '' # Add it if missing
        return df[df['Username'] == effective_username].copy()
    else:
        df = pd.DataFrame(columns=["Username", "Date", "Type", "Category", "Amount", "Note"])
        df.to_csv(DATA_FILE, index=False)
        return df[df['Username'] == effective_username].copy()

def save_transaction(effective_username, date, trans_type, category, amount, note):
    """Saves a single transaction to the main data file."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Username", "Date", "Type", "Category", "Amount", "Note"])
        df.to_csv(DATA_FILE, index=False)

    df = pd.read_csv(DATA_FILE)
    new_transaction = pd.DataFrame([{
        "Username": effective_username,
        "Date": date.strftime('%Y-%m-%d'),
        "Type": trans_type,
        "Category": category,
        "Amount": amount,
        "Note": note
    }])
    df = pd.concat([df, new_transaction], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.session_state.transaction_df = load_transactions(effective_username) # Refresh session state data

def load_categories(username):
    """Loads custom categories for a user or creates an empty DataFrame."""
    if os.path.exists(CATEGORY_FILE):
        df = pd.read_csv(CATEGORY_FILE)
        # Filter categories specific to the user or global (if any)
        return df[df['Username'] == username].copy()
    else:
        df = pd.DataFrame(columns=["Username", "CategoryType", "CategoryName"])
        df.to_csv(CATEGORY_FILE, index=False)
        return df[df['Username'] == username].copy()

def save_category(username, category_type, category_name):
    """Saves a custom category for a user."""
    if not os.path.exists(CATEGORY_FILE):
        df = pd.DataFrame(columns=["Username", "CategoryType", "CategoryName"])
        df.to_csv(CATEGORY_FILE, index=False)

    df = pd.read_csv(CATEGORY_FILE)
    if not ((df['Username'] == username) & (df['CategoryName'] == category_name)).any():
        new_category = pd.DataFrame([{
            "Username": username,
            "CategoryType": category_type,
            "CategoryName": category_name
        }])
        df = pd.concat([df, new_category], ignore_index=True)
        df.to_csv(CATEGORY_FILE, index=False)
        st.session_state.category_df = load_categories(username) # Refresh session state data

# --- Authentication Pages ---

def login_page():
    st.markdown("<h2 style='text-align: center; color: #1976D2;'>🎉 Welcome to MyKhata – Manage your money smartly.</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            create_account_button = st.form_submit_button("Create a new account")

    if login_button:
        users = load_users()
        hashed_password = hash_password(password)
        match = users[(users["Username"] == username) & (users["PasswordHash"] == hashed_password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = match.iloc[0]["Role"]
            st.session_state.parent_username = match.iloc[0]["ParentUsername"] if pd.notna(match.iloc[0]["ParentUsername"]) else None
            
            # Determine the effective username for data storage
            st.session_state.effective_username = st.session_state.parent_username if st.session_state.user_role == "Sub" else st.session_state.username
            
            st.session_state.transaction_df = load_transactions(st.session_state.effective_username)
            st.session_state.category_df = load_categories(st.session_state.username) # Categories are per actual user
            st.success("✅ Login Successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

    if create_account_button:
        st.session_state.show_signup = True
        st.experimental_rerun()

def signup_page():
    st.markdown("<h2 style='text-align: center; color: #1976D2;'>📝 Create New Account</h2>", unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Your Name")
        username = st.text_input("Username (Starts with uppercase, alphanumeric)")
        password = st.text_input("Password (Starts with uppercase, alphanumeric, includes a symbol)", type="password")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address")
        
        col1, col2 = st.columns(2)
        with col1:
            create_account_button = st.form_submit_button("Create Account")
        with col2:
            back_to_login_button = st.form_submit_button("Back to Login")

    if create_account_button:
        # Username validation
        if not re.match(r"^[A-Z][A-Za-z0-9]+$", username):
            st.error("Username must start with an uppercase letter and contain only alphanumeric characters.")
            return
        # Password validation
        if not re.match(r"^[A-Z](?=.*[!@#$%^&*()_+={}\[\]:;<>,.?/~`-])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;<>,.?/~`-]*$", password):
            st.error("Password must start with an uppercase letter and include at least one special character.")
            return

        users = load_users()
        if username in users["Username"].values:
            st.error("Username already exists. Please choose a different one.")
        else:
            hashed_password = hash_password(password)
            new_user = pd.DataFrame([[username, hashed_password, name, mobile, email, "Main", None]],
                                    columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("Account created successfully! Please log in.")
            st.session_state.show_signup = False
            st.session_state.account_created = True # Indicate successful creation for login page
            st.experimental_rerun()
    
    if back_to_login_button:
        st.session_state.show_signup = False
        st.experimental_rerun()

# --- Navigation Bar ---
def bottom_navbar():
    # JavaScript to update query params without full page reload
    js = """
    <script>
        function navigate(page) {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('nav', page);
            window.location.search = urlParams.toString();
        }
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="bottom-bar">
        <div onclick="navigate('Home')" class="nav-item">
            <span class="icon">🏠</span> Home
        </div>
        <div onclick="navigate('Wallet')" class="nav-item">
            <span class="icon">💰</span> Wallet
        </div>
        <div onclick="navigate('Add')" class="plus-btn">
            +
        </div>
        <div onclick="navigate('Report')" class="nav-item">
            <span class="icon">📊</span> Report
        </div>
        <div onclick="navigate('Profile')" class="nav-item">
            <span class="icon">⚙️</span> Profile
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Pages ---

def dashboard():
    st.markdown(f"<h2 style='color: #1976D2;'>👋 Hello, {st.session_state.username}</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df
    
    if user_transactions.empty:
        st.info("No transactions recorded yet. Add some to see your financial summary!")
        total_balance = 0
        total_income = 0
        total_expense = 0
        net_loans = 0
    else:
        # Ensure 'Amount' column is numeric
        user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

        total_income = user_transactions[user_transactions['Type'] == 'Income']['Amount'].sum()
        total_expense = user_transactions[user_transactions['Type'] == 'Expense']['Amount'].sum()
        total_loans_taken = user_transactions[user_transactions['Type'] == 'Loan']['Amount'].sum()
        total_emi_paid = user_transactions[user_transactions['Type'] == 'EMI']['Amount'].sum()
        
        total_balance = total_income - total_expense - total_emi_paid + total_loans_taken
        net_loans = total_loans_taken - total_emi_paid

    # Display summary cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Balance</h3>
            <p>₹ {total_balance:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Income</h3>
            <p>₹ {total_income:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Expense</h3>
            <p>₹ {total_expense:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stCard">
            <h3>Net Loans</h3>
            <p>₹ {net_loans:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Financial Trends")

    if not user_transactions.empty:
        user_transactions['Date'] = pd.to_datetime(user_transactions['Date'])
        
        # Calculate net flow for charting
        chart_data = user_transactions.copy()
        chart_data['Flow'] = chart_data.apply(lambda row: row['Amount'] if row['Type'] in ['Income', 'Loan'] else -row['Amount'], axis=1)

        time_filter = st.selectbox("Filter by:", ["Daily", "Monthly", "Yearly"], key="dashboard_filter")

        if time_filter == "Daily":
            grouped_data = chart_data.groupby(chart_data['Date'].dt.date)['Flow'].sum().reset_index()
            grouped_data['Date'] = pd.to_datetime(grouped_data['Date'])
            x_axis_format = '%Y-%m-%d'
            x_axis_title = 'Date'
        elif time_filter == "Monthly":
            grouped_data = chart_data.groupby(chart_data['Date'].dt.to_period('M'))['Flow'].sum().reset_index()
            grouped_data['Date'] = grouped_data['Date'].dt.to_timestamp()
            x_axis_format = '%Y-%m'
            x_axis_title = 'Month'
        else: # Yearly
            grouped_data = chart_data.groupby(chart_data['Date'].dt.to_period('Y'))['Flow'].sum().reset_index()
            grouped_data['Date'] = grouped_data['Date'].dt.to_timestamp()
            x_axis_format = '%Y'
            x_axis_title = 'Year'

        chart = alt.Chart(grouped_data).mark_bar().encode(
            x=alt.X('Date', axis=alt.Axis(format=x_axis_format, title=x_axis_title)),
            y=alt.Y('Flow', title='Net Flow (Income/Loan - Expense/EMI)'),
            color=alt.condition(
                alt.datum.Flow > 0,
                alt.value('#4CAF50'),  # Green for positive flow
                alt.value('#F44336')   # Red for negative flow
            ),
            tooltip=[alt.Tooltip('Date', format=x_axis_format), 'Flow']
        ).properties(
            title=f'Net Financial Flow ({time_filter})'
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Add transactions to see financial trends.")

    st.markdown("---")
    st.subheader("All Transactions")
    if not user_transactions.empty:
        # Sort by date descending for latest transactions first
        st.dataframe(user_transactions.sort_values(by='Date', ascending=False).drop(columns=['Username']), use_container_width=True)
    else:
        st.info("No transactions to display.")


def add_transaction():
    st.markdown("<h2 style='color: #1976D2;'>➕ Add Transaction</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    current_username = st.session_state.username # For category management

    # Load categories for the current user
    user_categories_df = st.session_state.category_df
    
    # Default categories
    default_income_categories = ["Salary", "Freelance", "Investment", "Gift", "Other Income"]
    default_expense_categories = ["Food", "Transport", "Rent", "Utilities", "Shopping", "Entertainment", "Health", "Education", "Other Expense"]
    default_loan_categories = ["Personal Loan", "Home Loan", "Car Loan", "Student Loan", "Other Loan"]
    default_emi_categories = ["Loan Repayment", "Credit Card Bill", "Other EMI"]

    # Combine default and user-defined categories
    all_income_categories = sorted(list(set(default_income_categories + user_categories_df[user_categories_df['CategoryType'] == 'Income']['CategoryName'].tolist())))
    all_expense_categories = sorted(list(set(default_expense_categories + user_categories_df[user_categories_df['CategoryType'] == 'Expense']['CategoryName'].tolist())))
    all_loan_categories = sorted(list(set(default_loan_categories + user_categories_df[user_categories_df['CategoryType'] == 'Loan']['CategoryName'].tolist())))
    all_emi_categories = sorted(list(set(default_emi_categories + user_categories_df[user_categories_df['CategoryType'] == 'EMI']['CategoryName'].tolist())))

    with st.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now().date())
        trans_type = st.selectbox("Type", ["Expense", "Income", "Loan", "EMI"], key="trans_type")

        category_options = []
        if trans_type == "Income":
            category_options = all_income_categories
        elif trans_type == "Expense":
            category_options = all_expense_categories
        elif trans_type == "Loan":
            category_options = all_loan_categories
        elif trans_type == "EMI":
            category_options = all_emi_categories
        
        # Add a "Add New Category" option
        category_options.append("➕ Add New Category...")
        
        category = st.selectbox("Category", category_options, key="category_select")

        new_category_name = ""
        if category == "➕ Add New Category...":
            new_category_name = st.text_input("Enter New Category Name", key="new_category_input")
            if new_category_name:
                # Save new category to memory
                save_category(current_username, trans_type, new_category_name)
                category = new_category_name # Use the new category for the current transaction
                st.success(f"Category '{new_category_name}' added!")
                # Re-run to update category dropdown with new option
                st.experimental_rerun()
            else:
                st.warning("Please enter a name for the new category.")
                st.stop() # Stop execution if new category is selected but not named

        amount = st.number_input("Amount", min_value=0.01, format="%.2f")
        note = st.text_area("Note (Optional)", max_chars=200)

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if not category or category == "➕ Add New Category...":
                st.error("Please select or add a category.")
            elif amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                save_transaction(effective_username, date, trans_type, category, amount, note)
                st.success("✅ Transaction saved successfully!")
                # No explicit rerun here, form clear_on_submit handles it

def wallet():
    st.markdown("<h2 style='color: #1976D2;'>💼 Wallet Overview</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df

    if user_transactions.empty:
        st.info("No transactions recorded yet to display wallet overview.")
        total_balance = 0
        total_income = 0
        total_expense = 0
        net_loans = 0
    else:
        user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

        total_income = user_transactions[user_transactions['Type'] == 'Income']['Amount'].sum()
        total_expense = user_transactions[user_transactions['Type'] == 'Expense']['Amount'].sum()
        total_loans_taken = user_transactions[user_transactions['Type'] == 'Loan']['Amount'].sum()
        total_emi_paid = user_transactions[user_transactions['Type'] == 'EMI']['Amount'].sum()
        
        total_balance = total_income - total_expense - total_emi_paid + total_loans_taken
        net_loans = total_loans_taken - total_emi_paid

    # Display summary cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard">
            <h3>Current Balance</h3>
            <p>₹ {total_balance:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Income</h3>
            <p>₹ {total_income:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="stCard">
            <h3>Total Expense</h3>
            <p>₹ {total_expense:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stCard">
            <h3>Net Loans</h3>
            <p>₹ {net_loans:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Expense Breakdown by Category")

    if not user_transactions.empty and not user_transactions[user_transactions['Type'] == 'Expense'].empty:
        expense_by_category = user_transactions[user_transactions['Type'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index()
        
        chart = alt.Chart(expense_by_category).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Amount", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", title="Category"),
            order=alt.Order("Amount", sort="descending"),
            tooltip=["Category", alt.Tooltip("Amount", format=",.2f")]
        ).properties(
            title="Expense Distribution"
        ).interactive()
        
        text = alt.Chart(expense_by_category).mark_text(radius=140).encode(
            theta=alt.Theta(field="Amount", type="quantitative"),
            text=alt.Text("Amount", format=",.2f"),
            order=alt.Order("Amount", sort="descending"),
            color=alt.value("black") # Set the color of the labels to black
        )
        
        st.altair_chart(chart + text, use_container_width=True)
    else:
        st.info("No expense transactions to display a breakdown.")


def report():
    st.markdown("<h2 style='color: #1976D2;'>📊 Reports</h2>", unsafe_allow_html=True)

    effective_username = st.session_state.effective_username
    user_transactions = st.session_state.transaction_df

    if user_transactions.empty:
        st.info("No transactions to generate reports.")
        return

    user_transactions['Date'] = pd.to_datetime(user_transactions['Date'])
    user_transactions['Amount'] = pd.to_numeric(user_transactions['Amount'], errors='coerce').fillna(0)

    report_type = st.selectbox("Select Report Type:", ["Income vs. Expense", "Category Spending", "Loan/EMI Trends"], key="report_type_select")
    time_filter = st.selectbox("Filter by:", ["Daily", "Monthly", "Yearly"], key="report_time_filter")

    # Determine grouping period
    if time_filter == "Daily":
        period_format = '%Y-%m-%d'
        period_title = 'Date'
        group_by_period = user_transactions['Date'].dt.date
    elif time_filter == "Monthly":
        period_format = '%Y-%m'
        period_title = 'Month'
        group_by_period = user_transactions['Date'].dt.to_period('M')
    else: # Yearly
        period_format = '%Y'
        period_title = 'Year'
        group_by_period = user_transactions['Date'].dt.to_period('Y')

    if report_type == "Income vs. Expense":
        st.subheader("Income vs. Expense Over Time")
        income_data = user_transactions[user_transactions['Type'] == 'Income'].groupby(group_by_period)['Amount'].sum().reset_index()
        expense_data = user_transactions[user_transactions['Type'] == 'Expense'].groupby(group_by_period)['Amount'].sum().reset_index()

        income_data['Type'] = 'Income'
        expense_data['Type'] = 'Expense'

        # Rename the period column for Altair
        income_data.rename(columns={income_data.columns[0]: 'Period'}, inplace=True)
        expense_data.rename(columns={expense_data.columns[0]: 'Period'}, inplace=True)

        combined_data = pd.concat([income_data, expense_data])
        
        if not combined_data.empty:
            # Convert Period to timestamp for Altair
            combined_data['Period'] = combined_data['Period'].astype(str).apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(combined_data).mark_line(point=True).encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Amount (₹)'),
                color=alt.Color('Type', legend=alt.Legend(title="Transaction Type")),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Type', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Income vs. Expense ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No income or expense data for this period.")

    elif report_type == "Category Spending":
        st.subheader("Spending by Category Over Time")
        expense_data = user_transactions[user_transactions['Type'] == 'Expense'].copy()
        
        if not expense_data.empty:
            expense_data['Period'] = group_by_period.astype(str) # Convert to string for grouping
            
            # Group by Period and Category
            grouped_expense = expense_data.groupby(['Period', 'Category'])['Amount'].sum().reset_index()
            
            # Convert Period back to datetime for Altair
            grouped_expense['Period'] = grouped_expense['Period'].apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(grouped_expense).mark_bar().encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Total Spending (₹)'),
                color=alt.Color('Category', title="Category"),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Category', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Spending by Category ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No expense data to display category spending.")

    elif report_type == "Loan/EMI Trends":
        st.subheader("Loan and EMI Trends Over Time")
        loan_data = user_transactions[user_transactions['Type'] == 'Loan'].groupby(group_by_period)['Amount'].sum().reset_index()
        emi_data = user_transactions[user_transactions['Type'] == 'EMI'].groupby(group_by_period)['Amount'].sum().reset_index()

        loan_data['Type'] = 'Loan Taken'
        emi_data['Type'] = 'EMI Paid'

        loan_data.rename(columns={loan_data.columns[0]: 'Period'}, inplace=True)
        emi_data.rename(columns={emi_data.columns[0]: 'Period'}, inplace=True)

        combined_data = pd.concat([loan_data, emi_data])

        if not combined_data.empty:
            combined_data['Period'] = combined_data['Period'].astype(str).apply(lambda x: datetime.strptime(x, period_format))

            chart = alt.Chart(combined_data).mark_line(point=True).encode(
                x=alt.X('Period', axis=alt.Axis(format=period_format, title=period_title)),
                y=alt.Y('Amount', title='Amount (₹)'),
                color=alt.Color('Type', legend=alt.Legend(title="Transaction Type")),
                tooltip=[alt.Tooltip('Period', format=period_format), 'Type', alt.Tooltip('Amount', format=",.2f")]
            ).properties(
                title=f'Loan and EMI Trends ({time_filter})'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No loan or EMI data for this period.")


def profile():
    st.markdown("<h2 style='color: #1976D2;'>👤 Profile Settings</h2>", unsafe_allow_html=True)

    users_df = load_users()
    current_user_row = users_df[users_df['Username'] == st.session_state.username].iloc[0]

    st.subheader("Your Profile Information")
    col_img, col_details = st.columns([1, 2])
    with col_img:
        # Placeholder for profile photo upload
        st.image("https://placehold.co/150x150/e0e0e0/ffffff?text=Profile", width=150, caption="Profile Photo")
        # st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"], key="profile_photo_uploader")
        st.markdown("<small><i>(Photo upload is for display only; persistence requires backend storage)</i></small>", unsafe_allow_html=True)
    
    with col_details:
        st.write(f"**Name:** {current_user_row['Name']}")
        st.write(f"**Username:** {current_user_row['Username']}")
        st.write(f"**Mobile:** {current_user_row['Mobile']}")
        st.write(f"**Email:** {current_user_row['Email']}")
        st.write(f"**Role:** {current_user_row['Role']}")
        if current_user_row['Role'] == "Sub" and pd.notna(current_user_row['ParentUsername']):
            st.write(f"**Linked to Main Account:** {current_user_row['ParentUsername']}")

    st.markdown("---")

    if st.session_state.user_role == "Main":
        st.subheader("Add New Sub-User")
        st.info("You are a 'Main' user. You can invite sub-users to access your account.")
        with st.form("add_sub_user_form", clear_on_submit=True):
            sub_user_name = st.text_input("Sub-User's Name")
            sub_user_username = st.text_input("Sub-User's Username (Starts with uppercase, alphanumeric)")
            sub_user_password = st.text_input("Sub-User's Password (Starts with uppercase, alphanumeric, includes a symbol)", type="password")
            sub_user_mobile = st.text_input("Sub-User's Mobile Number")
            sub_user_email = st.text_input("Sub-User's Email Address")

            add_sub_user_button = st.form_submit_button("Create Sub-User Account")

            if add_sub_user_button:
                # Sub-user username validation
                if not re.match(r"^[A-Z][A-Za-z0-9]+$", sub_user_username):
                    st.error("Sub-User Username must start with an uppercase letter and contain only alphanumeric characters.")
                    return
                # Sub-user password validation
                if not re.match(r"^[A-Z](?=.*[!@#$%^&*()_+={}\[\]:;<>,.?/~`-])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;<>,.?/~`-]*$", sub_user_password):
                    st.error("Sub-User Password must start with an uppercase letter and include at least one special character.")
                    return

                if sub_user_username in users_df["Username"].values:
                    st.error("Sub-User Username already exists. Please choose a different one.")
                else:
                    hashed_sub_password = hash_password(sub_user_password)
                    new_sub_user = pd.DataFrame([[sub_user_username, hashed_sub_password, sub_user_name, sub_user_mobile, sub_user_email, "Sub", st.session_state.username]],
                                                columns=["Username", "PasswordHash", "Name", "Mobile", "Email", "Role", "ParentUsername"])
                    users_df = pd.concat([users_df, new_sub_user], ignore_index=True)
                    save_users(users_df)
                    st.success(f"Sub-user '{sub_user_username}' created successfully and linked to your account!")
                    st.experimental_rerun()
    else:
        st.info(f"You are a 'Sub' user linked to '{st.session_state.parent_username}' account. Only the main user can add new sub-users.")

    st.markdown("---")
    st.subheader("Payment Reminders (Upcoming)")
    st.info("This section will display upcoming loan or EMI due dates.")
    st.markdown("<small><i>(Feature placeholder)</i></small>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.session_state.parent_username = None
        st.session_state.effective_username = ""
        st.session_state.transaction_df = pd.DataFrame() # Clear dataframes
        st.session_state.category_df = pd.DataFrame()
        st.success("You have been logged out.")
        st.experimental_rerun()

# --- Main App Logic ---
def main_app():
    # Get navigation parameter from URL query string
    nav = st.query_params.get("nav", "Home") # Default to Home if not present
    st.session_state.active_page = nav

    # Ensure data is loaded when app starts or after login
    if st.session_state.logged_in and (st.session_state.transaction_df is None or st.session_state.category_df is None or st.session_state.transaction_df.empty):
        st.session_state.effective_username = st.session_state.parent_username if st.session_state.user_role == "Sub" else st.session_state.username
        st.session_state.transaction_df = load_transactions(st.session_state.effective_username)
        st.session_state.category_df = load_categories(st.session_state.username)


    if st.session_state.active_page == "Home":
        dashboard()
    elif st.session_state.active_page == "Add":
        add_transaction()
    elif st.session_state.active_page == "Wallet":
        wallet()
    elif st.session_state.active_page == "Report":
        report()
    elif st.session_state.active_page == "Profile":
        profile()
    
    bottom_navbar()

# --- Launch App ---
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main_app()
