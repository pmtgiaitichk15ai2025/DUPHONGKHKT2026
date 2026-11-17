# -*- coding: utf-8 -*-
"""Lượt giải độc lập để đối chiếu khóa chấm của đề do AI sinh (Trạm 3).

Vì sao cần: luật cố định không bắt được lỗi khóa ở bài tham số/tối ưu. Ca thật
17/11/2026: x tối ưu = 2√6 ≈ 4,9 nhưng khóa ghi 6; có 4 giá trị nguyên m nhưng khóa ghi 3.

Cách làm:
- Gửi đề cho AI KHÔNG kèm khóa, lời giải, hint; kèm dữ liệu hình (hàm được vẽ, BBT).
- Đối chiếu từng câu: TN theo chữ cái, Đ/S theo từng ý, TLN bằng chính hàm chấm của app.
- Câu lệch được đánh dấu để đi vào luồng thay câu sẵn có (context_recovery).
- Lượt giải lỗi / trả dữ liệu lạ: bỏ qua, không chặn đề. Lệch quá nhiều câu (dấu hiệu
  chính bộ giải sai): không đánh dấu câu nào, chỉ ghi nhận để giáo viên xem.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy

MISMATCH_MARK = "_independent_answer_mismatch"
MAX_MISMATCH_RATIO = 0.4
UNVERIFIED_MARK = "_independent_answer_unverified"
# Bài dễ sai khóa nhất (ca thật 17/11/2026): tối ưu, giá trị lớn/nhỏ nhất, đếm tham số m.
HIGH_RISK_RE = re.compile(
    r"lớn nhất|nhỏ nhất|tối đa|tối thiểu|tối ưu|cực đại|cực tiểu|tham số|giá trị nguyên|bao nhiêu giá trị|\bm\b",
    re.IGNORECASE)

SOLVER_SYSTEM = (
    "Bạn là giáo viên chấm thi độc lập, cẩn thận và chính xác. Tự giải từng câu từ đầu, "
    "không đoán. Với câu có dữ liệu hình (hàm được vẽ, bảng biến thiên), dùng đúng dữ liệu đó. "
    "Với bài tối ưu, giá trị lớn/nhỏ nhất hoặc đếm tham số: kiểm ngược bằng cách thế đáp số vào điều kiện "
    "và xét đủ các đầu mút/trường hợp biên trước khi chốt. "
    "Chỉ trả null khi đề thật sự thiếu dữ kiện, không trả null vì câu khó. "
    "Chỉ trả JSON đúng schema được yêu cầu, không giải thích."
)


def _figure_note(question):
    notes = []
    spec = question.get("f")
    if isinstance(spec, dict) and spec.get("type"):
        k = {name: spec.get(name, 0) for name in "abcde"}
        kind = spec.get("type")
        if kind == "func_3":
            notes.append(f"Hình vẽ là đồ thị y = {k['a']}x^3 + {k['b']}x^2 + {k['c']}x + {k['d']}")
        elif kind == "func_1_1":
            notes.append(f"Hình vẽ là đồ thị y = ({k['a']}x + {k['b']})/({k['c']}x + {k['d']})")
        elif kind == "func_2_1":
            notes.append(f"Hình vẽ là đồ thị y = ({k['a']}x^2 + {k['b']}x + {k['c']})/({k['d']}x + {k['e']})")
    if question.get("bbt"):
        notes.append("Bảng biến thiên (dòng x | dấu y' | giá trị y):\n" + str(question["bbt"]))
    return "\n".join(notes)


def solver_request(exam, subject, grade):
    """(system, user) cho lượt giải độc lập; không chứa khóa, lời giải.

    Hint được gửi ở phần riêng, đọc SAU khi tự giải, để cùng lượt này kiểm hint có trỏ thẳng
    vào đáp án không (không thêm lượt gọi AI).
    """
    items = {}
    hints = {}
    for part in ("p1", "p2", "p3"):
        rows = []
        for question in exam.get(part) or []:
            if not isinstance(question, dict):
                rows.append({})
                continue
            row = {"q": question.get("q", "")}
            figure = _figure_note(question)
            if figure:
                row["figure"] = figure
            if part == "p1":
                row["options"] = question.get("opt") or []
            if part == "p2":
                row["statements"] = [str((s or {}).get("t", "")) for s in question.get("stmts") or []]
            rows.append(row)
            if part == "p2":
                hints.setdefault(part, []).append([str((s or {}).get("hint") or "") for s in question.get("stmts") or []])
            else:
                hints.setdefault(part, []).append(str(question.get("hint") or question.get("socratic_hint") or ""))
        if rows:
            items[part] = rows
    example = {
        "p1": [{"work": "tính nháp ngắn", "ans": "C", "hint_points_to": None}],
        "p2": [{"work": "tính nháp ngắn", "ans": [True, False, True, False], "hint_reveals": [False, True, False, False]}],
        "p3": [{"work": "tính nháp ngắn", "ans": "4.9", "hint_reveals": False}],
    }
    user = (f"Môn {subject}, lớp {grade}. Tự giải độc lập các câu sau.\n"
            + json.dumps(items, ensure_ascii=False)
            + "\nVới MỖI câu, ghi tính nháp ngắn (1–3 dòng: phép tính then chốt) vào 'work' TRƯỚC, rồi mới chốt 'ans'. "
            + "Phần p1: ans là một chữ cái A/B/C/D. Phần p2: ans là mảng true/false cho từng ý theo thứ tự. "
            + "Phần p3: ans là đáp số dạng chuỗi. Không chắc chắn thì ans = null. "
            + "\n\nSAU KHI đã tự giải xong, mới đọc phần GỢI Ý dành cho học sinh dưới đây (cùng thứ tự câu/ý). "
            + "Không dùng gợi ý để đổi 'ans'. Với mỗi gợi ý, xét: một học sinh CHƯA biết làm, chỉ đọc gợi ý, có chọn ngay được đáp án mà không cần tự suy luận không? "
            + "Phần p1: 'hint_points_to' là chữ cái phương án mà gợi ý chỉ thẳng tới (nêu, diễn đạt lại nội dung, hoặc loại trừ hết phương án khác), null nếu gợi ý chỉ hướng dẫn cách nghĩ. "
            + "Phần p2: 'hint_reveals' là mảng true/false cho từng ý, true nếu gợi ý của ý đó đã nói ra ý đúng hay sai. "
            + "Phần p3: 'hint_reveals' là true nếu gợi ý đã nêu hoặc gần như nêu đáp số.\nGỢI Ý: "
            + json.dumps(hints, ensure_ascii=False)
            + "\nTrả đúng một object JSON có đủ ba khóa p1, p2, p3 (phần không có câu thì để mảng rỗng), ví dụ: "
            + json.dumps(example, ensure_ascii=False))
    return SOLVER_SYSTEM, user


def _bool_value(value):
    if isinstance(value, bool) or value is None:
        return value
    text = str(value).strip().casefold()
    if text in ("true", "đúng", "dung", "đ", "t"):
        return True
    if text in ("false", "sai", "s", "f"):
        return False
    if text in ("null", "none", ""):
        return None
    raise ValueError("not a boolean")


def _answer_of(entry):
    return entry.get("ans") if isinstance(entry, dict) else entry


def _load_solver_json(raw):
    if isinstance(raw, dict):
        return raw
    text = str(raw or "").strip()
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        text = match.group(0)
    try:
        return json.loads(text)
    except ValueError:
        pass
    # Model nhẹ đôi khi quên khóa "p3": {"p1": [...], "p2": [[...]], ["2", "0"]}
    if '"p3"' not in text:
        repaired = re.sub(r'(\]\s*\]\s*,)\s*(\[)', r'\1 "p3": \2', text, count=1)
        try:
            return json.loads(repaired)
        except ValueError:
            return None
    return None


def parse_solver_answers(raw):
    """Đọc JSON đáp án (chấp nhận kèm 'work', bool dạng chữ); dạng lạ trả None (không đánh dấu gì)."""
    data = _load_solver_json(raw)
    if not isinstance(data, dict):
        return None
    out = {}
    try:
        p1 = data.get("p1")
        if isinstance(p1, list):
            letters = []
            for entry in p1:
                value = _answer_of(entry)
                if value is None or str(value).strip().casefold() == "null":
                    letters.append(None)
                elif isinstance(value, str) and re.fullmatch(r"\s*[A-Da-d]\s*\.?\s*", value):
                    letters.append(value.strip().strip(".").upper())
                else:
                    return None
            out["p1"] = letters
        p2 = data.get("p2")
        if isinstance(p2, list):
            rows = []
            for entry in p2:
                values = _answer_of(entry)
                if values is None:
                    rows.append([])
                elif isinstance(values, list):
                    rows.append([_bool_value(v) for v in values])
                else:
                    return None
            out["p2"] = rows
        p3 = data.get("p3")
        if isinstance(p3, list):
            answers = []
            for entry in p3:
                value = _answer_of(entry)
                if value is None or str(value).strip().casefold() == "null":
                    answers.append(None)
                elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
                    answers.append(str(value))
                else:
                    return None
            out["p3"] = answers
    except ValueError:
        return None
    has_answer = any(v is not None for v in out.get("p1", []) + out.get("p3", [])) or any(
        v is not None for row in out.get("p2", []) for v in row)
    if not has_answer:
        return None
    out["hint"] = _parse_hint_signals(data)
    return out


def _parse_hint_signals(data):
    """Tín hiệu 'hint trỏ thẳng đáp án' từ cùng lượt giải; dạng lạ thì bỏ qua (không ảnh hưởng đối chiếu khóa)."""
    signals = {"p1": [], "p2": [], "p3": []}
    for entry in data.get("p1") or []:
        value = entry.get("hint_points_to") if isinstance(entry, dict) else None
        text = str(value or "").strip().strip(".").upper()
        signals["p1"].append(text if text in ("A", "B", "C", "D") else None)
    for entry in data.get("p2") or []:
        row = entry.get("hint_reveals") if isinstance(entry, dict) else None
        flags = []
        for value in row if isinstance(row, list) else []:
            try:
                flags.append(bool(_bool_value(value)))
            except ValueError:
                flags.append(False)
        signals["p2"].append(flags)
    for entry in data.get("p3") or []:
        value = entry.get("hint_reveals") if isinstance(entry, dict) else None
        try:
            signals["p3"].append(bool(_bool_value(value)))
        except ValueError:
            signals["p3"].append(False)
    return signals


HINT_LEAK_MARK = "hint_leak_detected"
# Thử thật 17/11/2026: model nhẹ gắn cờ 100% hint (kể cả hint tốt) — không phân biệt được.
# Chỉ tin tín hiệu khi bộ giải gắn cờ CHỌN LỌC (không quá 30% số hint), nếu không thì bỏ qua toàn bộ.
MAX_HINT_LEAK_RATIO = 0.3


def mark_hint_leaks(exam, solved):
    """Đánh dấu hint mà bộ giải thấy trỏ thẳng vào đáp án đúng; app sẽ không hiện hint đó."""
    from qa_runtime import canonicalize_mcq_key
    signals = (solved or {}).get("hint") or {}
    candidates = _hint_leak_candidates(exam, signals, canonicalize_mcq_key)
    hint_total = sum(1 for q in exam.get("p1") or [] if isinstance(q, dict) and (q.get("hint") or q.get("socratic_hint")))
    hint_total += sum(1 for q in exam.get("p2") or [] if isinstance(q, dict) for s in q.get("stmts") or [] if isinstance(s, dict) and s.get("hint"))
    hint_total += sum(1 for q in exam.get("p3") or [] if isinstance(q, dict) and (q.get("hint") or q.get("socratic_hint")))
    if not candidates or not hint_total or len(candidates) > MAX_HINT_LEAK_RATIO * hint_total:
        return []
    marked = []
    for target, part, idx in candidates:
        target[HINT_LEAK_MARK] = True
        marked.append((part, idx))
    return marked


def _hint_leak_candidates(exam, signals, canonicalize_mcq_key):
    found = []
    for idx, question in enumerate(exam.get("p1") or []):
        points = signals.get("p1") or []
        if idx < len(points) and points[idx] and isinstance(question, dict) and points[idx] == canonicalize_mcq_key(question):
            found.append((question, "p1", idx))
    for idx, question in enumerate(exam.get("p2") or []):
        rows = signals.get("p2") or []
        if idx >= len(rows) or not isinstance(question, dict):
            continue
        for s_idx, stmt in enumerate(question.get("stmts") or []):
            if s_idx < len(rows[idx]) and rows[idx][s_idx] and isinstance(stmt, dict):
                found.append((stmt, "p2", idx))
    for idx, question in enumerate(exam.get("p3") or []):
        flags = signals.get("p3") or []
        if idx < len(flags) and flags[idx] and isinstance(question, dict):
            found.append((question, "p3", idx))
    return found


def find_mismatches(exam, solved):
    """Danh sách (phần, chỉ số) mà bộ giải độc lập không khớp khóa chấm."""
    from qa_runtime import canonicalize_mcq_key, normalize_bool, short_answer_matches
    found = []
    for idx, question in enumerate(exam.get("p1") or []):
        answers = solved.get("p1") or []
        if idx < len(answers) and answers[idx] and isinstance(question, dict):
            key = canonicalize_mcq_key(question)
            if key and answers[idx] != key:
                found.append(("p1", idx))
    for idx, question in enumerate(exam.get("p2") or []):
        rows = solved.get("p2") or []
        if idx >= len(rows) or not isinstance(question, dict):
            continue
        for s_idx, stmt in enumerate(question.get("stmts") or []):
            if s_idx >= len(rows[idx]) or rows[idx][s_idx] is None:
                continue
            expected = normalize_bool((stmt or {}).get("a") if "a" in (stmt or {}) else (stmt or {}).get("ans"))
            if expected is not None and rows[idx][s_idx] != expected:
                found.append(("p2", idx))
                break
    for idx, question in enumerate(exam.get("p3") or []):
        answers = solved.get("p3") or []
        if idx < len(answers) and answers[idx] not in (None, "") and isinstance(question, dict):
            expected = str(question.get("ans", "")).strip()
            if expected and not short_answer_matches(answers[idx], expected, question.get("rounding_decimals")):
                found.append(("p3", idx))
    return found


def is_high_risk(question):
    """Câu tối ưu/tham số: khóa dễ sai, cần bộ giải xác nhận."""
    return isinstance(question, dict) and bool(HIGH_RISK_RE.search(str(question.get("q") or "")))


def find_unverified(exam, solved):
    """Câu rủi ro cao mà bộ giải không đưa được đáp án: khóa chưa được ai xác nhận."""
    found = []
    for part in ("p1", "p2", "p3"):
        answers = solved.get(part) or []
        for idx, question in enumerate(exam.get(part) or []):
            if not is_high_risk(question):
                continue
            value = answers[idx] if idx < len(answers) else None
            missing = (value in (None, "") if part != "p2"
                       else not isinstance(value, list) or any(v is None for v in value))
            if missing:
                found.append((part, idx))
    return found


def _mark_unverified(result, solved, report):
    unverified = find_unverified(result, solved)
    for part, idx in unverified:
        result[part][idx][UNVERIFIED_MARK] = True
    if unverified:
        report["unverified"] = [{"part": p, "index": i} for p, i in unverified]


def count_review_flags(exam):
    """Số câu giáo viên cần xem lại khóa (chưa xác nhận độc lập hoặc lượt giải lệch quá nhiều)."""
    count = sum(1 for part in ("p1", "p2", "p3") for q in (exam.get(part) or [])
                if isinstance(q, dict) and q.get(UNVERIFIED_MARK))
    check = exam.get("independent_answer_check") or {}
    if isinstance(check, dict) and check.get("status") == "too_many_mismatches_teacher_review":
        count += len(check.get("mismatches") or [])
    return count


def mark_independent_mismatches(exam, subject, grade, solve):
    """Trả (bản sao đề có đánh dấu câu lệch, báo cáo). `solve(system, user) -> str`."""
    result = deepcopy(exam)
    total = sum(len(result.get(p) or []) for p in ("p1", "p2", "p3"))
    if not total:
        return result, {"status": "skipped_no_items"}
    try:
        system, user = solver_request(result, subject, grade)
        solved = parse_solver_answers(solve(system, user))
    except Exception as error:  # Lượt giải lỗi không được chặn đề.
        return result, {"status": "skipped_solver_error", "error": type(error).__name__}
    if not solved:
        return result, {"status": "skipped_unreadable_response"}
    mismatches = find_mismatches(result, solved)
    report = {"status": "checked", "checked": total,
              "mismatches": [{"part": p, "index": i} for p, i in mismatches]}
    if len(mismatches) > MAX_MISMATCH_RATIO * total:
        report["status"] = "too_many_mismatches_teacher_review"
        _mark_unverified(result, solved, report)
        leaks = mark_hint_leaks(result, solved)
        if leaks:
            report["hint_leaks"] = [{"part": p, "index": i} for p, i in leaks]
        return result, report
    for part, idx in mismatches:
        result[part][idx][MISMATCH_MARK] = True
    _mark_unverified(result, solved, report)
    leaks = mark_hint_leaks(result, solved)
    if leaks:
        report["hint_leaks"] = [{"part": p, "index": i} for p, i in leaks]
    return result, report
