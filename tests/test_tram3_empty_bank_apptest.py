# -*- coding: utf-8 -*-
"""Kho đề trống không ảnh hưởng Trạm 3 đơn giản: vẫn một nút Sinh đề, không radio hình thức."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3EmptyBankAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_empty_bank.db")
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

    def _open(self, grade_label, subject):
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

    def test_empty_bank_keeps_simple_sinh_de(self):
        from services.academic_context import subjects_for_grade

        with patch("real_exam_engine.get_baseline_full_exams", return_value=[]):
            for grade in (6, 9, 12):
                subjects = subjects_for_grade(grade)
                at = self._open(f"Lớp {grade}", subjects[0])
                for subject in subjects:
                    with self.subTest(subject=subject, grade=grade):
                        if subject != subjects[0]:
                            next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run(timeout=90)
                        self.assertEqual([e.message for e in at.exception], [])
                        self.assertEqual(at.session_state.get("exam_state"), "config")
                        self.assertFalse(any(r.label == "Lựa chọn hình thức đề thi:" for r in at.radio))
                        sinh = [b.label for b in at.button if b.label == "🚀 Sinh đề"]
                        self.assertEqual(sinh, ["🚀 Sinh đề"], msg=f"{subject} L{grade}")
                        old = [
                            b.label
                            for b in at.button
                            if any(n in b.label for n in ("Trộn Siêu Đề", "Trích Xuất Đề", "Mở đề gốc", "Khởi Tạo Đề"))
                        ]
                        self.assertEqual(old, [], msg=f"{subject} L{grade}")


if __name__ == "__main__":
    unittest.main()
