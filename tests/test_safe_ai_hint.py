# -*- coding: utf-8 -*-
"""Hint AI bám dữ kiện câu được dùng; hint lộ đáp án bị chặn và quay về câu mẫu."""
import unittest

from services.socratic_context import build_tram3_socratic_guide, safe_ai_hint
from services.visual_placement import split_stem_at_visual


def mcq(hint, ans="D", opts=("A. $0$.", "B. $1$.", "C. $2$.", "D. $3$."),
        q="Số giao điểm của đồ thị hàm số $y = x^3 - 3x^2 + 1$ và trục hoành là:"):
    return {"q": q, "opt": list(opts), "ans": ans, "hint": hint, "explain": ""}


class SafeAiHintTests(unittest.TestCase):
    def test_specific_warm_hint_is_used(self):
        hint = ("Em để ý hàm $y = x^3 - 3x^2 + 1$ nhé. Thầy hỏi em: số giao điểm với trục hoành "
                "liên quan gì đến dấu của giá trị cực đại và cực tiểu? Em làm được mà!")
        q = mcq(hint)
        self.assertEqual(safe_ai_hint(q), hint)
        self.assertIn("x^3 - 3x^2 + 1", build_tram3_socratic_guide(q, "Toán học", 12))

    def test_number_answer_in_plain_text_is_blocked(self):
        # Ca thật 17/11/2026: hint nói thẳng "cắt trục hoành tại 3 điểm" (đáp án D. 3).
        q = mcq("Hãy tìm các giá trị cực đại và cực tiểu của hàm số. Nếu chúng trái dấu, "
                "đồ thị sẽ cắt trục hoành tại 3 điểm.")
        self.assertEqual(safe_ai_hint(q), "")
        self.assertNotIn("3 điểm", build_tram3_socratic_guide(q, "Toán học", 12))

    def test_correct_option_content_and_letter_are_blocked(self):
        opts = ("A. $y=2$.", "B. $x=-2$.", "C. $y=-1/2$.", "D. $y=1/2$.")
        stem = "Đồ thị hàm số $y = \\frac{2x-1}{x+2}$ có đường tiệm cận ngang là:"
        self.assertEqual(safe_ai_hint(mcq("Em sẽ thấy tiệm cận ngang là $y=2$ thôi.", "A", opts, stem)), "")
        self.assertEqual(safe_ai_hint(mcq("Em xét giới hạn rồi chọn phương án A nhé.", "A", opts, stem)), "")

    def test_short_answer_value_is_blocked(self):
        q = {"q": "Tìm giá trị cực đại của hàm số $y = -x^3 + 3x + 1$.", "ans": "3",
             "hint": "Em tính đạo hàm, sẽ ra giá trị cực đại bằng 3 nhé.", "explain": ""}
        self.assertEqual(safe_ai_hint(q), "")
        q["hint"] = "Em tính $y'$ của hàm $y = -x^3 + 3x + 1$, rồi tự hỏi: tại điểm nào $y'$ đổi dấu từ dương sang âm?"
        self.assertTrue(safe_ai_hint(q))

    def test_statement_verdict_is_blocked(self):
        q = {"q": "Cho hàm số $y = x^3 - 3x^2 + 2$.", "stmts": [{"t": "a", "a": True}],
             "hint": "Ý a đúng vì đạo hàm dương trên khoảng đó.", "explain": ""}
        self.assertEqual(safe_ai_hint(q), "")

    def test_copied_explanation_is_blocked(self):
        explain = "Ta có y' = 3x^2 - 6x = 0 khi x = 0 hoặc x = 2, lập bảng biến thiên thấy cực tiểu tại x = 2."
        q = {"q": "Cho hàm số $y = x^3 - 3x^2 + 2$.", "ans": "", "opt": [],
             "hint": "Gợi ý: " + explain, "explain": explain}
        self.assertEqual(safe_ai_hint(q), "")

    def test_missing_hint_falls_back_to_template(self):
        q = mcq("")
        self.assertEqual(safe_ai_hint(q), "")
        self.assertTrue(build_tram3_socratic_guide(q, "Toán học", 12))


class VisualPlacementTests(unittest.TestCase):
    def test_table_goes_between_lead_in_and_question(self):
        before, after = split_stem_at_visual(
            "Cho hàm số $y=f(x)$ liên tục trên $\\mathbb{R}$ và có bảng biến thiên:\n\n\n"
            "Số nghiệm của phương trình $2f(x) - 1 = 0$ là:")
        self.assertTrue(before.endswith("bảng biến thiên:"))
        self.assertEqual(after, "Số nghiệm của phương trình $2f(x) - 1 = 0$ là:")

    def test_plain_stem_unchanged(self):
        text = "Cho hàm số có đồ thị như hình vẽ. Công thức hàm số là:"
        self.assertEqual(split_stem_at_visual(text), (text, ""))



class BbtDirectionTests(unittest.TestCase):
    def test_increasing_interval_cannot_go_down(self):
        from services.math_conditions import _bbt_direction_conflict, math_condition_conflict
        # Ca thật 17/11/2026: y' > 0 trên (1; +∞) nhưng y đi từ 3 xuống 1.
        q = {"q": "Cho hàm số có bảng biến thiên như sau:", "subject": "Toán học",
             "bbt": "x | -inf | -1 | 0 | 1 | +inf\nf'(x) | + | 0 | - || - | 0 | +\nf(x) | -1 | 2 | -inf | +inf | 3 | 1"}
        self.assertTrue(_bbt_direction_conflict(q))
        self.assertTrue(math_condition_conflict(q))

    def test_consistent_tables_pass(self):
        from services.math_conditions import _bbt_direction_conflict
        ok_plain = {"q": "Cho bảng biến thiên:", "bbt": "x | -inf | 0 | 2 | +inf\ny' | - | 0 | + | 0 | -\ny | +inf | -3 | 1 | -inf"}
        ok_asym = {"q": "Cho bảng biến thiên:", "bbt": "x | -inf | -1 | 0 | 1 | +inf\nf'(x) | + | 0 | - || - | 0 | +\nf(x) | -1 | 2 | -inf | +inf | 3 | 4"}
        ok_markdown = {"q": "Cho bảng biến thiên:\n\n| x | -inf | | -1 | | 1 | | +inf |\n|---|---|---|---|---|---|---|---|\n"
                            "| f'(x) | | + | 0 | - | 0 | + | |\n| f(x) | -inf | -> | 3 | -> | -1 | -> | +inf |\n\nChọn đáp án."}
        for q in (ok_plain, ok_asym, ok_markdown):
            self.assertEqual(_bbt_direction_conflict(q), "", q)


class GraphExtremaAndMarkdownBbtTests(unittest.TestCase):
    def _q(self, ans):
        return {"q": "Cho hàm số $y = f(x)$ liên tục trên $\mathbb{R}$ và có đồ thị như hình vẽ. Gọi $M, m$ lần lượt là "
                     "giá trị lớn nhất và giá trị nhỏ nhất của hàm số trên đoạn $[-1; 2]$. Tính $M + m$.",
                "opt": ["A. 2.", "B. 4.", "C. 0.", "D. 6."], "ans": ans,
                "f": {"type": "func_3", "a": 1, "b": -3, "c": 0, "d": 2}}

    def test_wrong_key_against_drawn_graph_is_blocked(self):
        from services.math_conditions import math_condition_conflict
        # Ca thật 17/11/2026: y = x^3 - 3x^2 + 2 trên [-1; 2] cho M + m = 0, khóa ghi A (2).
        self.assertEqual(math_condition_conflict(self._q("A")), "graph_interval_extrema_answer_mismatch")
        self.assertEqual(math_condition_conflict(self._q("C")), "")

    def test_markdown_table_in_stem_becomes_drawable_bbt(self):
        from services.context_recovery import recover_visual
        q = {"q": ("Cho hàm số $y = f(x)$ có bảng biến thiên như sau:\n\n| x | -inf | | -1 | | 1 | | +inf |\n"
                   "|---|------|---|----|---|---|---|------|\n| f'(x) | | + | 0 | - | 0 | + | |\n"
                   "| f(x) | -inf | -> | 3 | -> | -1 | -> | +inf |\n\nHàm số đã cho đồng biến trên khoảng nào?"),
             "opt": ["A. $(-1; 1)$.", "B. $(1; +\infty)$.", "C. $(-1; 3)$.", "D. $(-\infty; 1)$."], "ans": "B"}
        r = recover_visual(q, "Toán học", 12)
        self.assertEqual(r["bbt"], "x | -inf | -1 | 1 | +inf\nf'(x) | + | 0 | - | 0 | +\nf(x) | -inf | 3 | -1 | +inf")
        self.assertNotIn("|", r["q"])
        before, after = split_stem_at_visual(r["q"])
        self.assertTrue(before.endswith("như sau:"))
        self.assertTrue(after.startswith("Hàm số đã cho"))


class StemTableCleanupTests(unittest.TestCase):
    """Ca thật đề 6 (17/11/2026): rác nối chuỗi '" + "', bảng xét dấu 2 dòng, bảng trùng với trường bbt."""

    def test_json_concat_garbage_and_sign_table(self):
        from services.context_recovery import recover_visual
        q = {"q": 'Cho hàm số $y = f(x)$ liên tục trên $\mathbb{R}$ và có bảng xét dấu đạo hàm như sau:\n\n" + '
                  '"x | -inf | -2 | 0 | 2 | +inf\nf\'(x) | - | 0 | + | 0 | - | 0 | +\n\n" + "Hàm số đã cho có bao nhiêu điểm cực tiểu?',
             "opt": ["A. $1$", "B. $2$", "C. $3$", "D. $4$"], "ans": "B"}
        r = recover_visual(q, "Toán học", 12)
        self.assertNotIn('" + "', r["q"])
        self.assertEqual(r["bbt"], "x | -inf | -2 | 0 | 2 | +inf\nf'(x) | - | 0 | + | 0 | - | 0 | +")
        self.assertEqual(split_stem_at_visual(r["q"])[1], "Hàm số đã cho có bao nhiêu điểm cực tiểu?")

    def test_table_text_duplicating_bbt_field_is_removed_from_stem(self):
        from services.context_recovery import recover_visual
        table = "x | -inf | 0 | 1 | +inf\ny' | - | || - | 0 | +\ny | 2 | || +inf | -1 | +inf"
        q = {"q": "Cho hàm số có bảng biến thiên:\n\n" + table + "\n\nXét các mệnh đề sau:", "bbt": table,
             "stmts": [{"t": "a", "a": True}]}
        r = recover_visual(q, "Toán học", 12)
        self.assertEqual(r["bbt"], table)
        self.assertNotIn("|", r["q"])
        self.assertEqual(split_stem_at_visual(r["q"]), ("Cho hàm số có bảng biến thiên:", "Xét các mệnh đề sau:"))


if __name__ == "__main__":
    unittest.main()
