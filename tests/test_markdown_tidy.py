# -*- coding: utf-8 -*-
import unittest

from services.markdown_tidy import tidy_stray_bullets


class TidyStrayBullets(unittest.TestCase):
    def test_screenshot_case(self):
        raw = ("**Hướng dẫn giải:**\n\n*   *\n\n**Bước 1:** * Xét hai tam giác $ABC$ và $MNP$.\n\n*   *\n\n"
               r"**Bước 2:** * Theo trường hợp c.c.c, $\Delta ABC=\Delta MNP$.")
        out = tidy_stray_bullets(raw)
        self.assertNotIn("*   *", out)
        self.assertIn("**Bước 1:** Xét hai tam giác", out)
        self.assertIn("**Bước 2:** Theo", out)

    def test_keeps_real_markdown_and_math(self):
        raw = "- *nghiêng* và **đậm**\n* Ý một\n$a * b$ và $$x * y$$"
        self.assertEqual(tidy_stray_bullets(raw), raw)

    def test_bullet_followed_by_lone_star(self):
        self.assertEqual(tidy_stray_bullets("* * Nội dung"), "* Nội dung")


if __name__ == "__main__":
    unittest.main()


class VietnameseInMath(unittest.TestCase):
    def test_wraps_vietnamese_words(self):
        from services.markdown_tidy import wrap_vietnamese_in_math
        out = wrap_vietnamese_in_math(r"$\left[\begin{array}{l}x=-1 \text{ (loại)}\x=3 (thỏa mãn)\end{array}\right.$")
        self.assertIn(r"\text{thỏa mãn}", out)
        self.assertIn(r"\text{ (loại)}", out)  # đã bọc sẵn thì giữ nguyên
        self.assertEqual(wrap_vietnamese_in_math(r"$y=x^3-3x+\frac{1}{2}$"), r"$y=x^3-3x+\frac{1}{2}$")
        self.assertEqual(wrap_vietnamese_in_math("Không có công thức"), "Không có công thức")
