# -*- coding: utf-8 -*-
"""Lượt giải độc lập: đánh dấu câu khóa lệch để thay; bộ giải lỗi thì không chặn đề."""
import json
import unittest

from services.context_recovery import _question_issue
from services.curriculum_policy import normalize_math_infinity
from services.independent_answer_check import (
    MISMATCH_MARK, mark_independent_mismatches, parse_solver_answers, solver_request,
)


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
        self.assertEqual(parse_solver_answers('{"p1": ["c."]}'), {"p1": ["C"]})

    def test_parse_accepts_work_text_booleans_and_missing_p3_key(self):
        # Mẫu phản hồi thật của model nhẹ 17/11/2026: bool dạng chữ và quên khóa "p3".
        raw = '{"p1": ["A", "C"], "p2": [["true", "false"], ["true", "true"]], ["2", "-1"]}'
        self.assertEqual(parse_solver_answers(raw),
                         {"p1": ["A", "C"], "p2": [[True, False], [True, True]], "p3": ["2", "-1"]})
        worked = '{"p1": [{"work": "y\'=0", "ans": "B"}], "p2": [{"work": "...", "ans": ["Đúng", "Sai"]}], "p3": [{"work": "...", "ans": 4.9}]}'
        self.assertEqual(parse_solver_answers(worked), {"p1": ["B"], "p2": [[True, False]], "p3": ["4.9"]})


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


if __name__ == "__main__":
    unittest.main()
