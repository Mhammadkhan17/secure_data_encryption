import streamlit as st
import requests

st.title("Secure Data Vault")
api = "http://localhost:5000"

if "token" not in st.session_state:
    st.session_state.token = None

menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Upload", "Files"])

if menu == "Register":
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Register"):
        r = requests.post(f"{api}/register", json={"username": user, "password": pwd})
        st.write(r.json())

if menu == "Login":
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        r = requests.post(f"{api}/login", json={"username": user, "password": pwd})
        res = r.json()
        if "token" in res:
            st.session_state.token = res["token"]
            st.success("Logged in")
        else:
            st.error(res.get("error"))

if menu == "Upload" and st.session_state.token:
    file = st.file_uploader("Upload file")
    if file and st.button("Submit"):
        files = {"file": file.getvalue()}
        headers = {"Authorization": st.session_state.token}
        r = requests.post(f"{api}/upload", files={"file": file}, headers=headers)
        st.write(r.json())

if menu == "Files" and st.session_state.token:
    headers = {"Authorization": st.session_state.token}
    r = requests.get(f"{api}/files", headers=headers)
    for f in r.json():
        st.write(f"{f['filename']} - {f['date']}")
        if st.button(f"Download {f['id']}"):
            res = requests.get(f"{api}/download/{f['id']}", headers=headers)
            st.download_button("Download", res.content, file_name=f["filename"])
