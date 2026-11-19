# -*- coding: utf-8 -*-
"""Quyết định chủ dự án 19/11/2026: môn nhạy cảm không song ngữ; văn phong Nam Bộ lời thầy;
khung khẩn cấp ấm áp cố định; danh bạ trường ẩn người bị nhắc tên."""
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")


class SensitiveSubjects(unittest.TestCase):
    def test_no_bilingual_for_politics_law_literature_history(self):
        from services.lesson_translation import SENSITIVE_NOTE, bilingual_allowed, translation_request
        for s in ("Lịch sử", "Giáo dục kinh tế và pháp luật", "Ngữ văn", "Giáo dục công dân"):
            self.assertFalse(bilingual_allowed(s), s)
            with self.assertRaises(ValueError):
                translation_request([("a", "x")], s, 12)
        self.assertTrue(bilingual_allowed("Toán học"))
        self.assertIn("st.info(SENSITIVE_NOTE)", SRC)
        self.assertIn("giáo viên bộ môn duyệt", SENSITIVE_NOTE)


class SouthernTeacherVoice(unittest.TestCase):
    def test_rule_is_idempotent_and_on_both_text_paths_not_json(self):
        from services.voice_style import SOUTHERN_TEACHER_MARKER, with_southern_teacher_voice
        once = with_southern_teacher_voice("SI")
        self.assertEqual(with_southern_teacher_voice(once), once)
        self.assertIn("chuẩn SGK", once)
        self.assertIn(SOUTHERN_TEACHER_MARKER, once)
        call = SRC.split("def call_gemini_with_fallback", 1)[1].split("\ndef ", 1)[0]
        stream = SRC.split("def stream_gemini_with_fallback", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if not json_mode:", call.split("with_southern_teacher_voice", 1)[0][-400:])
        self.assertIn("effective_si = with_southern_teacher_voice(effective_si)", stream)
        # Trước vòng thử model → mọi model dự phòng nhận như nhau.
        self.assertLess(stream.index("with_southern_teacher_voice(effective_si)"), stream.index("for current_model in model_queue"))


class CrisisTemplate(unittest.TestCase):
    def test_warm_fixed_with_hotlines(self):
        from services.school_counseling import crisis_resources_md
        t = crisis_resources_md()
        for must in ("thầy thương em", "Em không có lỗi", "**111**", "**115**", "không phải chịu một mình"):
            self.assertIn(must, t)
        self.assertEqual(t, crisis_resources_md())   # cố định, không AI


class SchoolContacts(unittest.TestCase):
    RAW = [{"name": "Phan Minh Trí", "role": "Thầy tư vấn học đường", "phone": "0900 000 001", "hours": "Giờ hành chính"},
           {"name": "Nguyễn Văn A", "role": "Cán bộ Đoàn trường", "phone": "0900 000 002"},
           {"name": "Lê Thị B", "phone": ""}]

    def test_hides_person_student_names_and_skips_incomplete(self):
        from services.school_contacts import school_contacts_md
        md = school_contacts_md(self.RAW, "em bị thầy trí dạy toán làm hại")
        self.assertNotIn("0900 000 001", md)
        self.assertIn("0900 000 002", md)
        self.assertNotIn("Lê Thị B", md)
        full = school_contacts_md(self.RAW, "em buồn quá")
        self.assertIn("0900 000 001", full)
        self.assertIn("(Giờ hành chính)", full)
        self.assertEqual(school_contacts_md([], "x"), "")

    def test_wired_into_both_safety_paths(self):
        self.assertIn("_safe = crisis_resources_md() + _t4_school_contacts(_user_msg)", SRC)
        self.assertIn("_reply = violence_safety_block() + _t4_school_contacts(_user_msg)", SRC)
        self.assertIn('st.secrets.get("SCHOOL_SUPPORT_CONTACTS", [])', SRC)


if __name__ == "__main__":
    unittest.main()
