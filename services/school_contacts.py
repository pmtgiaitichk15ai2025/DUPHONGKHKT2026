# -*- coding: utf-8 -*-
"""Danh bạ hỗ trợ của trường cho khung an toàn Trạm 4 (owner duyệt 19/11/2026).

Số điện thoại KHÔNG nằm trong mã/GitHub: đọc từ Streamlit Secrets `SCHOOL_SUPPORT_CONTACTS`, ví dụ:

    [[SCHOOL_SUPPORT_CONTACTS]]
    name = "Phan Minh Trí"
    role = "Thầy tư vấn học đường"
    phone = "09xx xxx xxx"
    hours = "Giờ hành chính"

Người được học sinh nhắc tên trong lời kể (ví dụ người bị kể là gây hại) bị ẩn khỏi danh bạ của lượt đó,
để em không bao giờ bị hướng tới gọi đúng người em đang sợ. Chủ dự án tự hỏi ý từng người trước khi công khai số.
"""
import re
import unicodedata


def _fold(text):
    text = unicodedata.normalize("NFD", str(text or "")).casefold()
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def _mentioned(contact, message):
    """Học sinh có nhắc tới người này không: tên đầy đủ, hoặc 'thầy/cô/anh/chị + tên gọi'."""
    msg = " " + re.sub(r"\s+", " ", _fold(message)) + " "
    name = _fold(contact.get("name", "")).strip()
    if not name:
        return False
    if f" {name} " in msg:
        return True
    given = name.split()[-1]
    return bool(re.search(r"\b(thay|co|anh|chi|ong|ba)\s+" + re.escape(given) + r"\b", msg))


def normalize_contacts(raw):
    out = []
    for item in raw or []:
        try:
            item = dict(item)
        except (TypeError, ValueError):
            continue
        name, phone = str(item.get("name") or "").strip(), str(item.get("phone") or "").strip()
        if name and phone:
            out.append({"name": name, "role": str(item.get("role") or "").strip(),
                        "phone": phone, "hours": str(item.get("hours") or "").strip()})
    return out


def school_contacts_md(raw, message=""):
    """Khối Markdown "Người hỗ trợ ở trường em"; rỗng nếu chưa cấu hình hoặc mọi người đều bị nhắc tên."""
    shown = [c for c in normalize_contacts(raw) if not _mentioned(c, message)]
    if not shown:
        return ""
    lines = ["### Người hỗ trợ ở trường em"]
    for c in shown:
        who = f"{c['role']} {c['name']}".strip() if c["role"] else c["name"]
        hours = f" ({c['hours']})" if c["hours"] else ""
        lines.append(f"- {who}: **{c['phone']}**{hours}")
    lines.append("- Ngoài giờ trên, em gọi **111** (miễn phí, cả ngày đêm).")
    return "\n".join(lines) + "\n"
