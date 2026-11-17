# -*- coding: utf-8 -*-
import unittest

from services.markdown_tidy import tidy_stray_bullets


class TidyStrayBullets(unittest.TestCase):
    def test_screenshot_case(self):
        raw = ("**Hướng dẫn giải:**\n\n*   *\n\n**Bước 1:** * Xét hai tam giác $ABC$ và $MNP$.\n\n*   *\n\n"
               "**Bước 2:** * Theo trường hợp c.c.c, $\Delta ABC=\Delta MNP$.")
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
