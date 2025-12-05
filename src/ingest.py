from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_astradb import AstraDBVectorStore
import os
from pathlib import Path
from src.config import ASTRA_DB_TOKEN, ASTRA_DB_ENDPOINT, VECTOR_COLLECTION
from src.utils import extract_text_from_pdf

# ------------ CONFIG ------------
DATA_DIRS = [
    "data",                  # uploaded files
    "data/paper",            # original folder
    "data/uploaded_papers",  # upload folder (if used)
]

# ------------ INGEST ONE DOCUMENT ------------
def store_documents(file_path: str, text: str):
    if not text or len(text.strip()) < 50:
        return {"status": "skipped", "message": f"No usable text extracted from {file_path}"}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = AstraDBVectorStore(
        collection_name=VECTOR_COLLECTION,
        embedding=embeddings,
        token=ASTRA_DB_TOKEN,
        api_endpoint=ASTRA_DB_ENDPOINT
    )

    vector_store.add_texts(chunks)

    return {
        "status": "success",
        "file": file_path,
        "chunks_stored": len(chunks)
    }

# ------------ MAIN INGEST FUNCTION ------------
def ingest_documents():
    total_files = 0
    total_chunks = 0

    for directory in DATA_DIRS:
        path = Path(directory)
        if not path.exists():
            continue

        for pdf in path.rglob("*.pdf"):     # <-- Recursively find all PDFs
            print(f"📄 Ingesting PDF: {pdf}")
            text = extract_text_from_pdf(str(pdf))
            result = store_documents(str(pdf), text)
            print(result)

            if result["status"] == "success":
                total_files += 1
                total_chunks += result["chunks_stored"]

        for txt in path.rglob("*.txt"):
            print(f"📘 Ingesting text: {txt}")
            with open(txt, "r", encoding="utf-8") as f:
                text = f.read()
            result = store_documents(str(txt), text)
            print(result)

            if result["status"] == "success":
                total_files += 1
                total_chunks += result["chunks_stored"]

    return {
        "status": "completed",
        "files_ingested": total_files,
        "total_chunks": total_chunks
    }
