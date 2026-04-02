import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
from supabase import create_client
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from supabase import create_client
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def generate_pdf(df, username):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"{username}'s Expense Report", styles["Title"])
    elements.append(title)

    if not df.empty:
        data = [df.columns.tolist()] + df.values.tolist()

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),1,colors.black),
        ]))

        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
# ---------------------------------------------------------
# 🌈 PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide"
)

# ---------------------------------------------------------
# 🎨 BACKGROUND + FONT
# ---------------------------------------------------------
background_url = "https://images.pexels.com/photos/5466785/pexels-photo-5466785.jpeg"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --primary-color: #6366f1;
    --primary-hover: #4f46e5;
    --bg-card: rgba(255, 255, 255, 0.85);
    --text-main: #1f2937;
    --text-muted: #6b7280;
    --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: var(--text-main);
}}

[data-testid="stAppViewContainer"] {{
    background-image: url('{background_url}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    position: relative;
    overflow: hidden;
}}

[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.7),
        rgba(255, 255, 255, 0.4)
    );
    z-index: 0;
    pointer-events: none;
}}

[data-testid="stAppViewContainer"] > * {{
    position: relative;
    z-index: 1;
}}

/* Glassmorphism Card */
.card {{
    padding: 24px;
    border-radius: 20px;
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: var(--glass-shadow);
    margin-bottom: 24px;
    transition: transform 0.2s ease;
}}

.big-title {{
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg, #4f46e5, #9333ea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}}

/* Modern Header Bar */
.header-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}}

.avatar {{
    width: 45px;
    height: 45px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-weight: 700;
    font-size: 18px;
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
}}

/* Login/Signup Cards */
.login-card {{
    max-width: 480px;
    margin: 60px auto;
    padding: 40px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255,255,255,0.5);
}}

.login-title {{
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    color: #111827;
    margin-bottom: 12px;
}}

.login-sub {{
    text-align: center;
    color: var(--text-muted);
    margin-bottom: 30px;
    font-size: 16px;
}}

/* Metric styling */
.metric-card {{
    text-align: center;
}}
.metric-label {{
    font-size: 14px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}}
.metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: var(--text-main);
}}

/* Hide Streamlit components */
#MainMenu {{ display: none !important; }}
header {{ display: none !important; }}
footer {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stHeader"] {{ display: none !important; }}

/* Remove top padding */
[data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
}}
.main .block-container {{
    padding-top: 1rem !important;
}}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# ☁️ SUPABASE HANDLING (REPLACED CSV)
# ---------------------------------------------------------
def load_data(username):
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    df = pd.DataFrame(res.data)
    if df.empty:
        return pd.DataFrame(columns=["date","category","amount","payment_mode","month","username"])
    return df

def save_data(username, df):
    supabase.table("expenses").delete().eq("username", username).execute()
    if not df.empty:
        supabase.table("expenses").insert(df.to_dict(orient="records")).execute()

def save_profile(username, dob):
    supabase.table("users").upsert({
        "username": username,
        "dob": dob
    }).execute()

def load_profile(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    if res.data:
        return pd.DataFrame(res.data)
    return None

# ---------------------------------------------------------
# 🎯 AGE BASED BUDGET FUNCTION
# ---------------------------------------------------------
def calculate_age(dob):

    dob=datetime.datetime.strptime(dob,"%d-%m-%Y").date()
    today=datetime.date.today()

    age=today.year-dob.year-((today.month,today.day)<(dob.month,dob.day))

    return age

def recommended_budget(age):

    if age < 18:
        return 2000
    elif 18 <= age <= 25:
        return 5000
    elif 26 <= age <= 35:
        return 10000
    elif 36 <= age <= 50:
        return 15000
    else:
        return 12000

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
DEFAULT_CATEGORIES=["Food","Transport","Groceries","Entertainment","Shopping","Bills","Other"]
PAYMENT_MODES=["CASH","UPI","CARD","NET BANKING"]

# ---------------------------------------------------------
# SESSION STATES
# ---------------------------------------------------------
if "username" not in st.session_state:
    st.session_state.username=None

if "signup" not in st.session_state:
    st.session_state.signup=False

if "page" not in st.session_state:
    st.session_state.page="dashboard"

# ---------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------
if not st.session_state.username and not st.session_state.signup:

    left, center, right = st.columns([1, 2, 1])

    with center:
      
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>Welcome To Cashlytics 💸</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Sign in to manage your finances with ease</div>", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="e.g. kashish_26")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True, type="primary"):

            # 🔥 SUPABASE CHECK
            res = supabase.table("users").select("*").eq("username", username).execute()

            if res.data:
                st.session_state.username = username
                st.rerun()
            else:
                st.error("User does not exist")

        st.markdown("<div style='text-align:center; margin: 15px 0; color: #9ca3af;'>OR</div>", unsafe_allow_html=True)
        
        if st.button("Create New Account", use_container_width=True):
            st.session_state.signup = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# SIGNUP PAGE
# ---------------------------------------------------------
if st.session_state.signup and not st.session_state.username:

    st.markdown("<h1 class='big-title'>Create Account ✨</h1>",unsafe_allow_html=True)

    st.markdown("<div class='card'>",unsafe_allow_html=True)

    new_user=st.text_input("Choose Username")
    dob=st.text_input("Enter DOB (DD-MM-YYYY)")

    if st.button("Sign Up"):

        # 🔥 SUPABASE CHECK
        res = supabase.table("users").select("*").eq("username", new_user).execute()

        if res.data:
            st.error("Username already exists!")

        else:
            try:
                datetime.datetime.strptime(dob,"%d-%m-%Y")

                # 🔥 SAVE USER
                save_profile(new_user, dob)

                st.success("Account created! Please login")
                st.session_state.signup=False

            except:
                st.error("Invalid DOB format")

    if st.button("Back to Login"):

        st.session_state.signup=False
        st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

    st.stop()

## ---------------------------------------------------------
# DASHBOARD HEADER (Modern Header Bar)
# ---------------------------------------------------------
if st.session_state.username:
    st.markdown(f"""
        <div class="header-container">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="avatar">{st.session_state.username[0].upper()}</div>
                <div style="font-size: 24px; font-weight: 700;">Hello, {st.session_state.username} 👋</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Logout button and data loading
    col_logout, _ = st.columns([1, 5])
    with col_logout:
        if st.button("Logout", use_container_width=True):
            st.session_state.username = None
            st.session_state.page = "dashboard"
            st.rerun()

    # 🔥 FETCH EXPENSE DATA FROM SUPABASE
    res_exp = supabase.table("expenses").select("*").eq("username", st.session_state.username).execute()
    df = pd.DataFrame(res_exp.data)

    if df.empty:
        df = pd.DataFrame(columns=["date","category","amount","payment_mode","month"])

    # 🔥 FETCH USER PROFILE FROM SUPABASE
    res_user = supabase.table("users").select("*").eq("username", st.session_state.username).execute()

    if res_user.data:
        profile = pd.DataFrame(res_user.data)
    else:
        profile = None

    # ---------------------------------------------------------
    # AGE BASED BUDGET
    # ---------------------------------------------------------
    if profile is not None:
        dob = profile["dob"][0]
        age = calculate_age(dob)
        budget = recommended_budget(age)
        spent = df["amount"].sum()
        remaining = budget - spent

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>🎯 Monthly Budget Strategy</h3>", unsafe_allow_html=True)
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.write(f"Age: **{age} years**")
            st.write(f"Recommended Budget: **₹{budget}**")
        with b_col2:
            st.write(f"Total Spent: **₹{spent}**")
            st.write(f"Remaining: **₹{remaining}**")

        if spent >= 0.85 * budget and spent < budget:
            st.warning("⚠️ **Warning:** You've used 85% of your monthly budget.")

        if remaining > 0:
            st.success("🎉 **Great job!** You're within your budget.")
        elif remaining == 0:
            st.warning("ℹ️ **Limit Reached:** You've reached your budget limit.")
        else:
            st.error("🚨 **Budget Exceeded:** You've spent more than your recommended budget.")

        st.markdown("</div>", unsafe_allow_html=True)
    # ---------------------------------------------------------
# ADD EXPENSE BUTTON
# ---------------------------------------------------------
if st.button("➕ Add Expense", use_container_width=True):
    st.session_state.page = "add_expense"
    st.rerun()

# ---------------------------------------------------------
# ADD EXPENSE PAGE
# ---------------------------------------------------------
if st.session_state.page == "add_expense":
    st.markdown("<div class='header-container'><div style='font-size: 24px; font-weight: 700;'>➕ Add New Expense</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    col_date, col_cat = st.columns(2)
    with col_date:
        date = st.date_input("Transaction Date")
    with col_cat:
        categories = sorted(set(df["category"].unique()).union(DEFAULT_CATEGORIES))
        category = st.selectbox("Category", categories + ["Add New..."])
        if category == "Add New...":
            category = st.text_input("Custom Category Name")

    col_amt, col_pay = st.columns(2)
    with col_amt:
        amount = st.number_input("Amount (₹)", min_value=1, step=10)
    with col_pay:
        payment = st.selectbox("Payment Mode", PAYMENT_MODES)

    st.markdown("<br>", unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    with b1:
if st.button("Save Transaction", use_container_width=True, type="primary"):

    # 🔥 SAVE TO SUPABASE
    try:
        # ✅ Validate inputs
        if not st.session_state.get("username"):
            st.error("User not logged in")

        elif not amount:
            st.error("Please enter amount")

        else:
            response = supabase.table("expenses").insert({
                "username": str(st.session_state.username),
                "date": date.strftime("%Y-%m-%d"),   # ✅ FIXED FORMAT
                "category": str(category),
                "amount": float(amount),             # ✅ ensure numeric
                "payment_mode": str(payment),
                "month": date.strftime("%B")
            }).execute()

            st.success("✅ Success! Expense recorded.")
            print(response)

    except Exception as e:
        import traceback
        st.error(f"❌ Error: {e}")
        st.text(traceback.format_exc())

            # 🔥 REFRESH PAGE
            st.rerun()
    
    with b2:
        if st.button("Cancel & Return", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

 # ---------------------------------------------------------
# SUMMARY CARDS
# ---------------------------------------------------------

# 🔥 SAFETY: ensure numeric
if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

col1, col2, col3 = st.columns(3)

with col1:
    total_expense = df["amount"].sum() if not df.empty else 0
    st.markdown(f"""
        <div class="card metric-card">
            <div class="metric-label">💰 Total Expense</div>
            <div class="metric-value">₹ {total_expense:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    current_month = datetime.date.today().strftime("%B")
    month_total = df[df["month"] == current_month]["amount"].sum() if not df.empty else 0

    st.markdown(f"""
        <div class="card metric-card">
            <div class="metric-label">📅 This Month</div>
            <div class="metric-value">₹ {month_total:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if not df.empty and "category" in df.columns:
        top = df.groupby("category")["amount"].sum().idxmax()
    else:
        top = "N/A"

    st.markdown(f"""
        <div class="card metric-card">
            <div class="metric-label">🔥 Top Category</div>
            <div class="metric-value">{top}</div>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
st.markdown("<br><h3 style='text-align: center;'>📊 Visual Analytics</h3>", unsafe_allow_html=True)

if not df.empty:

    # 🔥 FIX MONTH ORDER
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

    c1, c2 = st.columns(2)
    color_scale = ["#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899"]

    with c1:
        fig_pie = px.pie(df, names="category", values="amount", hole=0.4, color_discrete_sequence=color_scale)
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bar = px.bar(df, x="month", y="amount", color_discrete_sequence=["#6366f1"])
        fig_bar.update_layout(margin=dict(t=20, b=0, l=0, r=0),
                              plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)


# ---------------------------------------------------------
# PAYMENT MODE ANALYTICS
# ---------------------------------------------------------
st.markdown("<h3 style='text-align: center;'>💳 Payment Mode Analysis</h3>", unsafe_allow_html=True)

if not df.empty:
    payment_chart = px.pie(df, names="payment_mode", values="amount", hole=0.4)
    payment_chart.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(payment_chart, use_container_width=True)


# ---------------------------------------------------------
# EXPENSE PREDICTION
# ---------------------------------------------------------
st.subheader("📈 Next Month Expense Prediction")

if not df.empty:
    monthly = df.groupby("month")["amount"].sum()

    if len(monthly) > 1:
        predicted = monthly.mean()
        st.info(f"Estimated Expense for Next Month : ₹ {predicted:,.0f}")
    else:
        st.write("Add more data to predict future expenses.")


# ---------------------------------------------------------
# TABLE
# ---------------------------------------------------------
st.subheader("📋 Expense Records")
st.dataframe(df, use_container_width=True)


# ---------------------------------------------------------
# DELETE (🔥 FIXED FOR SUPABASE)
# ---------------------------------------------------------
if not df.empty:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;'>🗑️ Delete an Expense</h4>", unsafe_allow_html=True)

    del_col1, del_col2 = st.columns([3, 1])

    with del_col1:
        delete_index = st.selectbox(
            "Select Record to Delete",
            options=df.index,
            format_func=lambda x: f"[{df.loc[x, 'date']}] {df.loc[x, 'category']} - ₹{df.loc[x, 'amount']} ({df.loc[x, 'payment_mode']})",
            label_visibility="collapsed"
        )

    with del_col2:
        if st.button("Delete Record", type="primary", use_container_width=True):

            row = df.loc[delete_index]

            # 🔥 DELETE FROM SUPABASE
            supabase.table("expenses") \
                .delete() \
                .eq("username", st.session_state.username) \
                .eq("date", row["date"]) \
                .eq("amount", row["amount"]) \
                .execute()

            st.success("Deleted successfully")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    # ---------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------
#st.download_button("📥 Download CSV", df.to_csv(index=False), "expenses.csv")

# 🔥 PDF DOWNLOAD
pdf_file = generate_pdf(df, st.session_state.username)

st.download_button(
    "📄 Download PDF",
    data=pdf_file,
    file_name="expense_report.pdf",
    mime="application/pdf"
)
