import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Document Search Bot", layout="wide")
st.title("📄 Document Search Bot")

# ------------------- User Login Section -------------------
st.sidebar.header("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if not username or not password:
    st.warning("Please enter your username and password in the sidebar to continue.")
    st.stop()

auth = HTTPBasicAuth(username, password)

# ------------------- Check Role -------------------
try:
    role_response = requests.post(f"{BACKEND_URL}/get-role/", auth=auth)
    role_response.raise_for_status()
    role = role_response.json().get("role")
    st.sidebar.success(f"Logged in as: {username} ({role})")
except requests.exceptions.RequestException:
    st.error("❌ Authentication failed. Please check your credentials.")
    st.stop()

# ------------------- File Upload Section (Admin Only) -------------------
if role == "admin":
    st.header("📤 Upload Documents (Admin Only)")
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, Word, Excel, PPT, TXT)",
        type=["pdf", "docx", "txt", "xlsx", "pptx"]
    )

    if uploaded_file and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            response = requests.post(f"{BACKEND_URL}/upload/", files=files, auth=auth)
            response.raise_for_status()
            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        except requests.exceptions.RequestException:
            st.error(f"❌ Upload failed: {response.text}")

# ------------------- Query Section -------------------
st.header("🔍 Ask a Question")
query = st.text_input("Enter your query:")
if st.button("Search") and query:
    try:
        response = requests.post(f"{BACKEND_URL}/query/", data={"query": query}, auth=auth)
        response.raise_for_status()
        st.write("**Response:**", response.json().get("answer"))
    except requests.exceptions.RequestException:
        st.error(f"❌ Error fetching response: {response.text}")

# ------------------- View Uploaded Files -------------------
st.header("📂 Uploaded Documents")
if st.button("View Files"):
    try:
        response = requests.get(f"{BACKEND_URL}/list-files/", auth=auth)
        response.raise_for_status()
        files = response.json().get("uploaded_files", [])
        if files:
            st.write("📑 **Uploaded Files:**")
            for file in files:
                st.write(f"- {file}")
        else:
            st.write("📭 No files uploaded.")
    except requests.exceptions.RequestException:
        st.error(f"❌ Could not fetch files: {response.text}")

# ------------------- Delete File Section (Admin Only) -------------------
if role == "admin":
    st.header("🗑️ Delete a Document (Admin Only)")
    delete_filename = st.text_input("Enter the file name to delete:")
    if st.button("Delete"):
        try:
            response = requests.delete(f"{BACKEND_URL}/delete/{delete_filename}", auth=auth)
            response.raise_for_status()
            st.success(f"✅ {delete_filename} deleted successfully!")
        except requests.exceptions.RequestException:
            st.error(f"❌ Error deleting file: {response.text}")
