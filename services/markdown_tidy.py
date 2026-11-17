# -*- coding: utf-8 -*-
"""Gỡ dấu gạch đầu dòng/dấu * mồ côi do AI sinh (ca thật 17/11/2026, Trạm 1 Toán 7).

AI hay viết "*   *" trên một dòng rồi "**Bước 1:** * Xét...", hiện thành "• *" và "Bước 1: *".
Chỉ gỡ dấu * đứng một mình (có khoảng trắng hai bên), không đụng **đậm**, *nghiêng* hay công thức.
"""
import re

_FENCE = re.compile(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|\$\$[\s\S]*?\$\$|\$[^$\n]*\$)')
_EMPTY_BULLET = re.compile(r'^[ \t]*(?:[*+\-•][ \t]*)+\*?[ \t]*$', re.M)
_LABEL_STAR = re.compile(r'(\*\*[^*\n]{1,40}:\*\*|\*\*[^*\n]{1,40}\*\*:)[ \t]+\*[ \t]+(?=\S)')
_BULLET_STAR = re.compile(r'^([ \t]*[*+\-][ \t]+)\*[ \t]+(?=[^*\s])', re.M)


def tidy_stray_bullets(text):
    if not text:
        return text
    parts = _FENCE.split(str(text))
    for i in range(0, len(parts), 2):
        part = _EMPTY_BULLET.sub('', parts[i])
        part = _LABEL_STAR.sub(r'\1 ', part)
        part = _BULLET_STAR.sub(r'\1', part)
        parts[i] = re.sub(r'\n{3,}', '\n\n', part)
    return ''.join(parts)
