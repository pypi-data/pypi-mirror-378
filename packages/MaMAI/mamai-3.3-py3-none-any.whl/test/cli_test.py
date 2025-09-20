#!/usr/bin/env python3
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from test import helpers


def main() -> None:
    log_file = helpers.LOGS_DIR / "test.log"
    reset_db = os.environ.get("MAMA_RESET_DB", "1") == "1"
    helpers.ensure_initialized(log_file=log_file, stream=True, force=True, reset_db=reset_db)

    question = "Qual è l'argomento del documento?"
    result = helpers.ask_question(question, chat_history_len=5)
    logging.info("Prompt completed")
    logging.info("Answer: %s", result.get("answer", ""))
    logging.info("Documents returned: %s", len(result.get("documents", [])))

    print("TEST OK: ingestion and prompting completed.")


if __name__ == "__main__":
    main()
