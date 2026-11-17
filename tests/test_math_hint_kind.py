# -*- coding: utf-8 -*-
"""Gợi ý dự phòng môn Toán chia theo bản chất thao tác, không phải nhãn NB/TH/VD (owner 17/11/2026).

Lỗi cũ: mọi câu Toán rơi vào một câu mẫu "thay hệ số của hàm này", kể cả câu lý thuyết hình học.
"""
import unittest

from services.socratic_context import _plain_midwife, math_hint_kind


class MathHintKind(unittest.TestCase):
    def test_theory_question_never_mentions_formula(self):
        q = {"q": r"Điều kiện để đường thẳng $a$ song song với mặt phẳng $(\alpha)$ là", "level": "NB"}
        self.assertEqual(math_hint_kind(q), "theory")
        hint = _plain_midwife(q, "Toán học")
        for word in ("công thức", "thay số", "hệ số"):
            self.assertNotIn(word, hint)

    def test_one_step_standard_deviation(self):
        q = {"q": "Mẫu số liệu ghép nhóm có phương sai bằng 9. Độ lệch chuẩn của mẫu là", "level": "NB"}
        self.assertEqual(math_hint_kind(q), "one_step")
        hint = _plain_midwife(q, "Toán học")
        self.assertIn(r"\sqrt{s^2}", hint)
        self.assertNotIn("3", hint.replace("s^2", ""))  # không lộ đáp số

    def test_one_step_vector_coordinates(self):
        q = {"q": r"Cho $\vec{u}=(3;-1;2)$ và $A(0;-1;1)$. Tọa độ điểm $B$ thỏa $\vec{AB}=\vec{u}$ là"}
        self.assertEqual(math_hint_kind(q), "one_step")
        self.assertIn("x_B-x_A", _plain_midwife(q, "Toán học"))

    def test_multi_step_gets_route(self):
        q = {"q": r"Tìm giá trị lớn nhất của hàm số $y=x^3-3x+1$ trên đoạn $[0;2]$.", "level": "TH"}
        self.assertEqual(math_hint_kind(q), "multi_step")
        hint = _plain_midwife(q, "Toán học")
        self.assertIn("đầu mút", hint)
        self.assertNotIn("bậc hai", hint)  # hàm bậc ba không được gọi là bậc hai
        self.assertNotIn("\\'", hint)
        self.assertNotIn("thay hệ số của hàm này", hint)


if __name__ == "__main__":
    unittest.main()
