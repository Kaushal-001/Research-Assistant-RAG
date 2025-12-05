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

### 📊 **3. RAGAS Evaluation**
Evaluates model performance using:
- Faithfulness  
- Answer Relevancy  
- Context Precision  
- Context Recall  

### 🖥️ **4. Streamlit UI**
A clean interface to:
- Ask research questions  
- Display retrieved context  
- Show structured outputs  

### ⚡ **5. FastAPI Backend**
Handles:
- Query → retrieval → LLM pipeline  
- Paper search integration (arXiv API)  
- Response formatting  

---

## 🏗️ Project Architecture

