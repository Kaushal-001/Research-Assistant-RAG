from sentence_transformers import SentenceTransformer
from langchain_astradb import AstraDBVectorStore
from src.config import VECTOR_COLLECTION, ASTRA_DB_TOKEN, ASTRA_DB_ENDPOINT


class LocalEmbeddings:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_query(self, text):
        return self.model.encode(text).tolist()

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()
    
def retrieve_context(query: str, k = 4 ) -> str:
    embeddings = LocalEmbeddings()
    vectore_store = AstraDBVectorStore(
        collection_name=VECTOR_COLLECTION,
        embedding=embeddings,
        token=ASTRA_DB_TOKEN,
        api_endpoint=ASTRA_DB_ENDPOINT
    )

    docs = vectore_store.similarity_search(query, k=k)
    if not docs:
        return ""
    return "\n".join([doc.page_content for doc in docs])
