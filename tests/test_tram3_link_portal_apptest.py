# -*- coding: utf-8 -*-
"""AppTest: Trạm 3 đơn giản không còn panel Quét Đề Link trên phòng thi học sinh."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3LinkPortalAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_link_portal.db")
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
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run(timeout=120)
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run(timeout=120)
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run(timeout=120)
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run(timeout=120)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_student_tab_has_no_link_scan_panel(self):
        at = self._open("Lớp 8", "Toán học")
        self.assertEqual([e.message for e in at.exception], [])
        self.assertFalse(any(r.label == "Lựa chọn hình thức đề thi:" for r in at.radio))
        self.assertFalse(any("Nhập Link bài viết" in t.label for t in at.text_input))
        self.assertFalse(any("Chọn chuyên trang" in s.label for s in at.selectbox))
        self.assertTrue(any(b.label == "🚀 Sinh đề" for b in at.button))
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Tin học").run(timeout=120)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertFalse(any(r.label == "Lựa chọn hình thức đề thi:" for r in at.radio))
        self.assertTrue(any(b.label == "🚀 Sinh đề" for b in at.button))



from tests.exam_cache_isolation import setUpModule, tearDownModule  # noqa: F401,E402

if __name__ == "__main__":
    unittest.main()
