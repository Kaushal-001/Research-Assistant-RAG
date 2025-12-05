import streamlit as st
import requests
import os

# ---------------------------
# CONFIG
# ---------------------------

API_URL = "http://localhost:8000"   # FastAPI backend

st.set_page_config(page_title="AI Research Assistant", layout="centered")
st.title("📘 AI Research Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------------------
# 📤 PDF UPLOAD (optional)
# ---------------------------

st.markdown("### 📤 Upload a research paper (Optional)")

uploaded_pdf = st.file_uploader("Upload a PDF to store on the server", type="pdf")

if uploaded_pdf:
    files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue())}

    with st.spinner("Uploading PDF to FastAPI..."):
        res = requests.post(f"{API_URL}/upload-pdf", files=files)

    if res.status_code == 200:
        st.success(f"Uploaded → {uploaded_pdf.name}")
    else:
        st.error("❌ Upload failed. Check FastAPI backend.")


# ---------------------------
# 🧠 SIDEBAR — DATABASE ACTIONS
# ---------------------------

with st.sidebar:
    st.markdown("### 🔧 Vector Database Controls")

    if st.button("🔁 Index ALL PDFs/TXTs in data/ folder"):
        with st.spinner("Sending indexing request to FastAPI..."):
            res = requests.post(f"{API_URL}/ingest")

        if res.status_code == 200:
            st.success(res.json().get("message", "Indexed successfully!"))
        else:
            st.error("❌ Ingestion failed. Check FastAPI backend.")

    st.markdown("---")
    st.markdown("This UI uses FastAPI for all computation.")


# ---------------------------
# 💬 DISPLAY CHAT HISTORY
# ---------------------------

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------
# 💬 CHAT INPUT → FastAPI /chat
# ---------------------------

query = st.chat_input("Ask a research question...")

if query:
    # 1️⃣ Show USER message
    st.session_state["messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # 2️⃣ Call FastAPI /chat
    with st.spinner("Fetching answer from FastAPI backend..."):
        res = requests.post(
            f"{API_URL}/chat",
            json={"question": query}
        )

    # --- START OF CORRECTION ---
    data = {}
    error_msg = None # Initialize error_msg to None

    if res.status_code != 200:
        # Handle transport/HTTP error (e.g., 500 server crash, 404)
        error_msg = f"❌ HTTP Error {res.status_code}: Could not connect or server failed."
        
        try:
            data = res.json()
            # Append backend message if available
            error_msg += f"\nBackend Message: {data.get('message', 'No message provided.')}"
        except requests.exceptions.JSONDecodeError:
            error_msg += f"\nRaw Response: {res.text}"
            
    else:
        # HTTP 200 OK. Now check the *internal* status from the JSON body.
        data = res.json()
        
        if data.get("status") == "error":
            # Handle internal error (e.g., Groq Rate Limit, DB failure)
            error_msg = f"❌ Internal API Error: {data.get('message', 'Unknown error.')}"
        else:
            # Success Path!
            answer = data["answer"]
            papers = data.get("papers", [])

            # 3️⃣ Display ASSISTANT message
            with st.chat_message("assistant"):
                st.write(answer)

            st.session_state["messages"].append({"role": "assistant", "content": answer})

            # 4️⃣ Show arXiv papers (if used)
            if papers:
                st.sidebar.markdown("### 📚 Relevant arXiv Papers")
                for p in papers:
                    st.sidebar.markdown(f"""
                    **📄 {p['title']}** 👤 {", ".join(p['authors'])}  
                    📅 {p['published']}  
                    🔗 [PDF Link]({p['pdf_url']})  
                    ---
                    """)
            
            # ⚠️ REMOVED: The 'return' statement is now gone.
            # The script will naturally continue past the error block below.

    # --- END OF CORRECTION ---

    # This code only runs if error_msg is NOT None (i.e., if an error occurred)
    if error_msg: 
        with st.chat_message("assistant"):
            st.write(error_msg)
        st.session_state["messages"].append({"role": "assistant", "content": error_msg})