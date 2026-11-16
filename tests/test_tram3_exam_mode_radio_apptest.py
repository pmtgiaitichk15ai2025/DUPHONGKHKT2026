# -*- coding: utf-8 -*-
"""AppTest: Trạm 3 đơn giản — không radio hình thức; một nút Sinh đề gửi đúng môn."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3SimpleSinhDeAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_simple_sinh.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()
        if cls._prev_baseline is None:
            os.environ.pop("GSAI_LOAD_BASELINE_MASTER", None)
        else:
            os.environ["GSAI_LOAD_BASELINE_MASTER"] = cls._prev_baseline

    def _open(self, grade_label: str, subject: str):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_every_subject_has_one_sinh_de_and_no_mode_radio(self):
        from services.academic_context import subjects_for_grade

        # Representative cells (full 6–12×môn is covered by CI matrix elsewhere).
        sample_grades = (6, 9, 12)
        for grade in sample_grades:
            subjects = subjects_for_grade(grade)
            at = self._open(f"Lớp {grade}", subjects[0])
            for subject in subjects:
                with self.subTest(subject=subject, grade=grade):
                    if subject != subjects[0]:
                        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run(timeout=90)
                        self.assertEqual([e.message for e in at.exception], [])

                    self.assertFalse(
                        any(r.label == "Lựa chọn hình thức đề thi:" for r in at.radio),
                        msg=f"{subject} L{grade} vẫn còn radio hình thức",
                    )
                    sinh = [b for b in at.button if b.label == "🚀 Sinh đề"]
                    self.assertEqual(len(sinh), 1, msg=f"{subject} L{grade} cần đúng 1 nút Sinh đề")
                    self.assertFalse(
                        any(
                            any(n in b.label for n in ("Trộn Siêu Đề", "Trích Xuất Đề", "Mở đề gốc", "Khởi Tạo Đề", "AI Tạo Đề"))
                            for b in at.button
                        ),
                        msg=f"{subject} L{grade} còn nút chế độ cũ",
                    )

                    captions = " ".join(str(c.value) for c in at.caption)
                    self.assertIn("CT GDPT 2018", captions)
                    self.assertIn("KNTT", captions)

                    marker = f"ONLY {subject} L{grade}"
                    area = next(t for t in at.text_area if "Yêu cầu ma trận" in t.label)
                    area.set_value(marker).run(timeout=90)
                    self.assertEqual([e.message for e in at.exception], [])
                    seen = []

                    def _capture(subj, g, topics, counts, code, custom, pathway=""):
                        seen.append((subj, int(g), tuple(topics), str(custom or "")))
                        return ("qa-system", "qa-prompt")

                    with patch("services.curriculum_policy.exam_generation_request", side_effect=_capture):
                        sinh[0].click().run(timeout=90)
                    self.assertEqual([e.message for e in at.exception], [])
                    self.assertEqual(at.session_state.get("exam_state"), "config")
                    self.assertTrue(seen, msg=f"{subject} L{grade} không gọi yêu cầu AI")
                    self.assertEqual(seen[-1][0], subject)
                    self.assertEqual(seen[-1][1], grade)
                    self.assertTrue(any(f"Lớp {grade}" in t for t in seen[-1][2]), msg=seen[-1][2])
                    self.assertIn(marker, seen[-1][3])
                    self.assertIn("GEMINI_API_KEY", " ".join(str(e.value) for e in at.error))


if __name__ == "__main__":
    unittest.main()
