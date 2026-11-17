# -*- coding: utf-8 -*-
"""Lượt giải độc lập: đánh dấu câu khóa lệch để thay; bộ giải lỗi thì không chặn đề."""
import json
import unittest

from services.context_recovery import _question_issue
from services.curriculum_policy import normalize_math_infinity
from services.independent_answer_check import (
    MISMATCH_MARK, mark_independent_mismatches, parse_solver_answers, solver_request,
)


def answers_only(parsed):
    return {k: v for k, v in (parsed or {}).items() if k != "hint"}


def exam():
    # P3 lấy từ ca thật 17/11/2026: tối ưu tại x = 2√6 ≈ 4,9 nhưng khóa ghi 6.
    return {
        "p1": [
            {"q": "Tiệm cận đứng của $y=\\frac{2x-1}{x+1}$ là", "opt": ["A. $x=1$", "B. $y=2$", "C. $x=-1$", "D. $y=-1$"], "ans": "C",
             "hint": "gợi ý", "explain": "lời giải"},
            {"q": "Hình vẽ là đồ thị nào?", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": "A",
             "f": {"type": "func_3", "a": 1, "b": 0, "c": -3, "d": 2}},
        ],
        "p2": [{"q": "Cho $y=x^3-3x$.", "stmts": [{"t": "a", "a": True}, {"t": "b", "a": False}]}],
        "p3": [{"q": "Vườn 36 m², tìm x để chi phí thấp nhất (làm tròn 0,1).", "ans": "6"},
               {"q": "Tìm m.", "ans": "-4"}],
    }


class IndependentAnswerCheckTests(unittest.TestCase):
    def test_request_hides_keys_but_keeps_figure_data(self):
        system, user = solver_request(exam(), "Toán học", 12)
        questions_part = user.split("\nVới MỖI câu")[0]
        self.assertNotIn("lời giải", questions_part)
        self.assertNotIn("gợi ý", questions_part)
        self.assertNotIn('"ans"', questions_part)
        self.assertIn("y = 1x^3 + 0x^2 + -3x + 2", user)
        self.assertIn("Tự giải", system)

    def test_wrong_short_answer_is_marked_and_becomes_an_issue(self):
        reply = json.dumps({"p1": ["C", "A"], "p2": [[True, False]], "p3": ["4,9", "-4,0"]})
        result, report = mark_independent_mismatches(exam(), "Toán học", 12, lambda s, u: reply)
        self.assertEqual(report["status"], "checked")
        self.assertEqual(report["mismatches"], [{"part": "p3", "index": 0}])
        self.assertTrue(result["p3"][0].get(MISMATCH_MARK))
        self.assertFalse(result["p3"][1].get(MISMATCH_MARK))   # -4,0 khớp -4 theo hàm chấm của app
        self.assertEqual(_question_issue(result["p3"][0], "p3", "Toán học", 12), "independent_answer_mismatch")

    def test_mcq_and_statement_mismatch(self):
        reply = json.dumps({"p1": ["B", None], "p2": [[True, True]], "p3": [None, None]})
        result, report = mark_independent_mismatches(exam(), "Toán học", 12, lambda s, u: reply)
        self.assertEqual({(m["part"], m["index"]) for m in report["mismatches"]}, {("p1", 0), ("p2", 0)})

    def test_solver_failure_never_blocks_exam(self):
        for solve in (lambda s, u: "không phải JSON", lambda s, u: json.dumps({"p1": [{"q": "đề"}]}),
                      lambda s, u: (_ for _ in ()).throw(TimeoutError())):
            result, report = mark_independent_mismatches(exam(), "Toán học", 12, solve)
            self.assertTrue(report["status"].startswith("skipped"), report)
            self.assertFalse(any(q.get(MISMATCH_MARK) for p in ("p1", "p2", "p3") for q in result[p]))

    def test_too_many_mismatches_means_solver_is_unreliable(self):
        reply = json.dumps({"p1": ["A", "B"], "p2": [[False, True]], "p3": ["1", "2"]})
        result, report = mark_independent_mismatches(exam(), "Toán học", 12, lambda s, u: reply)
        self.assertEqual(report["status"], "too_many_mismatches_teacher_review")
        self.assertFalse(any(q.get(MISMATCH_MARK) for p in ("p1", "p2", "p3") for q in result[p]))

    def test_parse_rejects_wrong_shapes(self):
        self.assertIsNone(parse_solver_answers('{"p1": ["E"]}'))
        self.assertIsNone(parse_solver_answers('{"p2": [["có lẽ"]]}'))
        self.assertEqual(answers_only(parse_solver_answers('{"p1": ["c."]}')), {"p1": ["C"]})

    def test_parse_accepts_work_text_booleans_and_missing_p3_key(self):
        # Mẫu phản hồi thật của model nhẹ 17/11/2026: bool dạng chữ và quên khóa "p3".
        raw = '{"p1": ["A", "C"], "p2": [["true", "false"], ["true", "true"]], ["2", "-1"]}'
        self.assertEqual(answers_only(parse_solver_answers(raw)),
                         {"p1": ["A", "C"], "p2": [[True, False], [True, True]], "p3": ["2", "-1"]})
        worked = '{"p1": [{"work": "y\'=0", "ans": "B"}], "p2": [{"work": "...", "ans": ["Đúng", "Sai"]}], "p3": [{"work": "...", "ans": 4.9}]}'
        self.assertEqual(answers_only(parse_solver_answers(worked)), {"p1": ["B"], "p2": [[True, False]], "p3": ["4.9"]})


class MathInfinityTests(unittest.TestCase):
    def test_bare_inf_inside_math_becomes_infty(self):
        self.assertEqual(normalize_math_infinity("B. $(1; +inf)$"), "B. $(1; +\\infty)$")
        self.assertEqual(normalize_math_infinity("$(-infty; 2)$"), "$(-\\infty; 2)$")

    def test_existing_latex_and_plain_text_unchanged(self):
        for text in ("$x \\to +\\infty$", "$\\inf_{x} f$", "information inf", "D. $(-∞; 1)$"):
            self.assertEqual(normalize_math_infinity(text), text)


class DeterministicMathChecksTests(unittest.TestCase):
    """Ca thật đề 7 (17/11/2026)."""

    def test_counting_integers_for_increasing_cubic_on_R_is_unbounded(self):
        from services.math_conditions import math_condition_conflict
        q = {"q": "Có bao nhiêu giá trị nguyên của tham số $m$ để hàm số $y = \\frac{1}{3}x^3 - x^2 + mx + 5$ đồng biến trên $\\mathbb{R}$?",
             "ans": "0"}
        self.assertEqual(math_condition_conflict(q), "unbounded_integer_parameter_count")
        # Hệ số x^3 âm mà hỏi đồng biến trên R: không m nào thỏa, đáp số 0 hợp lệ.
        q["q"] = q["q"].replace("\\frac{1}{3}x^3", "-x^3")
        self.assertEqual(math_condition_conflict(q), "")

    def test_rational_stem_with_cubic_figure_is_rejected(self):
        from services.math_conditions import math_condition_conflict
        q = {"q": "Cho hàm số $y = \\frac{ax+b}{cx+d}$ có đồ thị như hình vẽ.",
             "stmts": [{"t": "a", "a": True}], "f": {"type": "func_3", "a": 2, "b": 1, "c": 1, "d": -1}}
        self.assertEqual(math_condition_conflict(q), "graph_type_mismatch")
        q["f"]["type"] = "func_1_1"
        self.assertEqual(math_condition_conflict(q), "")

    def test_stray_pipe_before_option_label_is_removed(self):
        from services.curriculum_policy import prepare_exam_for_delivery
        exam = {"p1": [{"q": "Đồ thị hàm số $y = \\frac{2x^2 - 3x + 1}{x - 2}$ có tiệm cận xiên là đường thẳng:",
                        "opt": ["A. $y = 2x + 1$.", "B. $y = 2x - 1$.", "C. $y = 2x + 3$.", "|D. $y = x + 2$."],
                        "ans": "A", "explain": "x"}]}
        out = prepare_exam_for_delivery(exam, "Toán học", 12)
        self.assertEqual(out["p1"][0]["opt"][3], "D. $y = x + 2$.")


class DuplicateKeyIsolationTests(unittest.TestCase):
    """Ca thật Lịch sử 12 (17/11/2026): cả đề bị hủy vì khóa trùng, dù chỉ một câu mơ hồ."""

    def test_one_conflicting_question_is_isolated_not_whole_exam(self):
        from services.ai_json import parse_ai_json, question_has_duplicate_conflict
        raw = ('{"subject":"Lịch sử","grade":12,"p1":['
               '{"q":"Câu một","opt":["A. x","B. y","C. z","D. t"],"ans":"A","ans":"B"},'
               '{"q":"Câu hai","opt":["A. x","B. y","C. z","D. t"],"ans":"C"}]}')
        data = parse_ai_json(raw)
        self.assertEqual(len(data["p1"]), 2)
        self.assertTrue(question_has_duplicate_conflict(data["p1"][0]))
        self.assertFalse(question_has_duplicate_conflict(data["p1"][1]))
        self.assertEqual(_question_issue(data["p1"][0], "p1", "Lịch sử", 12), "duplicate_key_conflict")

    def test_root_level_conflict_still_rejected(self):
        from services.ai_json import parse_ai_json
        for raw in ('{"code":"1","code":"2","p1":[]}',
                    '{"part_doc_hieu":{"text":"a","text":"b"},"part_viet":[]}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_ai_json(raw)


class ItemIsolationTests(unittest.TestCase):
    """Ca thật Lịch sử 12 và Địa lý 10 (17/11/2026): một câu thiếu khóa làm hủy cả đề."""

    def _exam(self, bad_ans):
        good = {"q": "Câu tốt", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": "B."}
        bad = {"q": "Câu lỗi", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": bad_ans}
        return {"p1": [good, bad, dict(good, q="Câu tốt 2", ans="Đáp án: C")]}

    def test_strict_letter_reading_does_not_guess(self):
        from services.curriculum_policy import strict_mcq_letter
        options = ["A. 1", "B. 2", "C. 3", "D. 4"]
        for raw, letter in (("B", "B"), ("b.", "B"), ("(C)", "C"), ("D) 4", "D"), ("Đáp án: A", "A"), ("2", "B"),
                            ("Câu B", ""), ("E", ""), ("", ""), ("Ba", "")):
            self.assertEqual(strict_mcq_letter(raw, options), letter, raw)

    def test_strict_mode_still_rejects_whole_exam(self):
        from services.curriculum_policy import validate_exam_structure
        with self.assertRaises(ValueError):
            validate_exam_structure(self._exam(""), "Lịch sử")

    def test_isolation_keeps_good_items_and_leaves_bad_one_for_recovery(self):
        from services.curriculum_policy import validate_exam_structure
        exam = validate_exam_structure(self._exam(""), "Lịch sử", (3, 0, 0), isolate_items=True)
        self.assertEqual([q["ans"] for q in exam["p1"]], ["B", "", "C"])
        self.assertEqual(_question_issue(exam["p1"][1], "p1", "Lịch sử", 12), "missing_or_invalid_question_data")

    def test_all_items_broken_is_still_rejected(self):
        from services.curriculum_policy import validate_exam_structure
        exam = {"p1": [{"q": "x", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": ""}]}
        with self.assertRaises(ValueError):
            validate_exam_structure(exam, "Lịch sử", isolate_items=True)


class ForeignScriptTests(unittest.TestCase):
    """Ca thật Lịch sử 12 (17/11/2026): AI trộn chữ Thái vào ngữ liệu tiếng Việt."""

    def test_foreign_script_is_rejected_but_greek_and_literature_han_are_kept(self):
        from services.curriculum_policy import item_display_language_issue as issue
        thai = "Hội nghị Xan Ph" + "ราน" + " năm 1945"
        han = "Bài thơ " + "靜夜思"
        self.assertEqual(issue(thai, "Lịch sử"), "foreign_script_contamination")
        self.assertEqual(issue(han, "Lịch sử"), "foreign_script_contamination")
        self.assertEqual(issue(han, "Ngữ văn"), "")
        self.assertEqual(issue("Góc α và tần số góc ω", "Vật lý"), "")

    def test_contaminated_option_enters_replacement_path(self):
        q = {"q": "Hiến chương Liên hợp quốc được thông qua tại hội nghị nào?",
             "opt": ["A. I-an-ta", "B. Xan Ph" + "ราน", "C. Pốt-xđam", "D. Tê-hê-ran"], "ans": "B"}
        self.assertEqual(_question_issue(q, "p1", "Lịch sử", 12), "display_language_mismatch")


class HintLeakJudgeTests(unittest.TestCase):
    """Cùng lượt giải độc lập kiểm hint có trỏ thẳng đáp án (ca thật Tin 12, 17/11/2026)."""

    def _exam(self):
        return {"p1": [{"q": "Một lợi ích lớn của AI trong y tế là gì?",
                        "opt": ["A. Thay thế hoàn toàn bác sĩ", "B. Hỗ trợ chẩn đoán qua phân tích ảnh X-quang, MRI",
                                "C. Tự động chữa mọi bệnh", "D. Giảm số bệnh nhân"], "ans": "B",
                        "hint": "Hãy tìm phương án nói về việc AI trợ giúp bác sĩ phân tích hình ảnh y khoa nhé."},
                       {"q": "Tiệm cận đứng của $y=\frac{1}{x-2}$ là", "opt": ["A. $x=2$", "B. $x=-2$", "C. $y=2$", "D. $y=0$"],
                        "ans": "A", "hint": "Em xem giá trị nào của $x$ làm mẫu số bằng 0 nhé."}]
                      + [{"q": f"Câu ôn tập số {i}", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": "C",
                          "hint": f"Em đọc kỹ dữ kiện câu {i} rồi tự hỏi bước đầu tiên là gì nhé."} for i in range(3, 13)],
                "p2": [{"q": "Cho $y=x^3$.", "stmts": [{"t": "a", "a": True, "hint": "Ý này đúng rồi đó em."},
                                                       {"t": "b", "a": False, "hint": "Em tính đạo hàm nhé."}]}],
                "p3": [{"q": "Tính 2+2.", "ans": "4", "hint": "Hai cộng hai được bốn."}]}

    def test_request_puts_hints_after_solving_and_reply_marks_leaks(self):
        from services.socratic_context import build_tram3_socratic_guide, safe_ai_hint
        system, user = solver_request(self._exam(), "Tin học", 12)
        self.assertLess(user.index("Với MỖI câu"), user.index("GỢI Ý:"))
        self.assertIn("phân tích hình ảnh y khoa", user.split("GỢI Ý:")[1])
        reply = json.dumps({"p1": [{"work": "", "ans": "B", "hint_points_to": "B"},
                                   {"work": "", "ans": "A", "hint_points_to": None}]
                                  + [{"work": "", "ans": "C", "hint_points_to": None}] * 10,
                            "p2": [{"work": "", "ans": [True, False], "hint_reveals": [True, False]}],
                            "p3": [{"work": "", "ans": "4", "hint_reveals": True}]})
        result, report = mark_independent_mismatches(self._exam(), "Tin học", 12, lambda s, u: reply)
        self.assertEqual(report["mismatches"], [])
        self.assertEqual({(m["part"], m["index"]) for m in report["hint_leaks"]}, {("p1", 0), ("p2", 0), ("p3", 0)})
        self.assertEqual(safe_ai_hint(result["p1"][0]), "")          # diễn đạt lại phương án đúng: bỏ
        self.assertTrue(safe_ai_hint(result["p1"][1]))              # hint hướng dẫn cách nghĩ: giữ
        guide = build_tram3_socratic_guide(result["p2"][0])
        self.assertNotIn("Ý này đúng", guide)
        self.assertIn("Em tính đạo hàm", guide)

    def test_judge_flagging_almost_every_hint_is_ignored(self):
        # Ca thật 17/11/2026: model nhẹ gắn cờ 24/24 hint (kể cả hint tốt) — không tin, giữ hint.
        from services.socratic_context import safe_ai_hint
        reply = json.dumps({"p1": [{"work": "", "ans": "B", "hint_points_to": "B"}, {"work": "", "ans": "A", "hint_points_to": "A"}]
                                  + [{"work": "", "ans": "C", "hint_points_to": "C"}] * 10,
                            "p2": [{"ans": [True, False], "hint_reveals": [True, True]}], "p3": [{"ans": "4", "hint_reveals": True}]})
        result, report = mark_independent_mismatches(self._exam(), "Tin học", 12, lambda s, u: reply)
        self.assertNotIn("hint_leaks", report)
        self.assertTrue(safe_ai_hint(result["p1"][1]))

    def test_hint_pointing_to_a_wrong_option_is_not_a_leak(self):
        reply = json.dumps({"p1": [{"work": "", "ans": "B", "hint_points_to": "C"}, {"work": "", "ans": "A"}]
                                  + [{"work": "", "ans": "C"}] * 10, "p2": [], "p3": []})
        result, report = mark_independent_mismatches(self._exam(), "Tin học", 12, lambda s, u: reply)
        self.assertNotIn("hint_leaks", report)

    def test_unreadable_hint_fields_do_not_break_answer_check(self):
        reply = json.dumps({"p1": [{"work": "", "ans": "B", "hint_points_to": 7}, {"work": "", "ans": "A"}]
                                  + [{"work": "", "ans": "C"}] * 10,
                            "p2": [{"ans": [True, False], "hint_reveals": "không rõ"}], "p3": [{"ans": "4"}]})
        result, report = mark_independent_mismatches(self._exam(), "Tin học", 12, lambda s, u: reply)
        self.assertEqual(report["status"], "checked")


if __name__ == "__main__":
    unittest.main()
