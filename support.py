import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# 1. Database Connection Function
def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        port="5432",
        password="12345",
        dbname="client_details"
    )

st.set_page_config(layout="wide")
st.title("Client Query Management (Support Dashboard)")

# --- FETCH DATA FROM DATABASE ---
def load_data():
    conn = get_connection()
    # We use ORDER BY query_id ASC to ensure the sequence looks correct
    query = "SELECT * FROM synthetic_client_detail ORDER BY query_id ASC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# --- Filtering Section ---
col1, col2 = st.columns(2)

with col1:
    status_filter = st.selectbox("Filter by Status", ["All", "opened", "Closed"])
with col2:
    category_filter = st.selectbox(
        "Filter by Category",
        ["All", "Technical", "Billing", "Log in issue", "Bug Report", "General", "Other"]
    )

# Apply Filters
filtered_df = df.copy()
if status_filter != "All":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["query_heading"] == category_filter]

st.subheader("Active Queries")
st.dataframe(filtered_df, use_container_width=True)

# --- Close Query Section ---
st.divider()
st.subheader("Action: Close a Query")

# User types the ID (e.g., Q5201)
query_to_close = st.text_input("Enter Query ID to close")

if st.button("Confirm Close"):
    if query_to_close:
        # 1. Check if ID exists in our table
        if query_to_close in df["query_id"].values:
            conn = get_connection()
            cur = conn.cursor()
            
            # 2. Update the Database
            cur.execute("""
                UPDATE synthetic_client_detail 
                SET status = 'Closed', date_closed = %s 
                WHERE query_id = %s
            """, (datetime.now(), query_to_close))
            
            conn.commit()
            cur.close()
            conn.close()
            
            # 3. SHOW THE SUCCESS MESSAGE
            st.success(f"Query {query_to_close} closed successfully!")
            
            # 4. TRIGGER THE REFRESH
            # This makes the table at the top update to show 'Closed'
            st.rerun() 
            
        else:
            st.error("Query ID not found. Please double-check the ID.")
    else:
        st.warning("Please enter a Query ID first.")