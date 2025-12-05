# src/graph.py
from typing import List, TypedDict, Dict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.ingest import ingest_documents
from src.retrieve import retrieve_context
from src.summary import answer_from_sources # ✅ we will adapt this in summary_node
from src.arxiv_search import search_arxiv


class GraphState(TypedDict):
    query: str
    db_context: str
    papers: List[Dict]
    summary: dict
    status: str

def build_graph():
    g = StateGraph(GraphState)

    # 1) Ingest node (PDF → AstraDB from folder)
    def ingest_node(state: GraphState):
        print("🚀 Ingesting documents from local data/ folder...")
        ingest_documents()
        state["db_context"] = "PAPER_INGESTED"
        state["status"] = "INGESTED_FROM_FOLDER"
        state["papers"] = []
        return state

    # 2) Retrieve node (AstraDB similarity search using HF embeddings)
    def retrieve_node(state: GraphState):
        ctx = retrieve_context(state["query"])
        state["db_context"] = ctx if ctx else "NO_RESULTS"
        return state

    # 3) arXiv fallback node (only when no DB context)
    def arxiv_node(state: GraphState):
        print("🌐 Hybrid mode → always searching arXiv...")
        papers = search_arxiv(state["query"], max_results=5)
        state["papers"] = papers
        return state


    # 4) Summary node (Llama via Groq answering user query)
    def summary_node(state: GraphState):
        # ✅ Call summary function using 3 individual parameters
        papers = state.get("papers", [])
        assistance_text = answer_from_sources(state["query"], state["db_context"], papers)

        state["summary"] = {"text": assistance_text}
        return state

    # Register nodes
    g.add_node("ingest", ingest_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("arxiv", arxiv_node)
    g.add_node("summary", summary_node)

    # Wire graph
    g.add_edge(START, "ingest")
    g.add_edge("ingest", "retrieve")
    g.add_edge("retrieve", "arxiv")
    g.add_edge("arxiv", "summary")
    g.add_edge("summary", END)

    memory = MemorySaver()
    return g.compile(checkpointer=memory)
