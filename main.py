import streamlit as st
import psycopg2
import bcrypt

# ---------- DB CONNECTION ----------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        port=5432,
        password="12345",
        dbname="client_details"
    )

# ---------- LOGIN FUNCTION ----------
def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT password_hashed, role FROM client WHERE username = %s",
        (username,)
    )

    result = cur.fetchone()

    if result:
        stored_hash, role = result

        stored_hash = stored_hash.strip()

        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return role

    return None
        
# ---------- STREAMLIT UI ----------
st.title("CLIENT QUERY MANAGEMENT SYSTEM")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
role=st.selectbox("Role",['client',"admin"])

if st.button("Login"):
    role = login_user(username, password)

    if role:
        st.success(f"Login successful! Role: {role}")
    else:
        st.error("Invalid username or password")

    if role == "client":
        st.switch_page("pages\client.py")
    else:
        st.switch_page("pages\support.py")   
        
                           

