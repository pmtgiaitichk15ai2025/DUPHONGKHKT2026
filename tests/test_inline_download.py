# -*- coding: utf-8 -*-
import base64
import json
import unittest

from services.inline_download import inline_download_links
from services.lesson_export import handwritten_prompt


class InlineDownload(unittest.TestCase):
    def test_link_embeds_exact_bytes(self):
        data = "Tiếng Việt có dấu".encode("utf-8")
        out = inline_download_links([("Tệp", data, 'a"b.md', "text/markdown")])
        self.assertIn('download="a&quot;b.md"', out)
        self.assertIn(base64.b64encode(data).decode(), out)

    def test_empty_or_huge_skipped(self):
        self.assertEqual(inline_download_links([("x", b"", "x.md", "text/markdown")]), "")


class OwnerHandwrittenTemplate(unittest.TestCase):
    def test_prompt_uses_owner_template_and_keeps_system_rules(self):
        prompt = json.loads(handwritten_prompt("Toán học", 10, "Bài 14", "Nội dung bài"))
        self.assertEqual(prompt["system_name"], "MASTER_HANDWRITTEN_EXAM_NOTEBOOK_GENERATOR")
        self.assertEqual(prompt["USER_INPUTS"]["NOI_DUNG_DE_KIEM_TRA"], "Nội dung bài")
        self.assertIn("Bài 14", prompt["USER_INPUTS"]["TIEU_DE"])
        self.assertIn("NEGATIVE_PROMPT", prompt)
        self.assertTrue(prompt["rules"])


if __name__ == "__main__":
    unittest.main()
