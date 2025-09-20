import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from Mama.embedding_factory import get_embeddings
from Mama.train import train_on_documents

try:
    from langchain_community.vectorstores import FAISS  # type: ignore
except Exception:  # pragma: no cover
    from langchain.vectorstores import FAISS  # type: ignore

try:
    from langchain_community.document_loaders import PyPDFLoader  # type: ignore
except Exception:  # pragma: no cover
    from langchain.document_loaders import PyPDFLoader  # type: ignore

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
except Exception:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore


def _load_faiss(kb_dir: str, kb_id: str):
    kb_path = Path(kb_dir) / kb_id
    embeddings = get_embeddings()
    if not kb_path.exists() or not embeddings:
        return None
    return FAISS.load_local(
        str(kb_path),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )


def list_documents(kb_dir: str, kb_id: str, limit: int | None = None) -> List[Dict[str, Any]]:
    """Return metadata for documents stored in the FAISS index."""
    store = _load_faiss(kb_dir, kb_id)
    if not store:
        return []

    results: List[Dict[str, Any]] = []
    for doc_id, doc in store.docstore._dict.items():  # type: ignore[attr-defined]
        info = {
            "id": doc_id,
            "source": doc.metadata.get("source", ""),
            "page_content": doc.page_content,
        }
        results.append(info)
        if limit and len(results) >= limit:
            break
    results.sort(key=lambda item: item.get("source", ""))
    return results


def get_faiss_stats(kb_dir: str, kb_id: str) -> Dict[str, Any]:
    store = _load_faiss(kb_dir, kb_id)
    if not store:
        return {
            "documents": 0,
            "vectors": 0,
            "dimension": 0,
            "disk_size": 0,
        }

    kb_path = Path(kb_dir) / kb_id
    size = 0
    if kb_path.exists():
        for file in kb_path.glob("**/*"):
            if file.is_file():
                size += file.stat().st_size

    vectors = len(store.index_to_docstore_id)
    faiss_index = getattr(store, "_faiss_index", None) or getattr(store, "index", None)
    embedding_dim = getattr(faiss_index, "d", 0) if faiss_index is not None else 0

    return {
        "documents": len(store.docstore._dict),  # type: ignore[attr-defined]
        "vectors": vectors,
        "dimension": embedding_dim,
        "disk_size": size,
    }


def ingest_file(file_path: str, kb_dir: str, kb_id: str, title: str = "", description: str = "") -> Tuple[bool, str]:
    path = Path(file_path)
    if not path.exists():
        return False, "File non trovato"

    if path.suffix.lower() != ".pdf":
        return False, "Sono supportati solo file PDF per questo test"

    try:
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        splits = splitter.split_documents(docs)
        train_on_documents(
            kb_dir,
            kb_id,
            src_dir="",
            documents=splits,
            title=title,
            description=description,
            return_summary=False,
        )
        return True, "Documento ingestato con successo"
    except Exception as exc:  # pragma: no cover - defensive
        return False, str(exc)
