import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import os
import uuid

# ---------------- DB CONNECTION ----------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        port="5432",
        password="12345",
        dbname="client_details"
    )

# ---------------- UI ----------------
st.title("Query Submission Form")

client_email = st.text_input("Email ID")
client_mobile = st.text_input("Phone number")

query_heading = st.selectbox(
    "Query Heading",
    ["Technical", "Billing", "Log in issue", "Bug Report", "General", "Other"]
)

query_description = st.text_area("Query Description")

# Store query_id in session (important for Streamlit reruns)
if "query_id" not in st.session_state:
    st.session_state.query_id = None

# ---------------- SUBMIT ----------------
if st.button("Submit Query"):

    if client_email and client_mobile and query_heading and query_description:

        date_raised = datetime.now()
        status = "opened"
        date_closed = None

        # 1. SAVE TO DATABASE FIRST (to get the generated Q ID)
        conn = get_connection()
        cur = conn.cursor()

        # Notice: query_id is NOT in the columns or values list here
        insert_query = """
        INSERT INTO synthetic_client_detail
        (client_email, client_mobile, query_heading, query_description, status, date_raised, date_closed)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING query_id;
        """

        cur.execute(insert_query, (
            client_email,
            client_mobile,
            query_heading,
            query_description,
            status,
            date_raised,
            date_closed
        ))

        # 2. GET THE NEW ID FROM DATABASE
        new_id = cur.fetchone()[0]
        st.session_state.query_id = new_id  # This replaces the line causing your error

        conn.commit()
        cur.close()
        conn.close()

        # 3. SAVE TO CSV (using the new_id we just got)
        data = {
            "Query ID": new_id,
            "Email": client_email,
            "Phone_number": client_mobile,
            "Heading": query_heading,
            "Description": query_description,
            "Status": status,
            "Created Time": date_raised,
            "Closed Time": date_closed
        }

        df = pd.DataFrame([data])
        file = "c:/data/synthetic_client_queries.csv"

        if os.path.exists(file):
            df.to_csv(file, mode='a', header=False, index=False)
        else:
            # Ensure folder exists or this will fail
            df.to_csv(file, index=False)

        st.success(f"Query submitted successfully! ID: {new_id}")

    else:
        st.error("Please fill all fields")