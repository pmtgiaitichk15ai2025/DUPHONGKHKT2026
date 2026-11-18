# -*- coding: utf-8 -*-
"""Nút 👍/👎 đánh giá gợi ý Socratic (owner 17/11/2026).

Đánh giá đi đúng đường phản hồi sẵn có (type USER_FEEDBACK → SQLite/Supabase + Google Sheets Trạm 5),
không tạo kho lưu thứ hai và không gọi AI.
"""
import hashlib
import json
import uuid

HINT_RATING_CATEGORY = "Đánh giá gợi ý Socratic"
TOOLTIP_UP = "Đánh giá lời hướng dẫn của hệ thống: gợi ý này hữu ích, giống thầy cô gợi mở"
TOOLTIP_DOWN = "Đánh giá lời hướng dẫn của hệ thống: gợi ý này chưa đạt, ghi lý do để sửa"
DOWN_REASONS = ("Chung chung, không bám câu hỏi", "Lộ đáp án / giải hộ", "Không giống thầy cô gợi mở",
                "Sai kiến thức", "Lý do khác")


def hint_id(station, question_text, hint) -> str:
    raw = f"{station}|{question_text}|{hint}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def build_hint_rating_entry(*, liked, station, subject, grade, question_text, hint,
                            name="", reason="", note="", time=""):
    """Bản ghi USER_FEEDBACK; `detail` là JSON để Trạm 5/Sheets đọc lại làm mẫu tốt hoặc ca lỗi."""
    detail = {
        "hint_id": hint_id(station, question_text, hint),
        "station": station,
        "verdict": "up" if liked else "down",
        "question": str(question_text or "")[:1500],
        "hint": str(hint or "")[:1500],
        "reason": "" if liked else str(reason or ""),
        "note": "" if liked else str(note or "")[:500],
    }
    return {
        "event_id": str(uuid.uuid4()),
        "time": time,
        "name": name,
        "grade": grade,
        "subject": subject,
        "category": HINT_RATING_CATEGORY,
        "rating": 5 if liked else 1,
        "detail": json.dumps(detail, ensure_ascii=False),
        "type": "USER_FEEDBACK",
    }


def render_hint_rating(st, sync_event, *, key, station, subject, grade, question_text, hint,
                       name="", time_fn=lambda: ""):
    """Vẽ 👍/👎 (tooltip qua `help`) dưới một gợi ý. Mỗi gợi ý chỉ ghi một lần mỗi phiên."""
    if not str(hint or "").strip():
        return
    done = st.session_state.setdefault("hint_ratings_done", {})
    hid = hint_id(station, question_text, hint)
    if hid in done:
        st.caption("✅ Cảm ơn thầy cô/em đã đánh giá gợi ý này.")
        return

    def send(liked, reason="", note=""):
        entry = build_hint_rating_entry(liked=liked, station=station, subject=subject, grade=grade,
                                        question_text=question_text, hint=hint, name=name,
                                        reason=reason, note=note, time=time_fn())
        try:
            sync_event(entry)
        finally:
            done[hid] = entry["rating"]

    # Một hàng ngang cố định (owner 18/11/2026: st.columns tự xếp dọc khi khung hẹp) và nhãn
    # luôn hiện, không chỉ dựa vào tooltip khi rê chuột.
    row = st.container(horizontal=True, wrap=False, vertical_alignment="center", gap="small")
    with row:
        st.caption("Đánh giá lời hướng dẫn của hệ thống:", width="content")
        up = st.button("👍", key=f"{key}_up", help=TOOLTIP_UP, width="content")
        down = st.button("👎", key=f"{key}_down", help=TOOLTIP_DOWN, width="content")
    if up:
        send(True)
        st.rerun()
    if down:
        st.session_state[f"{key}_down_open"] = True
    if st.session_state.get(f"{key}_down_open"):
        reason = st.radio("Gợi ý này chưa đạt vì:", DOWN_REASONS, key=f"{key}_reason", horizontal=True)
        note = st.text_input("Ghi thêm (không bắt buộc):", key=f"{key}_note")
        if st.button("📤 Gửi đánh giá", key=f"{key}_send"):
            send(False, reason, note)
            st.session_state.pop(f"{key}_down_open", None)
            st.rerun()
