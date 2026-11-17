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


class GenericHintRejected(unittest.TestCase):
    """Ca thật web 17/11/2026: hint Đúng/Sai chung chung, không bám dữ kiện câu."""

    def test_generic_hints(self):
        from services.socratic_context import is_generic_hint
        stem = {"q": r"Cho hàm số $y=x^3-3x$. Xét tính đúng sai của các mệnh đề sau:",
                "stmts": [{"t": r"Hàm số nghịch biến trên khoảng $(-1;1)$."}]}
        self.assertTrue(is_generic_hint("Em hãy ôn lại các tính chất cơ bản của đồ thị hàm bậc ba để làm từng ý nhé.", stem))
        self.assertTrue(is_generic_hint("Em hãy giải phương trình đạo hàm và phương trình giao điểm một cách cẩn thận.", stem))
        self.assertFalse(is_generic_hint(r"Em tính $y'$ rồi xét dấu trên $(-1;1)$ nhé.", stem))
        theory = {"q": r"Điều kiện để đường thẳng $a$ song song với mặt phẳng $(\alpha)$ là"}
        self.assertFalse(is_generic_hint("Em nhớ lại định nghĩa: đường thẳng song song mặt phẳng thì có điểm chung không?", theory))


class OxyzTeacherHint(unittest.TestCase):
    """Ca thật web 17/11/2026 (Toán 12 Bài 8): câu u+v nhận câu mẫu chung 'một công thức áp dụng trực tiếp'."""

    def test_vector_sum(self):
        from services.socratic_context import build_tram3_socratic_guide
        q = {"q": r"Trong không gian $Oxyz$, cho hai vectơ $\vec{u}=(1;-2;3)$ và $\vec{v}=(2;1;-1)$. Tọa độ của vectơ $\vec{u}+\vec{v}$ là",
             "opt": ["A. $(3;-1;2)$.", "B. $(2;-2;-3)$.", "C. $(1;3;-4)$.", "D. $(-1;-3;4)$."], "ans": "A", "level": "NB"}
        hint = build_tram3_socratic_guide(q, subject="Toán học")
        self.assertIn("từng thành phần", hint)
        self.assertIn("?", hint)
        self.assertNotIn("một công thức áp dụng trực tiếp", hint)
        self.assertNotIn("3;-1;2", hint)

    def test_angle_and_midpoint(self):
        from services.socratic_context import build_tram3_socratic_guide
        angle = {"q": r"Trong không gian $Oxyz$, cho $\vec{a}=(1;0;1)$ và $\vec{b}=(0;1;1)$. Góc giữa hai vectơ $\vec{a}$ và $\vec{b}$ bằng",
                 "opt": [r"A. $30^\circ$.", r"B. $45^\circ$.", r"C. $90^\circ$.", r"D. $60^\circ$."], "ans": "D"}
        self.assertIn("góc giữa hai vectơ", build_tram3_socratic_guide(angle))
        mid = {"q": r"Trong không gian $Oxyz$, cho $A(1;3;-2)$ và $B(3;-1;4)$. Tọa độ trung điểm $M$ của đoạn thẳng $AB$ là",
               "opt": ["A. $(1;-2;3)$.", "B. $(2;1;1)$.", "C. $(4;2;2)$.", "D. $(2;2;2)$."], "ans": "B"}
        hint = build_tram3_socratic_guide(mid)
        self.assertIn("chính giữa", hint)
        self.assertNotIn("2;1;1", hint)


if __name__ == "__main__":
    unittest.main()
