import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os
st.write("App Started Successfully")

EXCEL_FILE = "Log.xlsx"

# ---------- Helper Functions ----------

def load_students():
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet1")

def load_logs():
    #try:
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet2")
    #except:
        #return pd.DataFrame(columns=["reg_no","name","faculty","date","start_time","end_time","description"])

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

# ---------- UI ----------

st.title("Student Log Management System")

page = st.sidebar.selectbox("Select Page", ["Student", "Professor"])

students_df = load_students()
logs_df = load_logs()

# ================= STUDENT PAGE =================

if page == "Student":
    st.header("Student Log Entry")
    students_df["reg_no"] = students_df["reg_no"].astype(str)

    reg_no = st.text_input("Enter Register Number")

    if reg_no:
        student = students_df[students_df["reg_no"] == reg_no]
        st.write(reg_no)
        if not student.empty:
            student = student.iloc[0]

            st.write("Name:", student["name"])
            st.write("Problem Statement:", student["problem_statement"])
            st.write("Problem Number:", student["problem_no"])
            st.write("Faculty Guide:", student["faculty_guide"])
            st.write("Date:", datetime.today().date())

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

# ================= PROFESSOR PAGE =================

if page == "Professor":
    st.header("Professor Dashboard")

    st.subheader("View All Logs")

    display_df = logs_df.copy()
    display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%d-%m-%Y")

    st.dataframe(display_df)

    st.subheader("Search by Register Number")
    #logs_df["reg_no"] = logs_df["reg_no"].astype(str)

    search_reg = st.text_input("Enter Register Number to Search")

    if search_reg:
        search_reg=int(search_reg)
        filtered = logs_df[logs_df["reg_no"] == search_reg]
        
        filtered_display = filtered.copy()
        filtered_display["date"] = pd.to_datetime(filtered_display["date"]).dt.strftime("%d-%m-%Y")
        st.dataframe(filtered_display)

        #st.write("Search Input:", search_reg)
        #st.write("Logs Reg Nos:", logs_df["reg_no"].tolist())
        #st.write("Logs dtype:", logs_df["reg_no"].dtype)


    st.subheader("View Logs by Faculty ID")
    faculty_id = st.text_input("Enter Faculty ID")

    if faculty_id:
        faculty_students = students_df[students_df["faculty_id"] == faculty_id]["reg_no"]
        faculty_logs = logs_df[logs_df["reg_no"].isin(faculty_students)]
        st.dataframe(faculty_logs)

    # PDF Section
    st.subheader("Generate PDF Report")

    from_date = st.date_input("From Date")
    to_date = st.date_input("To Date")

    if st.button("Generate Report"):
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
            st.warning("No logs in selected date range")
