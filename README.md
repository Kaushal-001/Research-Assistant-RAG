# 🔍 AI Research Assistant — RAG + Groq Llama 3 + FastAPI + Streamlit

An intelligent **AI Research Assistant** built using Retrieval-Augmented Generation (RAG),  
Groq’s ultra-fast Llama 3 models, FAISS vector search, and a clean Streamlit UI.

This assistant can:
- Retrieve and understand scientific papers  
- Answer complex research questions  
- Generate math-heavy explanations in LaTeX  
- Summarize papers  
- Perform hybrid reasoning using local DB + arXiv search  


---

## 🎥 Demo Video

Click the thumbnail below to watch the demo:

<a href="https://drive.google.com/file/d/1QT47GJFbBSRQAYSJo8BBmHzdmoSqlSdM/view?usp=sharing" target="_blank">
 <img width="600" height="400" alt="Image" src="https://github.com/user-attachments/assets/c52162d9-2298-48ce-8510-54e5cde6129e" />
</a>

Or open directly:  
👉 **https://drive.google.com/file/d/1QT47GJFbBSRQAYSJo8BBmHzdmoSqlSdM/view?usp=sharing**

---

## 🚀 Features

### 🔎 **1. Hybrid Retrieval**
- Retrieves relevant chunks from your vector DB  
- Searches arXiv for related academic papers  
- Combines both sources intelligently  

### 🧠 **2. Advanced LLM Reasoning**
Uses **Groq’s Llama 3** for:
- Scientific explanations  
- Research-oriented answers  
- LaTeX math formatting  
- Multi-source synthesis  

### 🖥️ **3. Streamlit UI**
A clean interface to:
- Ask research questions  
- Display retrieved context  
- Show structured outputs  

### ⚡ **4. FastAPI Backend**
Handles:
- Query → retrieval → LLM pipeline  
- Paper search integration (arXiv API)  
- Response formatting  

---

## 🏗️ Project Architecture
🧩 Architecture Breakdown
1️⃣ User Interface (Streamlit Frontend)
- User types a research question
- Sends request to your FastAPI backend

2️⃣ FastAPI Backend
Handles the entire pipeline:
- Receives query
- Retrieves context
- Searches arXiv
- Passes everything to LLM
Acts as the “controller” of the system.

3️⃣ Vector Database (AstraDB )
- Stores all embedded research PDFs
- Supports semantic similarity search
- Returns the top-K useful text chunks

4️⃣ arXiv Search Layer
- Fetches external papers
- Used when local retrieval is weak
- Enhances reasoning quality

5️⃣ Groq Llama 3 Inference
- Combines local DB + arXiv + query
- Generates the final high-quality answer
- Extremely low latency using Groq hardware

6️⃣ Final Result Returned to UI
- Ready-to-display formatted response

<div align="center"> <img width="200" alt="Image" src="https://github.com/user-attachments/assets/9e66b0e4-5c42-407d-8668-227369c035ac" /></div>


---
## 🧠 LANGFLOW DIAGRAM
<div align="center"> <img width="1113" height="648" alt="Image" src="https://github.com/user-attachments/assets/93111e68-9dc8-4469-b28c-0945e494d2a9" /></div>
This LangFlow diagram represents a complete Retrieval-Augmented Generation (RAG) workflow that processes uploaded PDFs, retrieves relevant knowledge, pulls external papers from arXiv, and generates high-quality answers using Groq’s Llama models.

🔷 1. File Loader
- Uploads PDF research papers that serve as your knowledge base.

🔷 2. Split Text
- Chunks the PDF into smaller segments for better embedding and retrieval.

🔷 3. AstraDB (Vector Store)
- Stores embedded chunks and performs similarity search based on the user’s query.

🔷 4. Chat Input
- User enters a question; this triggers retrieval and LLM processing.

🔷 5. Prompt Template
- Combines the retrieved context and user query into a structured prompt for the LLM.

🔷 6. Groq LLM
- Llama model reads the prompt and generates a fast, grounded response.

🔷 7. Parser
- Cleans and formats the LLM response.

🔷 8. arXiv Tool
- Fetches relevant external papers to supplement local PDF knowledge.

🔷 9. Agent
- Coordinates tools + LLM reasoning to produce the final answer.

🔷 10. Chat Output
- Displays the final answer to the user.
