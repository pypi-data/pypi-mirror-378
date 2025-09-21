"""
📄 filetype_utils.py

Purpose:
    Determines supported filetypes and dispatches extraction logic.

Key Features:
    - SUPPORTED_EXTENSIONS(): provides lists of extensions support and can be extended.
    - extract_text_from_file(): Delegates to specific extractors in extract_utils.

Usage:
    Called during file indexing in `indexly.py` or `fts_core.py`.
"""

"""
filetype_utils.py

Central place for supported file types and extraction.
"""

import os
from pathlib import Path
from .extract_utils import (
    _extract_docx,
    extract_image_metadata,
    _extract_msg,
    _extract_eml,
    _extract_html,
    _extract_pdf,
    _extract_xlsx,
    _extract_epub,
    _extract_odt,
    _extract_pptx,
)
from .utils import clean_text

# ✅ Single source of truth
SUPPORTED_EXTENSIONS = {
    ".txt",
    ".json",
    ".md",
    ".xml",
    ".docx",
    ".xlsx",
    ".pdf",
    ".py",
    ".html",
    ".htm",
    ".csv",
    ".log",
    ".js",
    ".css",
    ".msg",
    ".eml",
    ".pptx",
    ".epub",
    ".odt",
    ".jpg",
    ".jpeg",
    ".png",
    ".tiff",
    ".bmp",
}


def extract_text_from_file(file_path):
    """
    Extract text + metadata.
    Returns: (text_content, metadata) or (None, None)
    """
    ext = Path(file_path).suffix.lower()
    raw_text = None
    metadata = None

    if ext not in SUPPORTED_EXTENSIONS:
        return None, None

    try:
        if ext in [".html", ".htm"]:
            raw_text = _extract_html(file_path)

        elif ext in [
            ".txt", ".md", ".json", ".xml", ".py",
            ".csv", ".log", ".js", ".css",
        ]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()

        elif ext == ".docx":
            raw_text = _extract_docx(file_path)
        elif ext == ".xlsx":
            raw_text = _extract_xlsx(file_path)
        elif ext == ".pdf":
            raw_text = _extract_pdf(file_path)
        elif ext == ".pptx":
            raw_text = _extract_pptx(file_path)
        elif ext == ".epub":
            raw_text = _extract_epub(file_path)
        elif ext == ".odt":
            raw_text = _extract_odt(file_path)
        elif ext == ".msg":
            raw_text = _extract_msg(file_path)
        elif ext == ".eml":
            raw_text = _extract_eml(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            metadata = extract_image_metadata(file_path)
        elif ext in [".zip", ".exe", ".bin"]:
            return None, None  # skip binaries

        text_content = clean_text(raw_text) if raw_text else None
        return text_content, metadata

    except Exception as e:
        print(f"⚠️ Error extracting text from {file_path}: {e}")
        return None, None
