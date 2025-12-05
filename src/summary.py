# src/summary.py
import logging
from langchain_groq import ChatGroq
from src.config import GROQ_API_KEY, LLAMA_MODEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# controllable settings
MAX_PAPERS_IN_PROMPT = 5      # pass at most this many papers to the LLM
MAX_SUMMARY_CHARS = 400       # truncate each paper summary to this length
LLM_TEMPERATURE = 0.0         # deterministic answers
LLM_MAX_TOKENS = 800


def _truncate(text: str, n: int) -> str:
    if not text:
        return ""
    if len(text) <= n:
        return text
    return text[: n - 3].rstrip() + "..."


def _format_papers_for_prompt(papers: list) -> str:
    """
    Convert list[dict] to a compact, readable block for the prompt.
    Each paper block: index, title, authors, published, pdf link, short summary (truncated).
    Limit to MAX_PAPERS_IN_PROMPT.
    """
    if not papers:
        return "No arXiv papers found."

    blocks = []
    for i, p in enumerate(papers[:MAX_PAPERS_IN_PROMPT], start=1):
        title = p.get("title", "No title").strip()
        authors = ", ".join(p.get("authors", [])) if p.get("authors") else "Unknown authors"
        published = p.get("published", "").strip() or "Unknown date"
        pdf = p.get("pdf_url") or p.get("arxiv_id") or "No PDF link"
        summary = _truncate(p.get("summary", "").replace("\n", " ").strip(), MAX_SUMMARY_CHARS)
        blocks.append(
            f"[{i}] Title: {title}\n"
            f"    Authors: {authors}\n"
            f"    Published: {published}\n"
            f"    PDF: {pdf}\n"
            f"    Summary: {summary if summary else 'No summary available.'}\n"
        )
    return "\n".join(blocks)


def answer_from_sources(query: str, context: str, papers: list) -> str:
    """
    Hybrid Research Assistant (Final Updated Version):

    PRIORITY:
    1) DB context strong → answer ONLY from DB (no DB mention)
    2) DB context weak → blend DB + Arxiv naturally
    3) DB empty → use Arxiv only:
          - Give a natural explanation first
          - Then list 5 related papers
    4) ALWAYS use clean LaTeX for all mathematical equations
    """

    context = context or ""
    context_stripped = context.strip()
    context_len = len(context_stripped)

    DB_STRONG = context_len >= 500
    DB_WEAK = 0 < context_len < 500
    DB_EMPTY = context_len == 0

    has_papers = bool(papers and len(papers) > 0)

    llm = ChatGroq(
        model=LLAMA_MODEL,
        temperature=0.0,
        max_tokens=1500,
        groq_api_key=GROQ_API_KEY
    )

    # ------------------------------------------------
    # CASE 1: STRONG DB → ONLY DB (NO DB MENTION)
    # ------------------------------------------------
    if DB_STRONG:
        prompt = fr"""
You are a research assistant.

Answer the user's question using ONLY the text below. 
Your answer MUST be:
- **Long, comprehensive, and deeply elaborated**
- Written at a **graduate or research level**
- Step-by-step and highly explanatory

Do NOT mention where the information came from.
Do NOT talk about database, retrieval, or context.

When mathematics is needed:
- ALWAYS use LaTeX.
- Inline math example: $ E = mc^2 $
- Block math example:
$$
\frac{{QK^T}}{{\sqrt{{d_k}}}}
$$
Use proper LaTeX: \frac, \sqrt, \sum, \times, etc.

--- SOURCE ---
{context_stripped}

--- QUESTION ---
{query}

Now write a natural, direct answer. No mention of where the information was obtained.
"""
        r = llm.invoke(prompt)
        return r.content if hasattr(r, "content") else str(r)

    # ------------------------------------------------
    # CASE 2: WEAK DB → DB + ARXIV
    # ------------------------------------------------
    if DB_WEAK and has_papers:
        papers_text = _format_papers_for_prompt(papers)

        prompt = fr"""
You are a research-grade LLM designed for **deep scientific explanation**.

Use BOTH:
- The provided source text (primary)
- The Arxiv papers (secondary)

Do NOT mention database, retrieval, or missing context.

When equations are needed:
- Write LaTeX inline or block.
Example inline: $ \text{{softmax}}(x_{{i}}) = \frac{{e^{{x_{{i}}}}}}{{\sum_{{j}} e^{{x_{{j}}}}}} $


--- SOURCE MATERIAL ---
{context_stripped}

--- ARXIV PAPERS ---
{papers_text}

--- QUESTION ---
{query}

Write a complete, natural explanation combining both sources smoothly.
"""
        r = llm.invoke(prompt)
        return r.content if hasattr(r, "content") else str(r)

    # ------------------------------------------------
    # CASE 3: DB EMPTY → ARXIV ONLY
    # ------------------------------------------------
    if DB_EMPTY and has_papers:
        papers_text = _format_papers_for_prompt(papers)

        prompt = fr"""
You are an expert research assistant.

Use the Arxiv papers below PLUS general scientific knowledge.

Your response MUST follow this structure:

====================  
**(1) Deep Explanation**  
Write a **long, detailed, fully elaborated** explanation of the concept.  
Requirements:
- Graduate-level clarity  
- Step-by-step reasoning  
- Mathematical intuition + LaTeX equations  
- Formal definitions, derivations, assumptions  
- Examples, edge cases, and practical implications  
- Aim for **600+ words**  

follow the rules:
Rules:
- DO NOT say anything about databases or missing context.
- FIRST: give a natural explanation of the concept.
- THEN: list 5 related papers.
- Use LaTeX for all mathematical expressions.

Example block equation:
$$
\text{{Attention}}(Q,K,V) = \text{{softmax}}\left( \frac{{QK^T}}{{\sqrt{{d_k}}}} \right)V
$$

--- ARXIV PAPERS ---
{papers_text}

--- QUESTION ---
{query}

REQUIRED OUTPUT:
1. Natural explanation (no mention of retrieval or DB)
2. Heading: "5 related papers (PDF links):"
3. List exactly 5 papers with:
   Title — Authors (Year)
   PDF: link
"""
        r = llm.invoke(prompt)
        return r.content if hasattr(r, "content") else str(r)

    # ------------------------------------------------
    # CASE 4: NOTHING FOUND ANYWHERE
    # ------------------------------------------------
    return "No relevant information was found for this query."
