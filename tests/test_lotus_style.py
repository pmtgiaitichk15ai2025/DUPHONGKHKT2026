# -*- coding: utf-8 -*-
"""Kiểu phiếu Sen Việt + từ vựng Anh–Việt chuyên ngành đã đối chiếu (owner 19/11/2026)."""
import json
import pathlib
import unittest

from services.subject_glossary import APPROVED, approved_terms, terms_in

LESSON = ("### PHẦN 1: BÀI HỌC\n\n#### Khởi động\nTìm **tiệm cận đứng** và tính **đạo hàm** của hàm số $y=\dfrac{2x+1}{x-1}$, "
          "lập **bảng biến thiên** rồi vẽ đồ thị hàm số.\n")


class Glossary(unittest.TestCase):
    def test_only_reviewed_terms_and_british_spelling(self):
        doc = json.loads(pathlib.Path("data/subject_glossary/toan_12.json").read_text(encoding="utf-8"))
        self.assertTrue(all(t["status"] in APPROVED and t["sources"] for t in doc["terms"]))
        en = dict(approved_terms("Toán học", 12))
        self.assertEqual(en["Bảng biến thiên"], "table of variations")
        self.assertEqual(en["Hai vectơ cùng phương"], "parallel vectors")
        self.assertEqual(en["Tối ưu hóa"], "optimisation")

    def test_longest_phrase_wins_and_unknown_subject_is_empty(self):
        got = terms_in("Tìm tiệm cận đứng của đồ thị.", "Toán học", 12)
        self.assertIn(("Tiệm cận đứng", "vertical asymptote"), got)
        self.assertNotIn("Tiệm cận", [vi for vi, _ in got])
        self.assertEqual(terms_in("Tìm tiệm cận đứng", "Vật lý", 12), [])
        self.assertEqual(terms_in("Tìm tiệm cận đứng", "Toán học", 11), [])


class LotusExport(unittest.TestCase):
    def test_lotus_style_vocab_and_graph_colours(self):
        from services.lesson_export import build_lesson_html
        doc = build_lesson_html("Toán học", 12, "Khảo sát hàm số", LESSON, "lotus")
        self.assertIn('class="handwritten lotus"', doc)   # kế thừa vở ô ly + gáy lò xo
        self.assertIn("#075B9A", doc)
        self.assertIn("counter(pages)", doc)
        self.assertIn("vocab-leaf", doc)
        self.assertIn("<b>vertical asymptote</b> – Tiệm cận đứng", doc)
        self.assertIn("MATHEMATICAL VOCABULARY", doc)
        self.assertIn("g[data-asymptote] line{stroke:#dc2626}", doc)
        self.assertNotIn(".handwritten.lotus .vocab-leaf,.pond", doc)
        self.assertIn("page-lotus", doc)
        self.assertNotIn("Thiết kế bởi", doc)

    def test_other_styles_unchanged_no_vocab(self):
        from services.lesson_export import build_lesson_html
        doc = build_lesson_html("Toán học", 12, "Khảo sát hàm số", LESSON, "color")
        self.assertNotIn('<aside class="vocab-leaf"', doc)

    def test_app_offers_sen_viet_option(self):
        src = pathlib.Path("app.py").read_text(encoding="utf-8")
        self.assertIn('"🌸 Infographic Sen Việt"', src)
        self.assertIn('"lotus" if "Sen Việt" in export_mode', src)



class Bilingual(unittest.TestCase):
    def setUp(self):
        from services.lesson_translation import lesson_blocks
        self.blocks = lesson_blocks("Toán học", 12, "Khảo sát hàm số", LESSON)

    def test_blocks_hide_formulas_behind_tokens(self):
        text = dict(self.blocks)
        para = [t for t in text.values() if "tiệm cận đứng" in t.lower()][0]
        self.assertIn("⟦0⟧", para)
        self.assertNotIn("dfrac", para)

    def test_programmatic_checks_do_not_trust_ai(self):
        from services.lesson_translation import check_translation
        vi = "Tìm tiệm cận đứng của ⟦0⟧."
        self.assertEqual(check_translation(vi, "Find the vertical asymptote of ⟦0⟧.", "Toán học", 12)[1], [])
        self.assertIsNone(check_translation(vi, "Find the vertical asymptote.", "Toán học", 12)[0])   # mất công thức
        self.assertIn("glossary:Tiệm cận đứng→vertical asymptote",
                      check_translation(vi, "Find the upright line of ⟦0⟧.", "Toán học", 12)[1])

    def test_broken_json_drops_batch_softly_and_sheet_still_builds(self):
        from services.lesson_export import build_lesson_html
        from services.lesson_translation import merge_response
        self.assertEqual(merge_response(self.blocks, "{not json", "Toán học", 12), {})
        doc = build_lesson_html("Toán học", 12, "Khảo sát hàm số", LESSON, "lotus", translations={"x": {"en": "y", "flags": []}})
        self.assertIn("chưa có bản tiếng Anh", doc)

    def test_injection_keeps_original_math(self):
        from services.lesson_export import build_lesson_html
        from services.lesson_translation import merge_response
        fake = {bid: (t.replace("Tìm", "Find") if "⟦" in t else "EN " + t) for bid, t in self.blocks}
        tr = merge_response(self.blocks, fake, "Toán học", 12)
        doc = build_lesson_html("Toán học", 12, "Khảo sát hàm số", LESSON, "lotus", translations=tr)
        self.assertIn('<span class="en" lang="en"', doc)
        self.assertIn("EN Khảo sát hàm số", doc)   # tiêu đề bài song ngữ
        en_part = doc.split('<span class="en" lang="en"', 2)[2]
        self.assertIn('class="lesson-math"', en_part.split("</span></p>", 1)[0] + "</span>")

    def test_system_instruction_carries_absolute_rules_and_glossary(self):
        from services.lesson_translation import translation_request
        system, user = translation_request(self.blocks, "Toán học", 12)
        for must in ("QUY TẮC TUYỆT ĐỐI", "kể cả model dự phòng", "⟦số⟧", "British English", "vertical asymptote"):
            self.assertIn(must, system)

    def test_app_uses_shared_fallback_gate(self):
        src = pathlib.Path("app.py").read_text(encoding="utf-8")
        self.assertIn("call_gemini_with_fallback(_user_tr, system_instruction=_sys_tr, json_mode=True)", src)
        self.assertIn("cleaned_p1, export_style, _lotus_tr)", src)


class ArtPrompt(unittest.TestCase):
    def test_art_prompt_forbids_text_and_formulas(self):
        import json
        from services.lotus_style import illustration_prompt
        doc = json.loads(illustration_prompt("Toán học", 12, "Khảo sát hàm số", LESSON))
        self.assertIn("TUYỆT ĐỐI KHÔNG vẽ chữ, chữ số, công thức, đồ thị, bảng hay ký hiệu toán học.", doc["hard_rules"])
        self.assertEqual(doc["scenes"][0]["based_on_section"], "Khởi động")
        self.assertNotIn("dfrac", json.dumps(doc))


if __name__ == "__main__":
    unittest.main()
