import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict


# Ensure local package has priority over installed distributions
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Mama.train import train_single_doc  # noqa: E402
from Mama.chains import get_response  # noqa: E402


LOGS_DIR = Path("test/logs")
PDF_SRC_DIR = Path("test/pdf_src")
KB_ROOT = Path("test/kb")
DB_PATH = Path("database/db.json")

KB_ID = "kb_test"
USER_ID = "test_user"

PROMPT_TEMPLATE = (
    "Usa il contesto per rispondere.\n"
    "Contesto:\n{context}\n"
    "Domanda: {question}\n"
    "Cronologia: {chat_history}\n"
)

DEFAULT_PDF_TEXT = (
    "Il presente documento descrive i principali servizi comunali: ufficio anagrafe, "
    "sportello tributi e centro di raccolta rifiuti. Spiega come utilizzare la piattaforma "
    "MaMa per prenotare appuntamenti online e ottenere assistenza digitale sui servizi cittadini."
)

_INITIALIZED = False


def setup_logging(log_file: Path, stream: bool = True) -> None:
    """Configure logging handlers for tests."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handlers = [logging.FileHandler(log_file, mode="w", encoding="utf-8")]
    if stream:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(message)s',
        handlers=handlers,
        force=True,
    )


def write_minimal_pdf(path: Path, text: str) -> None:
    """Write a minimal single-page PDF containing the provided text."""
    content = (
        "%PDF-1.1\n"
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        f"4 0 obj\n<< /Length {44 + len(text)} >>\nstream\n"
        "BT\n/F1 24 Tf\n100 700 Td\n"
        f"({text}) Tj\n"
        "ET\nendstream\nendobj\n"
        "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        "xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n"
        "0000000116 00000 n \n0000000293 00000 n \n0000000420 00000 n \n"
        "trailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n511\n%%EOF\n"
    )
    path.write_text(content)


def ensure_database(db_path: Path = DB_PATH, reset_to_dummy: bool = False) -> None:
    """Create a minimal database configuration file for tests if needed."""
    exists = db_path.exists()
    if exists and not reset_to_dummy:
        return

    if not exists or reset_to_dummy:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        data: Dict[str, Any] = {
            "config": {"model": "Dummy"},
            "LLMs": [
                {
                    "model": "Dummy",
                    "parameters": {},
                    "prompt_template": PROMPT_TEMPLATE,
                    "input_variables": ["context", "question", "chat_history"],
                }
            ],
            "users": [
                {
                    "user_id": USER_ID,
                    "sessions": [
                        {
                            "id": KB_ID,
                            "title": KB_ID,
                            "kb_id": KB_ID,
                            "type": "GENERAL",
                            "search_type": "similarity",
                            "num_docs": 2,
                            "prompt_template": PROMPT_TEMPLATE,
                            "chat_history": [],
                        }
                    ],
                }
            ],
            "KBs": [],
        }
        db_path.write_text(json.dumps(data, indent=4), encoding="utf-8")


def prepare_pdf_source(text: str = DEFAULT_PDF_TEXT) -> None:
    """Generate the sample PDF used for ingestion tests."""
    if PDF_SRC_DIR.exists():
        shutil.rmtree(PDF_SRC_DIR)
    PDF_SRC_DIR.mkdir(parents=True, exist_ok=True)
    write_minimal_pdf(PDF_SRC_DIR / "sample.pdf", text)
    logging.info("Sample PDF created")


def prepare_vector_store() -> None:
    """Rebuild the FAISS index for the sample knowledge base."""
    KB_ROOT.mkdir(parents=True, exist_ok=True)
    kb_path = KB_ROOT / KB_ID
    if kb_path.exists():
        shutil.rmtree(kb_path)
    summary = train_single_doc(str(KB_ROOT), KB_ID, str(PDF_SRC_DIR))
    logging.info("Ingestion completed. Summary length=%s", len(summary))


def ensure_initialized(
    log_file: Path | None = None,
    stream: bool = True,
    force: bool = False,
    reset_db: bool = False,
) -> None:
    """Ensure that database, PDF source and vector store are ready for tests."""
    global _INITIALIZED

    os.environ.setdefault("MAMA_EMBEDDINGS", "simple")

    if force:
        _INITIALIZED = False

    if _INITIALIZED:
        return

    if log_file is not None:
        setup_logging(log_file, stream=stream)

    ensure_database(reset_to_dummy=reset_db)
    logging.info("Database initialized")
    prepare_pdf_source()
    prepare_vector_store()

    _INITIALIZED = True


def ask_question(question: str, chat_history_len: int = 5) -> Dict[str, Any]:
    """Query the sample knowledge base with the provided question."""
    ensure_initialized()
    sanitized = question.strip()
    if not sanitized:
        raise ValueError("La domanda non può essere vuota")
    return get_response(USER_ID, KB_ID, sanitized, str(KB_ROOT), chat_history_len)


__all__ = [
    "LOGS_DIR",
    "PDF_SRC_DIR",
    "KB_ROOT",
    "DB_PATH",
    "KB_ID",
    "USER_ID",
    "PROMPT_TEMPLATE",
    "DEFAULT_PDF_TEXT",
    "ensure_initialized",
    "ask_question",
]
