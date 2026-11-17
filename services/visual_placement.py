# -*- coding: utf-8 -*-
"""Đặt hình/bảng đúng chỗ trong thân câu hỏi.

Câu dạng "…có bảng biến thiên:\n\n\nSố nghiệm…" đã được tách bảng ra trường riêng,
để lại chỗ trống. Bảng/hình phải hiện ngay sau phần dẫn ("…bảng biến thiên:"),
trước câu hỏi, đúng thứ tự đọc của đề in.
"""
import re

_LEAD_IN = re.compile(
    r"(?is)^(?P<before>.*?(?:bảng\s+biến\s+thiên|bảng\s+xét\s+dấu|đồ\s+thị|hình\s+vẽ|hình\s+bên|bảng\s+sau|bảng\s+số\s+liệu)[^:\n]{0,80}:)"
    r"[ \t]*\n\s*\n\s*(?P<after>\S.*)$"
)


def split_stem_at_visual(text):
    """Trả (phần dẫn, phần sau hình). Không có chỗ trống sau câu dẫn thì trả (text, "")."""
    value = str(text or "")
    match = _LEAD_IN.match(value)
    if not match:
        return value, ""
    return match.group("before").rstrip(), match.group("after").strip()
