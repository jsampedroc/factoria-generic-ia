import os
from pathlib import Path
from typing import List, Dict

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = Path(os.getenv("CHROMA_PATH", ".chroma"))


def retrieve_context(query: str, k: int = 5) -> List[Dict]:
    """Retrieve top-k context chunks. Returns [] if index or embeddings are unavailable."""
    if not CHROMA_PATH.exists():
        return []

    api_key = os.getenv("EMBEDDINGS_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("EMBEDDINGS_BASE_URL") or os.getenv("AI_BASE_URL") or os.getenv("OPENAI_BASE_URL")

    if not api_key:
        return []

    try:
        embeddings = OpenAIEmbeddings(api_key=api_key, base_url=base_url)
        db = Chroma(persist_directory=str(CHROMA_PATH), embedding_function=embeddings)
        results = db.similarity_search_with_score(query, k=k)
    except Exception:
        return []

    return [
        {
            "text": doc.page_content,
            "source": doc.metadata.get("source"),
            "score": score,
        }
        for doc, score in results
    ]
