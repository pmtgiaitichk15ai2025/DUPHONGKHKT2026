# -*- coding: utf-8 -*-
"""Kiểu phiếu "Infographic Sen Việt" (owner 19/11/2026): hoa sen, lá sen màu nước vẽ bằng SVG vector,
khung từ vựng Anh–Việt chuyên ngành trên lá sen ở cuối mỗi phần lớn của bài.

Ý tưởng bố cục học từ mẫu anh Nguyễn Chính Em chia sẻ cộng đồng; hình và mã viết mới.
Hình trang trí đặt ở lề, không che chữ/BBT; đồ thị giữ nền trong suốt (docs/AI_BBT_GRAPH_INFOGRAPHIC_PROMPT.txt).
"""
import html
import math
import re
from urllib.parse import quote

from services.subject_glossary import terms_in


def _petal(angle, rx, ry, fill, op):
    return (f"<ellipse cx='60' cy='{78 - ry}' rx='{rx}' ry='{ry}' fill='{fill}' opacity='{op}' "
            f"transform='rotate({angle} 60 78)'/>")


def lotus_svg(scale=1.0):
    petals = "".join(_petal(a, 9, 30, "url(#p)", .9) for a in (-62, -38, 38, 62))
    petals += "".join(_petal(a, 10, 34, "url(#p2)", .95) for a in (-18, 18))
    petals += _petal(0, 11, 38, "url(#p2)", 1)
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 100'>"
            "<defs><linearGradient id='p' x1='0' y1='1' x2='0' y2='0'><stop offset='0' stop-color='#f9c6d3'/>"
            "<stop offset='1' stop-color='#e05a86'/></linearGradient>"
            "<linearGradient id='p2' x1='0' y1='1' x2='0' y2='0'><stop offset='0' stop-color='#fde2ea'/>"
            "<stop offset='1' stop-color='#ec6f98'/></linearGradient></defs>"
            "<path d='M8 86 Q60 70 112 86 Q60 100 8 86Z' fill='#5fa36a' opacity='.75'/>"
            + petals +
            "<circle cx='60' cy='76' r='5' fill='#f2c14e'/></svg>")


def leaf_svg():
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 120' preserveAspectRatio='none'>"
            "<path d='M100 60 L100 2 A98 58 0 1 1 92 2 Z' fill='#7fbf7f' opacity='.30'/>"
            "<g stroke='#4f8f5a' stroke-width='.8' opacity='.35' fill='none'>"
            + "".join(f"<path d='M100 60 L{100 + 96 * math.cos(t)} {60 + 56 * math.sin(t)}'/>"
                      for t in [i * 0.52 for i in range(12)]) +
            "</g></svg>")


def _uri(svg):
    return "url(\"data:image/svg+xml," + quote(svg) + "\")"


def pond_svg():
    """Dải hồ sen mờ (độ mờ 0,12 theo mẫu) đặt dưới chữ."""
    flowers = "".join(
        f"<g transform='translate({x} {y}) scale({k})'>" + lotus_svg().split("</defs>", 1)[1].replace("</svg>", "") + "</g>"
        for x, y, k in ((10, 40, .9), (170, 55, .7), (330, 35, 1.0), (500, 60, .65)))
    defs = lotus_svg().split("</defs>", 1)[0].split("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 100'>", 1)[1] + "</defs>"
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 160' preserveAspectRatio='xMidYMax slice'>"
            + defs + "<g opacity='.12'>"
            "<rect x='0' y='120' width='640' height='40' fill='#9cc9d8'/>"
            "<ellipse cx='90' cy='130' rx='70' ry='14' fill='#39866D'/><ellipse cx='420' cy='138' rx='90' ry='16' fill='#39866D'/>"
            "<circle cx='260' cy='126' r='3' fill='#9cc9d8'/><circle cx='560' cy='130' r='2.5' fill='#9cc9d8'/>"
            + flowers + "</g></svg>")


def lotus_css():
    """Vở ghi tay song ngữ – hoa sen Việt: kế thừa giấy ô ly + gáy lò xo của kiểu chữ viết tay.

    Quy tắc .handwritten nằm sau trong <style>, nên mọi quy tắc ở đây dùng .handwritten.lotus để thắng.
    """
    return _lotus_rules().replace(".lotus ", ".handwritten.lotus ")


def _lotus_rules():
    flower, leaf, pond = _uri(lotus_svg()), _uri(leaf_svg()), _uri(pond_svg())
    return (
        # Lề đỏ nhạt + nền ô ly trắng ngà (giữ lớp ô ly của .handwritten), hồ sen mờ dưới chữ.
        ".lotus .paper{background-color:#fbf8ef;background-image:linear-gradient(90deg,transparent 64px,#e8a0a8 64px,#e8a0a8 65.5px,transparent 65.5px),"
        "linear-gradient(#aea18a2a 1px,transparent 1px),linear-gradient(90deg,#aea18a2a 1px,transparent 1px);"
        "background-size:100% 100%,24px 24px,24px 24px;print-color-adjust:exact;-webkit-print-color-adjust:exact}"
        f".lotus .pond{{position:absolute;left:0;right:0;bottom:0;height:200px;background:{pond} no-repeat bottom/100% auto;pointer-events:none;z-index:0}}"
        f".lotus .corner-lotus{{position:absolute;top:10px;right:12px;width:96px;height:80px;background:{flower} no-repeat center/contain;pointer-events:none}}"
        ".lotus article,.lotus .notebook-header{position:relative;z-index:1}"
        ".lotus article{color:#174B9A}.lotus .katex{color:#C32746}"
        ".lotus .notebook-heading h1,.lotus article h1,.lotus article h2,.lotus article h3,.lotus article h4{color:#075B9A;text-decoration-color:#39866D}"
        ".lotus .notebook-header{border-bottom-color:#39866D}.lotus .notebook-identity span{border-bottom-color:#39866D}"
        ".lotus article strong{background:linear-gradient(transparent 62%,#F4B94266 62%)}"
        ".lotus article li::marker{color:#EC89A8}"
        # Tiếng Anh: nghiêng, nhỏ hơn tiếng Việt, xám xanh.
        ".lotus .en{display:block;font:italic 400 .62em/1.35 'Be Vietnam Pro','Segoe UI',Arial,sans-serif;color:#54758C;margin:.1em 0 .35em}"
        ".lotus h1 .en,.lotus h2 .en,.lotus h3 .en,.lotus h4 .en{font-size:.6em;font-weight:600;text-decoration:none}"
        ".lotus .en .katex{color:#54758C}.lotus .en-missing{display:block;font:italic 12px Arial,sans-serif;color:#9a6b2f}"
        # Đồ thị theo mẫu: đường cong xanh liền, tiệm cận đỏ nét đứt, trục đen, điểm đặc biệt đỏ.
        ".lotus .verified-function-visuals polyline{stroke:#1d4ed8}"
        ".lotus .verified-function-visuals g[data-asymptote] line{stroke:#dc2626}"
        ".lotus .verified-function-visuals circle[data-point]{fill:#dc2626;stroke:#dc2626}"
        f".lotus .vocab-leaf{{margin:18px auto 22px;max-width:620px;padding:16px 26px 14px;border-radius:50% / 34%;"
        f"background:{leaf} no-repeat center/100% 100%,#e6f2ea;border:1.5px solid #39866D;break-inside:avoid;position:relative;z-index:1}}"
        ".lotus .vocab-leaf h5{margin:0 0 8px;text-align:center;color:#2f6b3c;font:700 13px/1.3 Arial,sans-serif;letter-spacing:.06em}"
        ".lotus .vocab-leaf ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:4px 20px}"
        ".lotus .vocab-leaf li{font:14px/1.4 Arial,sans-serif;color:#1f3d2a}.lotus .vocab-leaf li b{color:#075B9A;font-weight:700}"
        ".vocab-leaf,.pond,.corner-lotus,.page-lotus,.translation-note{display:none}.lotus .vocab-leaf,.lotus .pond,.lotus .corner-lotus{display:block}"
        ".lotus .translation-note{display:block;font:12px/1.4 Arial,sans-serif;color:#54758C;margin-top:10px}"
        "@media(max-width:600px){.lotus .corner-lotus{width:60px;height:50px}.lotus .vocab-leaf ul{grid-template-columns:1fr}}"
        # In: hoa sen + hồ sen lặp lại mọi tờ (position:fixed), số trang "Trang x/y".
        "@page{@bottom-center{content:'Trang ' counter(page) '/' counter(pages);font:11px Arial,sans-serif;color:#54758C}}"
        f"@media print{{.lotus .pond,.lotus .corner-lotus{{display:none}}"
        f".lotus .page-lotus{{display:block;position:fixed;pointer-events:none}}"
        f".lotus .page-lotus.tr{{top:0;right:0;width:24mm;height:20mm;background:{flower} no-repeat center/contain}}"
        f".lotus .page-lotus.pond-print{{bottom:0;left:0;right:0;height:34mm;background:{pond} no-repeat bottom/100% auto}}}}"
    )


def _plain(fragment):
    text = re.sub(r'data-tex="([^"]*)"', lambda m: " " + html.unescape(m.group(1)) + " ", fragment)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


_EN_TITLE = {"Toán học": "MATHEMATICAL VOCABULARY", "Vật lý": "PHYSICS VOCABULARY", "Hóa học": "CHEMISTRY VOCABULARY",
             "Sinh học": "BIOLOGY VOCABULARY", "Tin học": "COMPUTING VOCABULARY", "Khoa học tự nhiên": "SCIENCE VOCABULARY",
             "Lịch sử": "HISTORY VOCABULARY", "Địa lý": "GEOGRAPHY VOCABULARY"}


def vocab_box(terms, subject):
    title_vi = "TỪ VỰNG " + html.escape(subject.upper())
    title_en = _EN_TITLE.get(subject, "SUBJECT VOCABULARY")
    items = "".join(f"<li><b>{html.escape(en)}</b> – {html.escape(vi)}</li>" for vi, en in terms)
    return (f'<aside class="vocab-leaf" aria-label="Từ vựng Anh–Việt"><h5>{title_vi} · {title_en}</h5>'
            f"<ul>{items}</ul></aside>")


PAGE_LOTUS = ('<div class="pond" aria-hidden="true"></div><div class="corner-lotus" aria-hidden="true"></div>'
              '<div class="page-lotus tr" aria-hidden="true"></div><div class="page-lotus pond-print" aria-hidden="true"></div>')


def with_vocabulary(body, subject, grade, per_box=5):
    """Chèn khung từ vựng cuối mỗi phần lớn (trước mỗi <h2> kế tiếp và cuối bài).

    Trình duyệt không biết chỗ ngắt trang giấy nên khung đặt theo phần nội dung, không theo tờ.
    Không lặp lại thuật ngữ đã in ở khung trước. Không có thuật ngữ đã duyệt → không chèn.
    """
    parts = re.split(r"(?=<h2\b)", body)
    if len(parts) == 1:
        parts = re.split(r"(?=<h3\b)", body)
    seen, out = set(), []
    for part in parts:
        picked = [t for t in terms_in(_plain(part), subject, grade, limit=50) if t[0] not in seen][:per_box]
        seen.update(vi for vi, _ in picked)
        out.append(part + (vocab_box(picked, subject) if picked else ""))
    return PAGE_LOTUS + "".join(out)


def illustration_prompt(subject, grade, topic, lesson):
    """Prompt tranh minh họa cho AI vẽ ảnh miễn phí (hướng A thu gọn, owner 19/11/2026).

    Chỉ xin TRANH (hồ sen, bối cảnh thực tế theo từng phần bài); tuyệt đối không xin chữ, công thức,
    đồ thị, số liệu — những thứ AI vẽ ảnh làm sai. Nội dung lấy đúng đề mục của bài đang mở, không bịa.
    """
    import json as _json
    from services.text_boundaries import student_essay_text
    heads = [re.sub(r"[*_`#$\\]", "", h).strip()
             for h in re.findall(r"(?m)^#{2,4}\s+(.+)$", student_essay_text(str(lesson or "")))]
    heads = [h for h in heads if h and not re.match(r"(?i)PHẦN\s*\d", h)][:8]
    scenes = [{"scene": i + 1, "based_on_section": h,
               "draw": "Tranh minh họa nghệ thuật bối cảnh thực tế gợi đúng nội dung phần này; không chữ, không số."}
              for i, h in enumerate(heads)]
    doc = {
        "purpose": "Tranh minh họa cho phiếu học tập 'Vở ghi tay song ngữ – Hoa sen Việt'. Chữ, công thức, đồ thị do ứng dụng Gia Sư AI dựng chính xác riêng.",
        "lesson": {"subject": subject, "grade": grade, "topic": str(topic or "")},
        "style": "Vietnamese lotus pond botanical watercolor combined with soft cinematic realistic illustration",
        "palette": {"lotus_pink": "#EC89A8", "lotus_green": "#39866D", "paper": "#fbf8ef", "accent": "#F4B942"},
        "dominant_elements": ["Hoa sen hồng", "Lá sen xanh", "Búp sen", "Đài sen", "Giọt sương", "Mặt nước"],
        "aspect_ratio": "3:4 (A4 dọc)",
        "scenes": scenes,
        "hard_rules": [
            "TUYỆT ĐỐI KHÔNG vẽ chữ, chữ số, công thức, đồ thị, bảng hay ký hiệu toán học.",
            "Không bịa thông số kỹ thuật, số liệu hay nhãn mác.",
            "Chừa khoảng trống sáng ở giữa ảnh để đặt nội dung bài học.",
            "Hoa sen và lá sen hiện diện trong mọi tranh.",
        ],
    }
    return _json.dumps(doc, ensure_ascii=False, indent=2)
