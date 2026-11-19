# -*- coding: utf-8 -*-
"""Học liệu tiếng Anh uy tín theo chủ đề (owner 19/11/2026): chỉ đường tìm kiếm chính thức, không bịa link."""
import pathlib
import unittest
from urllib.parse import urlparse

from services.english_resources import english_keywords, english_resources, english_resources_html


class EnglishResources(unittest.TestCase):
    def test_keyword_priority_translation_then_glossary_then_fallback(self):
        self.assertEqual(english_keywords("Toán học", 12, "Nguyên hàm", title_en="Antiderivatives"), ("Antiderivatives", "translation"))
        self.assertEqual(english_keywords("Toán học", 12, "Nguyên hàm")[1], "glossary")
        self.assertIn("antiderivative", english_keywords("Toán học", 12, "Nguyên hàm")[0])
        kw, how = english_keywords("Ngữ văn", 12, "Thơ hiện đại")
        self.assertEqual(how, "fallback")
        self.assertTrue(kw.startswith("literature"))

    def test_only_official_search_hosts_for_every_subject(self):
        allowed = {"www.khanacademy.org", "www.bbc.co.uk", "www.ck12.org", "en.wikipedia.org", "www.youtube.com"}
        from services.english_resources import SUBJECT_EN
        for subject in SUBJECT_EN:
            for _, url in english_resources(subject, 10, "chủ đề")["links"]:
                self.assertIn(urlparse(url).netloc, allowed, (subject, url))
        self.assertIn("khanacademy.org/search?page_search_query=antiderivative",
                      english_resources_html("Toán học", 12, "Nguyên hàm"))

    def test_rendered_in_station1_next_to_video(self):
        src = pathlib.Path("app.py").read_text(encoding="utf-8")
        self.assertIn("english_resources_html(subject, grade_num, current_topic_name", src)


if __name__ == "__main__":
    unittest.main()
