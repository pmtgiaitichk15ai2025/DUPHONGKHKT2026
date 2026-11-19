# -*- coding: utf-8 -*-
"""Học liệu tiếng Anh uy tín theo chủ đề bài (owner 19/11/2026), đặt cạnh gợi ý video Trạm 1.

Chỉ dùng ĐƯỜNG TÌM KIẾM CHÍNH THỨC của từng trang (không bịa đường dẫn bài cụ thể, không gọi AI).
Từ khóa tiếng Anh lấy theo thứ tự tin cậy: bản dịch tên bài đã có (lượt song ngữ) → thuật ngữ trong bảng
đã duyệt xuất hiện trong tên bài/bài học → tên môn tiếng Anh + tên bài gốc (ghi rõ là từ khóa tạm).
Kết quả là trang tìm kiếm, không phải học liệu đã được thẩm định theo CT2018/KNTT.
"""
import html
from urllib.parse import quote_plus

from services.subject_glossary import terms_in

SUBJECT_EN = {
    "Toán học": "mathematics", "Vật lý": "physics", "Hóa học": "chemistry", "Sinh học": "biology",
    "Khoa học tự nhiên": "science", "Tin học": "computer science", "Công nghệ": "technology",
    "Lịch sử": "history", "Địa lý": "geography", "Lịch sử & Địa lý": "history geography",
    "Giáo dục kinh tế và pháp luật": "economics", "Giáo dục công dân": "civics",
    "Ngữ văn": "literature", "Tiếng Anh": "English",
}

_SITES = {
    "khan": ("Khan Academy", "https://www.khanacademy.org/search?page_search_query="),
    "bitesize": ("BBC Bitesize", "https://www.bbc.co.uk/bitesize/search?q="),
    "ck12": ("CK-12", "https://www.ck12.org/search/?q="),
    "wiki": ("Wikipedia (English)", "https://en.wikipedia.org/w/index.php?search="),
    "yt": ("Video tiếng Anh (YouTube)", "https://www.youtube.com/results?search_query="),
}

_BY_SUBJECT = {
    "Toán học": ("khan", "bitesize", "ck12", "yt"),
    "Vật lý": ("khan", "ck12", "bitesize", "yt"),
    "Hóa học": ("khan", "ck12", "bitesize", "yt"),
    "Sinh học": ("khan", "ck12", "bitesize", "yt"),
    "Khoa học tự nhiên": ("khan", "ck12", "bitesize", "yt"),
    "Tin học": ("khan", "bitesize", "wiki", "yt"),
    "Công nghệ": ("bitesize", "ck12", "wiki", "yt"),
    "Lịch sử": ("bitesize", "khan", "wiki", "yt"),
    "Địa lý": ("bitesize", "wiki", "yt"),
    "Lịch sử & Địa lý": ("bitesize", "wiki", "yt"),
    "Giáo dục kinh tế và pháp luật": ("khan", "bitesize", "wiki", "yt"),
    "Giáo dục công dân": ("bitesize", "wiki", "yt"),
    "Ngữ văn": ("bitesize", "wiki", "yt"),
    "Tiếng Anh": ("bitesize", "yt"),
}


def english_keywords(subject, grade, topic, lesson="", title_en=""):
    """(từ khóa, nguồn từ khóa) — nguồn: 'translation' | 'glossary' | 'fallback'."""
    if str(title_en or "").strip():
        return str(title_en).strip(), "translation"
    found = terms_in(str(topic or ""), subject, grade, limit=3) or terms_in(str(lesson or "")[:3000], subject, grade, limit=3)
    if found:
        return " ".join(en for _, en in found[:3]), "glossary"
    return f"{SUBJECT_EN.get(subject, '')} {topic}".strip(), "fallback"


def english_resources(subject, grade, topic, lesson="", title_en=""):
    keywords, how = english_keywords(subject, grade, topic, lesson, title_en)
    links = []
    for key in _BY_SUBJECT.get(subject, ("khan", "bitesize", "wiki", "yt")):
        name, base = _SITES[key]
        q = f"{keywords} lesson" if key == "yt" else keywords
        links.append((name, base + quote_plus(q)))
    return {"keywords": keywords, "source": how, "links": links}


def english_resources_html(subject, grade, topic, lesson="", title_en=""):
    data = english_resources(subject, grade, topic, lesson, title_en)
    note = {"translation": "từ khóa theo bản dịch tên bài",
            "glossary": "từ khóa theo bảng thuật ngữ đã đối chiếu",
            "fallback": "từ khóa tạm (chưa có bản dịch/thuật ngữ) — nên bấm Tạo bản song ngữ để có từ khóa chuẩn"}[data["source"]]
    links = " · ".join(f'<a href="{html.escape(u, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(n)}</a>'
                       for n, u in data["links"])
    return (f'<div class="lesson-reference"><b>🌐 Học liệu tiếng Anh theo chủ đề</b> — <i>{html.escape(data["keywords"])}</i>'
            f'<p>{links}</p><p style="font-size:.85em">{html.escape(note)}. Đây là trang tìm kiếm của các nguồn giáo dục uy tín, '
            'không phải học liệu đã thẩm định theo CT2018/KNTT; thầy cô chọn nội dung phù hợp.</p></div>')
