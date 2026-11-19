# -*- coding: utf-8 -*-
"""Từ vựng Anh–Việt chuyên ngành cho phiếu bài học (owner 19/11/2026).

Chỉ đọc bảng thuật ngữ đã đối chiếu trong data/subject_glossary (≥2 nguồn độc lập khớp, hoặc chủ dự án
duyệt). Không dịch tự động, không gọi AI: thuật ngữ không có trong bảng thì không in, kể cả khi trang
còn trống chỗ. Môn/lớp chưa có bảng → trả rỗng.
"""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).resolve().parents[1] / "data" / "subject_glossary"
APPROVED = {"dat_2_nguon", "chu_du_an_duyet"}


def _norm(text):
    text = unicodedata.normalize("NFC", str(text or "")).casefold()
    text = text.replace("lý", "lí").replace("hoá", "hóa").replace("toạ", "tọa")
    return re.sub(r"\s+", " ", text)


@lru_cache(maxsize=32)
def approved_terms(subject, grade):
    try:
        index = json.loads((_DIR / "index.json").read_text(encoding="utf-8"))
        name = index.get(subject, {}).get(str(grade))
        if not name:
            return ()
        doc = json.loads((_DIR / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    terms = [(t["vi"], t["en"]) for t in doc.get("terms", [])
             if t.get("status") in APPROVED and t.get("vi") and t.get("en")]
    return tuple(sorted(terms, key=lambda t: -len(t[0])))   # cụm dài trước: "tiệm cận đứng" trước "tiệm cận"


def terms_in(text, subject, grade, limit=5):
    """Thuật ngữ đã duyệt xuất hiện trong đoạn văn, theo thứ tự xuất hiện, tối đa `limit`."""
    hay = _norm(text)
    found = []
    taken = []
    for vi, en in approved_terms(subject, grade):
        m = re.search(r"(?<!\w)" + re.escape(_norm(vi)) + r"(?!\w)", hay)
        if not m or any(a <= m.start() < b for a, b in taken):
            continue
        taken.append((m.start(), m.end()))
        found.append((m.start(), vi, en))
    found.sort()
    return [(vi, en) for _, vi, en in found[:limit]]


@lru_cache(maxsize=32)
def known_issues(subject, grade):
    """Tồn tại đã ghi của bảng thuật ngữ môn/lớp (hiện trên phiếu, vá theo phản hồi người dùng)."""
    try:
        index = json.loads((_DIR / "index.json").read_text(encoding="utf-8"))
        name = index.get(subject, {}).get(str(grade))
        return tuple(json.loads((_DIR / name).read_text(encoding="utf-8")).get("known_issues", ())) if name else ()
    except (OSError, ValueError):
        return ()
