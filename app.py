import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px

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
background_url = "https://img.freepik.com/free-photo/close-up-education-economy-objects_23-2149113581.jpg?semt=ais_rp_50_assets&w=740&q=80"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif !important;
}}

[data-testid="stAppViewContainer"] {{
    background-image: url('{background_url}');
    background-size: cover;
    background-position: center;
}}

.card {{
    padding:20px;
    border-radius:15px;
    background:rgba(255,255,255,0.7);
    backdrop-filter:blur(7px);
    box-shadow:0px 4px 12px rgba(0,0,0,0.18);
}}

.big-title {{
    font-size:38px;
    font-weight:600;
}}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📁 FILE HANDLING
# ---------------------------------------------------------
def get_user_file(username):
    return f"data_{username}.csv"

def get_profile_file(username):
    return f"profile_{username}.csv"

def load_data(username):
    file = get_user_file(username)
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=["date","category","amount","payment_mode","month"])

def save_data(username,df):
    df.to_csv(get_user_file(username),index=False)

# ---------------------------------------------------------
# 👤 USER PROFILE
# ---------------------------------------------------------
def save_profile(username,dob):
    df=pd.DataFrame({"username":[username],"dob":[dob]})
    df.to_csv(get_profile_file(username),index=False)

def load_profile(username):
    file=get_profile_file(username)
    if os.path.exists(file):
        return pd.read_csv(file)
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

    st.markdown("<h1 class='big-title'>Welcome 🌈</h1>",unsafe_allow_html=True)

    st.markdown("<div class='card'>",unsafe_allow_html=True)

    username=st.text_input("Enter Username")

    if st.button("Login"):

        if os.path.exists(get_user_file(username)):

            st.session_state.username=username
            st.rerun()

        else:
            st.error("User does not exist")

    if st.button("Create Account"):

        st.session_state.signup=True
        st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

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

        if os.path.exists(get_user_file(new_user)):
            st.error("Username already exists!")

        else:
            try:

                datetime.datetime.strptime(dob,"%d-%m-%Y")

                df=load_data(new_user)

                save_data(new_user,df)

                save_profile(new_user,dob)

                st.success("Account created! Please login")

                st.session_state.signup=False

            except:
                st.error("Invalid DOB format")

    if st.button("Back to Login"):

        st.session_state.signup=False
        st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# DASHBOARD HEADER (Avatar + Logout)
# ---------------------------------------------------------
colA,colB,colC=st.columns([8,1,1])

with colA:
    st.markdown(f"<h1 class='big-title'>Hello, {st.session_state.username} 👋</h1>",unsafe_allow_html=True)

with colB:
    st.markdown(f"""
        <div style="
        background:white;
        padding:8px 16px;
        border-radius:50px;
        font-size:22px;
        font-weight:600;
        color:#7b2cbf;
        text-align:center;">
        {st.session_state.username[0].upper()}
        </div>
    """,unsafe_allow_html=True)

with colC:
    if st.button("Logout"):
        st.session_state.username=None
        st.session_state.page="dashboard"
        st.rerun()

df=load_data(st.session_state.username)
profile=load_profile(st.session_state.username)

# ---------------------------------------------------------
# AGE BASED BUDGET
# ---------------------------------------------------------
if profile is not None:

    dob=profile["dob"][0]
    age=calculate_age(dob)
    budget=recommended_budget(age)

    spent=df["amount"].sum()
    remaining=budget-spent

    st.markdown("<div class='card'>",unsafe_allow_html=True)

    st.subheader("🎯 Recommended Monthly Budget")

    st.write(f"Age : **{age} years**")
    st.write(f"Recommended Budget : **₹{budget}**")
    st.write(f"Total Spent : **₹{spent}**")
    st.write(f"Remaining : **₹{remaining}**")

    if spent >= 0.85 * budget and spent < budget:
        st.warning("⚠ Warning: You already used 85% of your monthly budget.")

    if remaining > 0:
        st.success("You are saving money 🎉")

    elif remaining == 0:
        st.warning("You reached your budget limit")

    else:
        st.error("You exceeded your budget")

    st.markdown("</div>",unsafe_allow_html=True)

# ---------------------------------------------------------
# ADD EXPENSE BUTTON
# ---------------------------------------------------------
if st.button("➕ Add Expense",use_container_width=True):

    st.session_state.page="add_expense"
    st.rerun()

# ---------------------------------------------------------
# ADD EXPENSE PAGE
# ---------------------------------------------------------
if st.session_state.page=="add_expense":

    st.markdown("<h2 class='big-title'>➕ Add Expense</h2>",unsafe_allow_html=True)

    st.markdown("<div class='card'>",unsafe_allow_html=True)

    date=st.date_input("Select Date")

    categories=sorted(set(df["category"].unique()).union(DEFAULT_CATEGORIES))

    category=st.selectbox("Category",categories+["Add New..."])

    if category=="Add New...":
        category=st.text_input("Enter New Category")

    amount=st.number_input("Amount",min_value=1)

    payment=st.selectbox("Payment Mode",PAYMENT_MODES)

    if st.button("Save Expense"):

        new_row=pd.DataFrame({

            "date":[date.strftime("%d-%m-%Y")],
            "category":[category],
            "amount":[amount],
            "payment_mode":[payment],
            "month":[date.strftime("%B")]

        })

        df=pd.concat([df,new_row],ignore_index=True)

        save_data(st.session_state.username,df)

        st.success("Expense Added!")

    if st.button("⬅ Back to Dashboard"):

        st.session_state.page="dashboard"
        st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# SUMMARY CARDS
# ---------------------------------------------------------
col1,col2,col3=st.columns(3)

with col1:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("💰 Total Expense")
    st.write(f"₹ {df['amount'].sum():,.0f}")
    st.markdown("</div>",unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("📅 This Month")
    month_total=df[df["month"]==datetime.date.today().strftime("%B")]["amount"].sum()
    st.write(f"₹ {month_total:,.0f}")
    st.markdown("</div>",unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("🔥 Top Category")
    if not df.empty:
        top=df.groupby("category")["amount"].sum().idxmax()
        st.write(top)
    st.markdown("</div>",unsafe_allow_html=True)

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
st.subheader("📊 Visual Analytics")

if not df.empty:

    c1,c2=st.columns(2)

    with c1:
        st.plotly_chart(px.pie(df,names="category",values="amount"),use_container_width=True)

    with c2:
        st.plotly_chart(px.bar(df,x="month",y="amount"),use_container_width=True)

# ---------------------------------------------------------
# PAYMENT MODE ANALYTICS
# ---------------------------------------------------------
st.subheader("💳 Payment Mode Analytics")

if not df.empty:

    payment_chart=px.pie(
        df,
        names="payment_mode",
        values="amount"
    )

    st.plotly_chart(payment_chart,use_container_width=True)

# ---------------------------------------------------------
# EXPENSE PREDICTION
# ---------------------------------------------------------
st.subheader("📈 Next Month Expense Prediction")

if not df.empty:

    monthly=df.groupby("month")["amount"].sum()

    if len(monthly)>1:

        predicted=monthly.mean()

        st.info(f"Estimated Expense for Next Month : ₹ {predicted:,.0f}")

    else:

        st.write("Add more data to predict future expenses.")

# ---------------------------------------------------------
# TABLE
# ---------------------------------------------------------
st.subheader("📋 Expense Records")

st.dataframe(df,use_container_width=True)

# ---------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------

st.download_button("📥 Download CSV",df.to_csv(index=False),"expenses.csv")


