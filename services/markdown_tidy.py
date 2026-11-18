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


_VEC_BRACED = re.compile(r'\\vec\s*\{([^{}]+)\}')
_VEC_BARE = re.compile(r"\\vec\s*([A-Z](?:_?\d|')*[A-Z][A-Z0-9_']*)")
_ANGLE_BRACED = re.compile(r'\\hat\s*\{([^{}]+)\}')


def _many_letters(body):
    return len(re.findall(r'[A-Za-z]', body)) >= 2


def geometry_notation(tex):
    """Trong thân công thức: mũi tên vectơ và ký hiệu góc phủ hết tên (owner, lỗi tái phát 18/11/2026).

    \\vec{AB} → \\overrightarrow{AB}; \\hat{xOy} → \\widehat{xOy}. Vectơ một chữ (\\vec{u}) giữ nguyên.
    Lỗi cũ: bản vá trong _legacy_sanitize_katex_latex không chạm được công thức vì lớp bảo toàn $...$.
    """
    s = str(tex or '')
    if '\\vec' not in s and '\\hat' not in s:
        return s
    s = _VEC_BRACED.sub(lambda m: (r'\overrightarrow{' + m.group(1) + '}') if _many_letters(m.group(1)) else m.group(0), s)
    s = _VEC_BARE.sub(lambda m: r'\overrightarrow{' + m.group(1) + '}', s)
    s = _ANGLE_BRACED.sub(lambda m: (r'\widehat{' + m.group(1) + '}') if _many_letters(m.group(1)) else m.group(0), s)
    return s


def geometry_notation_in_text(text):
    """Áp geometry_notation cho mọi đoạn $...$/$$...$$ trong văn bản; ngoài công thức và khối mã giữ nguyên."""
    if not text or '$' not in str(text):
        return text
    pieces = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`)', str(text))
    for i in range(0, len(pieces), 2):
        pieces[i] = _MATH.sub(lambda m: geometry_notation(m.group(0)), pieces[i])
    return ''.join(pieces)


def geometry_notation_deep(value):
    """Đi qua dict/list (đề, câu hỏi JSON) và chuẩn hóa mọi chuỗi."""
    if isinstance(value, str):
        return geometry_notation_in_text(value)
    if isinstance(value, list):
        return [geometry_notation_deep(v) for v in value]
    if isinstance(value, dict):
        return {k: geometry_notation_deep(v) for k, v in value.items()}
    return value


def geometry_notation_inplace(value):
    """Như geometry_notation_deep nhưng sửa ngay trong dict/list (giữ nguyên đối tượng đề đang dùng)."""
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = geometry_notation_inplace(v) if isinstance(v, (dict, list)) else geometry_notation_deep(v)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            value[i] = geometry_notation_inplace(v) if isinstance(v, (dict, list)) else geometry_notation_deep(v)
    return value


_MATH = re.compile(r'(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)')
_PROTECTED = re.compile(r'(\\(?:text|mathrm|textbf|mbox|operatorname)\s*\{[^{}]*\})')
_VI_MARKED = 'À-ÃÈ-ÊÌÍÒ-ÕÙÚÝà-ãè-êìíò-õùúýĂăĐđĨĩŨũƠơƯưẠ-ỹ'
_VI_LETTER = 'A-Za-z' + _VI_MARKED
# Một từ có dấu tiếng Việt, kèm các từ chữ cái liền sau (vd "thỏa mãn", "loại").
_VI_RUN = re.compile('(?<![\\\\' + _VI_LETTER + '])'
                     '([' + _VI_LETTER + ']*[' + _VI_MARKED + '][' + _VI_LETTER + ']*'
                     '(?:[ \t]+[' + _VI_LETTER + ']{2,})*)')


def wrap_vietnamese_in_math(text):
    """Chữ Việt có dấu nằm trong công thức ($...$) được bọc \\text{} để KaTeX không vỡ chữ.

    Ca thật 17/11/2026 (Trạm 1): "$x=3$ (thỏa mãn)" viết trong math hiện thành "m a ˜ n".
    """
    if not text or '$' not in str(text):
        return text

    def fix_math(match):
        segment = geometry_notation(match.group(0))
        parts = _PROTECTED.split(segment)
        for i in range(0, len(parts), 2):
            parts[i] = _VI_RUN.sub(lambda m: r'\text{' + m.group(1) + '}', parts[i])
        return ''.join(parts)

    pieces = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~)', str(text))
    for i in range(0, len(pieces), 2):
        pieces[i] = _MATH.sub(fix_math, pieces[i])
    return ''.join(pieces)
