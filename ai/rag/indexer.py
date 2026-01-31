import os
from pathlib import Path
from typing import Iterable, List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = Path(os.getenv("CHROMA_PATH", ".chroma"))

DEFAULT_INCLUDE_DIRS = [
    Path("templates"),
    Path("ai_service/prompts"),
    Path("README.md"),
]


def _collect_texts() -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []

    for p in DEFAULT_INCLUDE_DIRS:
        if p.is_file() and p.exists():
            items.append((p.read_text(encoding="utf-8", errors="ignore"), str(p)))
            continue

        if p.is_dir() and p.exists():
            for f in p.rglob("*"):
                if f.is_file():
                    items.append((f.read_text(encoding="utf-8", errors="ignore"), str(f)))

    return items


def build_index() -> None:
    """Build a local Chroma index from repo files.

    Requires an embeddings-capable OpenAI-compatible endpoint.
    If your provider doesn't support embeddings, you can skip RAG.
    """
    texts = _collect_texts()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    documents: List[str] = []
    metadatas: List[dict] = []

    for text, source in texts:
        for chunk in splitter.split_text(text):
            documents.append(chunk)
            metadatas.append({"source": source})

    api_key = os.getenv("EMBEDDINGS_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("EMBEDDINGS_BASE_URL") or os.getenv("AI_BASE_URL") or os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise RuntimeError("Missing EMBEDDINGS_API_KEY (or DEEPSEEK_API_KEY / OPENAI_API_KEY).")

    embeddings = OpenAIEmbeddings(api_key=api_key, base_url=base_url)

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    Chroma.from_texts(
        documents,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=str(CHROMA_PATH),
    )
