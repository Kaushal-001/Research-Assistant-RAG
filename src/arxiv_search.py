import urllib.request, urllib.parse
from urllib.parse import urlparse
from defusedxml.ElementTree import fromstring
from typing import List, Dict
import re


ARXIV_API_URL = "http://export.arxiv.org/api/query?"



def preprocess_query(user_query: str) -> str:
    # 1. Lowercase text
    q = user_query.lower()

    # 2. Extract words (ignore punctuation)
    tokens = re.findall(r"[a-zA-Z\-]+", q)

    # 3. Stopwords (domain-agnostic)
    stopwords = {
        "how", "does", "do", "what", "why", "where", "when", "which",
        "recent", "latest", "models", "explain", "impact", "affect",
        "improve", "accuracy", "such", "as", "the", "a", "an", "and", "of",
        "on", "in", "to", "for", "from", "using", "use", "with", "based"
    }

    # 4. Filter tokens
    keywords = [tok for tok in tokens if tok not in stopwords]

    # ---------------------------------------------------------
    # 5. Group keywords into meaningful phrases
    #    Example: ["monetary", "policy", "uncertainty"]
    #    → all:"monetary policy uncertainty"
    # ---------------------------------------------------------
    
    phrases = []
    current = []

    for word in keywords:
        # If the word is short or a common term, break phrases
        if len(word) <= 3:
            if current:
                phrases.append(" ".join(current))
                current = []
            continue

        current.append(word)

        # If previous and next words aren't forming a clear phrase, push
        # (optional heuristic)
    
    if current:
        phrases.append(" ".join(current))

    # ---------------------------------------------------------
    # 6. Build the arXiv boolean query
    # ---------------------------------------------------------

    # Example:
    # ['monetary policy uncertainty', 'stock market volatility']
    # →
    # all:"monetary policy uncertainty" AND all:"stock market volatility"

    if not phrases:
        # fallback
        return f'all:"{user_query}"'

    boolean_clauses = [f'all:"{p}"' for p in phrases]
    structured_query = " AND ".join(boolean_clauses)

    return structured_query



def parse_arxiv_atom(xml_text: str) -> List[Dict]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = fromstring(xml_text)
    papers = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        summary = entry.find("atom:summary", ns).text.strip()
        published = entry.find("atom:published", ns).text.strip()
        authors = [a.find("atom:name", ns).text.strip() for a in entry.findall("atom:author", ns)]

        # Extract PDF link
        pdf_url = None
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib["href"]
                break

        papers.append({
            "title": title,
            "summary": summary,
            "authors": authors,
            "published": published,
            "pdf_url": pdf_url
        })

    return papers




# -------------------------------------------------
# 3. Main search function
# -------------------------------------------------
def search_arxiv(topic: str, max_results: int = 8) -> List[Dict]:
    from urllib.parse import urlencode

    structured_query = preprocess_query(topic)

    print(f"\n📘 Raw query: {topic}")
    print(f"🔍 Transformed arXiv query: {structured_query}\n")

    params = {
        "search_query": structured_query,
        "max_results": max_results,
    }

    url = ARXIV_API_URL + urlencode(params)

    resp = urllib.request.urlopen(url)
    xml_text = resp.read().decode("utf-8")

    return parse_arxiv_atom(xml_text)