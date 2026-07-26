from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Project root:
# RAG_document_qa/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Log location:
# RAG_document_qa/logs/app.log
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)


def configure_logging() -> None:
    formatter = logging.Formatter(LOG_FORMAT)

    # Shows logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Saves logs inside project
    # Maximum 5 MB per log file, with 3 backup files
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Prevent duplicate handlers when --reload restarts the app
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Hide unnecessary third-party INFO logs
    noisy_loggers = [
        "watchfiles",
        "watchfiles.main",
        "uvicorn.access",
        "httpx",
        "httpcore",
        "huggingface_hub",
        "sentence_transformers",
        "transformers",
        "urllib3",
        "openai",
        "multipart",
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "LOGGER_CONFIGURED | log_file=%s",
        LOG_FILE,
    )