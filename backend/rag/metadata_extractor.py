from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from backend.rag.llm import get_llm


def clean_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


def normalize_quarter(value: Any) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip().upper()

    if value in {"Q1", "1", "FIRST", "FIRST QUARTER"}:
        return "Q1"
    if value in {"Q2", "2", "SECOND", "SECOND QUARTER"}:
        return "Q2"
    if value in {"Q3", "3", "THIRD", "THIRD QUARTER"}:
        return "Q3"
    if value in {"Q4", "4", "FOURTH", "FOURTH QUARTER"}:
        return "Q4"

    return None


def infer_quarter_rule_based(text: str, filename: str) -> Optional[str]:
    filename_lower = filename.lower()
    text_lower = re.sub(r"\s+", " ", text.lower())

    if re.search(r"\bq1\b|_q1_|-q1-", filename_lower):
        return "Q1"
    if re.search(r"\bq2\b|_q2_|-q2-", filename_lower):
        return "Q2"
    if re.search(r"\bq3\b|_q3_|-q3-", filename_lower):
        return "Q3"
    if re.search(r"\bq4\b|_q4_|-q4-", filename_lower):
        return "Q4"

    if re.search(r"three\s+months\s+ended", text_lower):
        return "Q1"
    if re.search(r"six\s+months\s+ended", text_lower):
        return "Q2"
    if re.search(r"nine\s+months\s+ended", text_lower):
        return "Q3"

    return None


def infer_year_rule_based(text: str, filename: str) -> Optional[int]:
    filename_lower = filename.lower()

    filename_year = re.search(r"\b(20\d{2})\b", filename_lower)
    if filename_year:
        return int(filename_year.group(1))

    sample = re.sub(r"\s+", " ", text[:12000])

    period_year = re.search(
        r"(quarterly|annual)\s+period\s+ended\s+[A-Za-z]+\s+\d{1,2},\s+(20\d{2})",
        sample,
        re.IGNORECASE,
    )
    if period_year:
        return int(period_year.group(2))

    text_year = re.search(r"\b(20\d{2})\b", sample[:4000])
    if text_year:
        return int(text_year.group(1))

    return None


def ensure_year_is_int(value: Any) -> Optional[int]:
    """Convert year value to int, handling string and numeric inputs."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def extract_document_metadata(text: str, filename: str) -> Dict[str, Any]:
    sample = text[:12000]

    fallback = {
        "company": None,
        "ticker": None,
        "year": infer_year_rule_based(sample, filename),
        "quarter": infer_quarter_rule_based(sample, filename),
        "document_type_label": None,
        "report_title": None,
        "source_file": filename,
    }

    prompt = f"""
You are a strict SEC filing metadata extractor.

Read the filename and the first pages of the document.
Return ONLY valid JSON.

Required JSON keys:
{{
  "company": null,
  "ticker": null,
  "year": null,
  "quarter": null,
  "document_type_label": null,
  "report_title": null
}}

Important rules:
- company must be the actual registrant company, not SEC, not UNITED STATES, not government header.
- If the file is a SEC 10-Q, quarter must be fiscal quarter:
  - "three months ended" means Q1
  - "six months ended" means Q2
  - "nine months ended" means Q3
- Do NOT infer quarter only from calendar month.
- Example: NVIDIA period ended April can still be Q1.
- year should be the report period year.
- document_type_label should be 10-Q, 10-K, Annual Report, Quarterly Report, or PDF.
- ticker must be the official stock ticker symbol if clearly identifiable.
- NVIDIA Corporation -> NVDA
- Apple Inc. -> AAPL
- If uncertain, return null.
- Return JSON only. No explanation.

Filename:
{filename}

Document text:
{sample}
"""

    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        data = json.loads(clean_json_text(raw))

        rule_quarter = infer_quarter_rule_based(sample, filename)
        rule_year = infer_year_rule_based(sample, filename)

        return {
            "source_file": filename,
            "company": data.get("company"),
            "ticker": data.get("ticker"),
            "year": ensure_year_is_int(data.get("year")) or rule_year,
            "quarter": normalize_quarter(data.get("quarter")) or rule_quarter,
            "document_type_label": data.get("document_type_label"),
            "report_title": data.get("report_title"),
        }

    except Exception:
        return fallback