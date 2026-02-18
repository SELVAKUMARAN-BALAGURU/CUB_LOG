import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- Page Config ----------------
st.set_page_config(page_title="Student Log System", layout="wide")

# ---------------- Custom CSS ----------------
st.markdown("""
<style>

/* =========================
   GLOBAL BACKGROUND
========================= */

.stApp {
    background-color: #f4f6f9;
}

/* Main container padding */
.block-container {
    padding-top: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
}

/* =========================
   HEADINGS & TEXT
========================= */

h1 {
    color: #0f172a !important;
    text-align: center;
    font-weight: 700;
    margin-bottom: 30px;
}

h2, h3 {
    color: #1e293b !important;
    font-weight: 600;
}

p, label, span, div {
    color: #1e293b;
}

/* =========================
   CARD STYLE
========================= */

.section-card {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}

/* =========================
   SIDEBAR
========================= */

[data-testid="stSidebar"] {
    background-color: #1e293b;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* =========================
   INPUT FIELDS
========================= */

input, textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    caret-color: #2563eb !important;  /* Blue blinking cursor */
}

/* Streamlit specific inputs */
.stTextInput input,
.stTextArea textarea,
.stDateInput input,
.stNumberInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 8px !important;
    caret-color: #2563eb !important;
}

/* Focus effect */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stDateInput input:focus,
.stNumberInput input:focus {
    border: 2px solid #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}

div[data-baseweb="select"] > div {
    background-color: #ffffff !important;  /* Dark background */
    color: #000000 !important;             /* White text */
}

/* Dropdown arrow */
svg {
    fill: #000000 !important;              /* White arrow */
}

/* =========================
   BUTTONS
========================= */

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}

.stButton button:hover {
    background-color: #1d4ed8;
}

/* =========================
   DATAFRAME
========================= */

[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
    padding: 10px;
}

/* =========================
   REMOVE DARK MODE OVERRIDES
========================= */

[data-testid="stToolbar"] {
    visibility: hidden;
}
            
/* =========================
   FINAL TIME DROPDOWN FIX
========================= */

/* Popover container */
div[data-baseweb="popover"] {
    background-color: #ffffff !important;
}

/* List container */
ul[role="listbox"] {
    background-color: #ffffff !important;
}

/* Each option container */
li[role="option"] {
    background-color: #ffffff !important;
}

/* FORCE text color inside option */
li[role="option"] * {
    color: #000000 !important;
    opacity: 1 !important;
}

/* Hover */
li[role="option"]:hover {
    background-color: #f1f5f9 !important;
}

/* Selected option */
li[aria-selected="true"] {
    background-color: #e2e8f0 !important;
}

li[aria-selected="true"] * {
    color: #000000 !important;
    opacity: 1 !important;
}



</style>
""", unsafe_allow_html=True)



# ---------------- File ----------------
EXCEL_FILE = "Log.xlsx"

# ---------------- Helper Functions ----------------
def load_students():
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet1")

def load_logs():
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet2")

def save_log(new_data):
    df_logs = load_logs()
    df_logs = pd.concat([df_logs, pd.DataFrame([new_data])], ignore_index=True)

    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df_logs.to_excel(writer, sheet_name="Sheet2", index=False)

def generate_pdf(data, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    style = getSampleStyleSheet()

    elements.append(Paragraph("Weekly Log Report", style["Title"]))
    elements.append(Spacer(1, 20))

    table_data = [list(data.columns)] + data.values.tolist()
    table = Table(table_data)
    table.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ])

    elements.append(table)
    doc.build(elements)

def load_professors():
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet3")

def save_professor(new_prof):
    df_prof = load_professors()
    df_prof = pd.concat([df_prof, pd.DataFrame([new_prof])], ignore_index=True)

    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df_prof.to_excel(writer, sheet_name="Sheet3", index=False)


if "prof_logged_in" not in st.session_state:
    st.session_state.prof_logged_in = False

if "prof_name" not in st.session_state:
    st.session_state.prof_name = ""
# ---------------- UI ----------------
st.title("📘 Student Log Management System")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go To", ["Student", "Professor"])

students_df = load_students()
logs_df = load_logs()

# ================= STUDENT PAGE =================
if page == "Student":

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📝 Student Log Entry")

    students_df["reg_no"] = students_df["reg_no"].astype(str)

    reg_no = st.text_input("Enter Register Number")

    if reg_no:
        student = students_df[students_df["reg_no"] == reg_no]

        if not student.empty:
            student = student.iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name:**", student["name"])
                st.write("**Problem Statement:**", student["problem_statement"])
                st.write("**Problem Number:**", student["problem_no"])

            with col2:
                st.write("**Faculty Guide:**", student["faculty_guide"])
                st.write("**Date:**", datetime.today().strftime("%d-%m-%Y"))

            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            description = st.text_area("Work Description")

            if st.button("Save Log"):
                new_log = {
                    "reg_no": student["reg_no"],
                    "name": student["name"],
                    "faculty": student["faculty_guide"],
                    "date": datetime.today().strftime("%d-%m-%Y"),
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": description
                }
                save_log(new_log)
                st.success("Log Saved Successfully!")

        else:
            st.error("Register Number Not Found")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= PROFESSOR PAGE =================
if page == "Professor":

    # If NOT logged in → show login/signup
    if not st.session_state.prof_logged_in:

        st.subheader("🔐 Professor Authentication")

        auth_option = st.radio("Select Option", ["Login", "Sign Up"])

        # ---------------- SIGN UP ----------------
        if auth_option == "Sign Up":
            st.markdown("### 📝 Professor Sign Up")

            faculty_id = st.text_input("Faculty ID")
            name = st.text_input("Name")
            password = st.text_input("Password", type="password")

            if st.button("Create Account"):

                df_prof = load_professors()

                if faculty_id in df_prof["faculty_id"].astype(str).values:
                    st.error("Faculty ID already exists!")
                else:
                    new_prof = {
                        "faculty_id": faculty_id,
                        "name": name,
                        "password": password
                    }
                    save_professor(new_prof)
                    st.success("Account created successfully! Please login.")

        # ---------------- LOGIN ----------------
        elif auth_option == "Login":
            st.markdown("### 🔑 Professor Login")

            faculty_id = st.text_input("Faculty ID")
            password = st.text_input("Password", type="password")

            if st.button("Login"):

                df_prof = load_professors()
                df_prof["faculty_id"] = df_prof["faculty_id"].astype(str)
                df_prof["password"]=df_prof["password"].astype(str)
                user = df_prof[
                    (df_prof["faculty_id"] == faculty_id) &
                    (df_prof["password"] == password)
                ]

                if not user.empty:
                    st.session_state.prof_logged_in = True
                    st.session_state.prof_name = user.iloc[0]["name"]
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Faculty ID or Password")

    # ================= AFTER LOGIN =================
    else:
        st.success(f"Welcome {st.session_state.prof_name} 👨‍🏫")

        if st.button("Logout"):
            st.session_state.prof_logged_in = False
            st.session_state.prof_name = ""
            st.rerun()

        prof_option = st.sidebar.radio(
            "Professor Options",
            ["View All Logs", "Search by Student ID", "Search by Faculty ID", "Generate Report"],
            key="prof_sidebar_options"
        )


        st.subheader("👨‍🏫 Professor Dashboard")

        # ---- VIEW ALL LOGS ----
        if prof_option == "View All Logs":
            display_df = logs_df.copy()
            display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%d-%m-%Y")
            st.dataframe(display_df, use_container_width=True)

        # ---- SEARCH BY STUDENT ----
        elif prof_option == "Search by Student ID":
            search_reg = st.text_input("Enter Register Number")

            if search_reg:
                filtered = logs_df[logs_df["reg_no"].astype(str) == search_reg]
                if not filtered.empty:
                    st.dataframe(filtered, use_container_width=True)
                else:
                    st.warning("No logs found.")

        # ---- SEARCH BY FACULTY ----
        elif prof_option == "Search by Faculty ID":
            faculty_id = st.text_input("Enter Faculty ID")

            if faculty_id:
                faculty_students = students_df[
                    students_df["faculty_id"].astype(str) == faculty_id
                ]["reg_no"]

                faculty_logs = logs_df[
                    logs_df["reg_no"].astype(str).isin(faculty_students.astype(str))
                ]

                if not faculty_logs.empty:
                    st.dataframe(faculty_logs, use_container_width=True)
                else:
                    st.warning("No logs found.")

        # ---- GENERATE REPORT ----
        elif prof_option == "Generate Report":
            col1, col2 = st.columns(2)
            from_date = col1.date_input("From Date")
            to_date = col2.date_input("To Date")

            if st.button("Generate Report"):
                logs_df["date"] = pd.to_datetime(logs_df["date"])

                filtered = logs_df[
                    (logs_df["date"] >= pd.to_datetime(from_date)) &
                    (logs_df["date"] <= pd.to_datetime(to_date))
                ]

                if not filtered.empty:
                    filename = "weekly_report.pdf"
                    generate_pdf(filtered, filename)

                    with open(filename, "rb") as f:
                        st.download_button("Download PDF", f, file_name=filename)
                else:
                    st.warning("No logs found in range.")


