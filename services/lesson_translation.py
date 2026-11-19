# -*- coding: utf-8 -*-
"""Bản tiếng Anh cho phiếu "Sen Việt song ngữ" (owner 19/11/2026, chấp thuận thêm 1 lượt AI khi xuất).

Nguyên tắc tuyệt đối cho MỌI model (chính và dự phòng):
- Chỉ dịch chữ. Công thức (token ⟦n⟧), số liệu, đồ thị, BBT không qua AI; hệ thống tự gắn lại bản gốc.
- Thuật ngữ có trong bảng đã duyệt (data/subject_glossary) bắt buộc dùng đúng bản tiếng Anh của bảng.
- Kết quả được kiểm bằng chương trình (không tin AI): mất token công thức → bỏ bản dịch khối đó;
  lệch bảng thuật ngữ → gắn cờ cho giáo viên. Khối thiếu bản dịch vẫn in tiếng Việt, ghi rõ.
Lượt gọi đi qua call_gemini_with_fallback của app: cùng một system instruction cho mọi model dự phòng.
"""
import hashlib
import html
import json
import re

from services.subject_glossary import terms_in

_BLOCK_RE = re.compile(r"<(h[1-4]|p|li)\b([^>]*)>((?:(?!<(?:h[1-6]|p|li|ul|ol|table|section|div)\b)[\s\S])*?)</\1>")
_MATH_RE = re.compile(r'<span class="lesson-math"[^>]*>[\s\S]*?</span>')
_TOKEN_RE = re.compile(r"⟦(\d+)⟧")
BATCH_CHARS = 5000


def block_id(text):
    return hashlib.sha1(re.sub(r"\s+", " ", text).strip().encode("utf-8")).hexdigest()[:16]


def _tokenize(inner):
    maths = []

    def keep(m):
        maths.append(m.group(0))
        return f"⟦{len(maths) - 1}⟧"
    text = _MATH_RE.sub(keep, inner)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return re.sub(r"\s+", " ", text).strip(), maths


def extract_blocks(body_html):
    """[(id, văn bản có token công thức)] cho đề mục/đoạn/mục danh sách có chữ cần dịch."""
    out, seen = [], set()
    for m in _BLOCK_RE.finditer(body_html):
        text, _ = _tokenize(m.group(3))
        if not re.search(r"[A-Za-zÀ-ỹĐđ]{2,}", _TOKEN_RE.sub("", text)):
            continue
        bid = block_id(text)
        if bid not in seen:
            seen.add(bid)
            out.append((bid, text))
    return out


def batches(blocks, limit=BATCH_CHARS):
    """Chia theo phần để bài dài không bị cắt giữa chừng; mỗi lô một lượt gọi."""
    cur, size = [], 0
    for b in blocks:
        if cur and size + len(b[1]) > limit:
            yield cur
            cur, size = [], 0
        cur.append(b)
        size += len(b[1])
    if cur:
        yield cur


def translation_request(batch, subject, grade, topic=""):
    if not bilingual_allowed(subject):
        raise ValueError(SENSITIVE_NOTE)
    glossary = sorted({pair for _, t in batch for pair in terms_in(t, subject, grade, limit=50)})
    # Neo đúng hệ căn cứ dùng chung của lượt sinh bài (CT2018 + sửa đổi còn hiệu lực, trục KNTT, văn bản
    # pháp quy theo ngày áp dụng, hồ sơ môn/lớp) — không tạo bộ căn cứ thứ hai cho lượt dịch.
    from services.curriculum_policy import policy_prompt
    system = policy_prompt(subject, grade, 1, topic) + "\n[NHIỆM VỤ LƯỢT NÀY: CHỈ DỊCH SONG NGỮ, KHÔNG SOẠN BÀI]\n" + (
        f"Bạn là biên dịch viên giáo dục chuyên ngành {subject} lớp {grade} (chương trình GDPT 2018, Việt Nam).\n"
        "Dịch từng đoạn tiếng Việt sang tiếng Anh học thuật chuẩn của môn học, chính tả Anh (British English).\n"
        "QUY TẮC TUYỆT ĐỐI (mọi model, kể cả model dự phòng):\n"
        "1. Giữ nguyên mọi ký hiệu ⟦số⟧ đúng số lượng, đúng số thứ tự; đó là công thức, không dịch, không sửa.\n"
        "2. Không thêm, bớt, giải thích hay sửa nội dung, số liệu, đơn vị, đáp án.\n"
        "3. Thuật ngữ có trong BẢNG THUẬT NGỮ phải dùng đúng bản tiếng Anh của bảng; không dùng từ thông dụng khác.\n"
        "4. Không dịch theo nghĩa đời thường khi từ có nghĩa chuyên ngành.\n"
        "5. Giữ đúng cách gọi khái niệm theo CT GDPT 2018 và sách KNTT của môn/lớp này; không đổi nội dung "
        "chính trị, pháp lý, sự kiện lịch sử; tên riêng Việt Nam giữ nguyên hoặc dùng cách gọi chính thức.\n"
        "6. Chỉ trả JSON {\"id\": \"bản dịch\"}, đủ mọi id được giao; thêm khóa \"__terms__\" là danh sách tối đa "
        "8 thuật ngữ chuyên ngành then chốt THỰC SỰ xuất hiện trong các đoạn này, dạng {\"vi\": \"...\", \"en\": \"...\"} "
        "(vi viết đúng như trong đoạn; ưu tiên thuật ngữ trong BẢNG THUẬT NGỮ).\n"
        "BẢNG THUẬT NGỮ (đã đối chiếu): " + json.dumps(dict(glossary), ensure_ascii=False)
    )
    user = json.dumps({bid: text for bid, text in batch}, ensure_ascii=False)
    return system, user


def check_translation(vi, en, subject, grade):
    """Kiểm bằng chương trình. Trả (bản dịch dùng được hoặc None, danh sách cờ)."""
    flags = []
    if not isinstance(en, str) or not en.strip():
        return None, ["missing"]
    if sorted(_TOKEN_RE.findall(vi)) != sorted(_TOKEN_RE.findall(en)):
        return None, ["formula_tokens_changed"]
    low = en.casefold()
    for term_vi, term_en in terms_in(vi, subject, grade, limit=50):
        if term_en.casefold() not in low:
            flags.append(f"glossary:{term_vi}→{term_en}")
    return en.strip(), flags


def review_terms(items, text, subject, grade, limit=8):
    """Thuật ngữ AI đề xuất cho khung từ vựng — kiểm bằng chương trình, không tin AI:
    phải xuất hiện thật trong đoạn; có trong bảng đã duyệt thì lấy đúng bản tiếng Anh của bảng."""
    from services.subject_glossary import _norm, approved_terms
    approved = {_norm(vi): (vi, en) for vi, en in approved_terms(subject, grade)}
    hay, out, seen = _norm(text), [], set()
    for it in items or []:
        if not isinstance(it, dict):
            continue
        vi, en = str(it.get("vi") or "").strip(), str(it.get("en") or "").strip()
        key = _norm(vi)
        if not vi or not en or key in seen or len(vi) > 60 or len(en) > 80 or key not in hay:
            continue
        seen.add(key)
        if key in approved:
            out.append({"vi": approved[key][0], "en": approved[key][1], "source": "glossary"})
        else:
            out.append({"vi": vi, "en": en, "source": "ai"})
        if len(out) >= limit:
            break
    return out


def merge_response(batch, raw, subject, grade):
    """Đọc JSON trả về của một lô → {id: {"en":..., "flags":[...]}}; khối hỏng bị bỏ, không làm hỏng lô."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except ValueError:
        data = {}
    out = {}
    if not isinstance(data, dict):
        data = {}
    terms = review_terms(data.get("__terms__"), " ".join(t for _, t in batch), subject, grade)
    if terms and batch:
        out["__terms__" + batch[0][0]] = terms   # mỗi lô một khóa, không ghi đè khi gộp nhiều lô
    for bid, vi in batch:
        en, flags = check_translation(vi, data.get(bid), subject, grade)
        if en is not None:
            out[bid] = {"en": en, "flags": flags}
    return out


def inject_translations(body_html, translations):
    """Chèn bản tiếng Anh ngay dưới từng khối; công thức gắn lại đúng bản gốc của hệ thống."""
    missing = 0

    def add(m):
        nonlocal missing
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        text, maths = _tokenize(inner)
        if not re.search(r"[A-Za-zÀ-ỹĐđ]{2,}", _TOKEN_RE.sub("", text)):
            return m.group(0)
        item = translations.get(block_id(text))
        if not item:
            missing += 1
            return m.group(0)
        en = html.escape(item["en"])
        en = _TOKEN_RE.sub(lambda t: maths[int(t.group(1))] if int(t.group(1)) < len(maths) else "", en)
        flags = [f.split(":", 1)[1] for f in item.get("flags", []) if f.startswith("glossary:")]
        flag = (' data-glossary-flag="1" title="' + html.escape("Lệch bảng thuật ngữ, giáo viên cần xem: " + "; ".join(flags), quote=True) + '"'
                if flags else "")
        if flags:
            en = '<b class="glossary-warn">⚠ ' + html.escape("; ".join(flags)) + "</b> " + en
        return f'<{tag}{attrs}>{inner}<span class="en" lang="en"{flag}>{en}</span></{tag}>'
    body = _BLOCK_RE.sub(add, body_html)
    return body, missing


def flagged_count(translations):
    return sum(1 for k, v in (translations or {}).items()
               if not k.startswith("__terms__") and any(f.startswith("glossary:") for f in v.get("flags", [])))


def proposed_terms(translations):
    """Gộp thuật ngữ AI đề xuất (đã kiểm) của mọi lô: [{"vi","en","source"}], không trùng."""
    out, seen = [], set()
    for k, v in (translations or {}).items():
        if k.startswith("__terms__"):
            for t in v:
                if t["vi"].casefold() not in seen:
                    seen.add(t["vi"].casefold())
                    out.append(t)
    return out


def lesson_blocks(subject, grade, topic, lesson):  # noqa: E302
    """Các khối cần dịch của đúng phiếu sẽ in (dựng bằng chính bộ dựng phiếu, không dựng riêng)."""
    from services.lesson_export import build_lesson_html
    doc = build_lesson_html(subject, grade, topic, lesson, "lotus")
    article = doc.split('<article id="lesson">', 1)[-1].split("</article>", 1)[0]
    article = re.sub(r'<aside class="vocab-leaf"[\s\S]*?</aside>', "", article)
    blocks = extract_blocks(article)
    if str(topic or "").strip():
        blocks.insert(0, (block_id(str(topic)), str(topic).strip()))
    return blocks


TERM_FEEDBACK_CATEGORY = "Thuật ngữ song ngữ"


def build_term_feedback_entry(*, subject, grade, topic, text, name="", time=""):
    """Phản hồi 'thuật ngữ dịch sai' đi đúng đường USER_FEEDBACK sẵn có → SQLite/Supabase + Sheets Trạm 5."""
    import uuid
    return {"event_id": str(uuid.uuid4()), "time": time, "name": name, "grade": grade, "subject": subject,
            "category": TERM_FEEDBACK_CATEGORY, "rating": 1,
            "detail": json.dumps({"topic": str(topic or ""), "report": str(text or "")[:1000]}, ensure_ascii=False),
            "type": "USER_FEEDBACK"}


# Owner 19/11/2026: môn nhạy cảm chính trị – pháp lý chỉ mở song ngữ khi giáo viên bộ môn duyệt thuật ngữ.
SENSITIVE_SUBJECTS = frozenset({"Lịch sử", "Giáo dục kinh tế và pháp luật", "Ngữ văn", "Giáo dục công dân", "Lịch sử & Địa lý"})
SENSITIVE_NOTE = ("Môn có nội dung chính trị – pháp lý: bản song ngữ chỉ mở khi giáo viên bộ môn duyệt thuật ngữ. "
                  "Phiếu Sen Việt vẫn in đầy đủ bằng tiếng Việt.")


def bilingual_allowed(subject):
    from services.curriculum_policy import canonical_subject
    return canonical_subject(subject) not in SENSITIVE_SUBJECTS
