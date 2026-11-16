# -*- coding: utf-8 -*-
"""AppTest: nút Sinh đề Trạm 3 → testing đúng môn/lớp (mock AI JSON)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def _assert_subject_topics(test, at, subject: str, grade: int):
    from data.curriculum_data import BIGDATA_CURRICULUM

    curr = BIGDATA_CURRICULUM[subject]
    if grade >= 12:
        expected = list(curr[12]) + list(curr[11]) + list(curr[10])
        first = f"[Lớp 12] {curr[12][0]}"
    elif grade == 11:
        expected = list(curr[11]) + list(curr[10])
        first = f"[Lớp 11] {curr[11][0]}"
    else:
        expected = list(curr[grade])
        first = f"[Lớp {grade}] {curr[grade][0]}"
    labels = [str(c.label) for c in at.checkbox]
    missing = [name for name in expected if name not in labels]
    test.assertEqual(missing, [], msg=f"{subject} L{grade} thiếu checkbox: {missing[:3]}")
    selected = at.session_state.get("policy_selected_topics") or []
    test.assertIn(first, selected, msg=f"{subject} L{grade} không chọn sẵn {first}")


def _assert_simple_controls(test, at, subject: str, grade: int):
    test.assertFalse(any(r.label == "Lựa chọn hình thức đề thi:" for r in at.radio))
    labels = [b.label for b in at.button]
    test.assertEqual(
        sum(1 for lab in labels if lab == "🚀 Sinh đề"),
        1,
        msg=f"{subject} L{grade} thiếu đúng 1 nút Sinh đề",
    )
    test.assertFalse(any("Trộn Siêu Đề" in lab or "Trích Xuất Đề" in lab for lab in labels))


def _fake_exam(subject: str, grade: int, counts=(3, 1, 0)):
    n1, n2, n3 = counts
    if subject == "Ngữ văn":
        return {
            "code": f"MOCK-{grade}",
            "subject": subject,
            "grade": grade,
            "part_doc_hieu": {
                "text": "Ngữ liệu QA",
                "author": "",
                "source": "tự sáng tác",
                "questions": [{"q": "Đọc hiểu?", "ans": "rubric", "point": 4.0, "explain": "x"}],
            },
            "part_viet": [{"q": "Viết", "ans": "rubric", "point": 6.0, "explain": "x"}],
        }
    return {
        "code": f"MOCK-{grade}",
        "subject": subject,
        "grade": grade,
        "p1": [
            {
                "q": f"Câu TN {i+1} {subject} L{grade}",
                "opt": ["A.1", "B.2", "C.3", "D.4"],
                "ans": "B",
                "subject": subject,
                "explain": "x",
            }
            for i in range(n1)
        ],
        "p2": [
            {
                "q": f"Câu ĐS {i+1}",
                "stmts": [
                    {"t": "a", "a": True},
                    {"t": "b", "a": False},
                    {"t": "c", "a": True},
                    {"t": "d", "a": False},
                ],
                "subject": subject,
                "explain": "x",
            }
            for i in range(n2)
        ],
        "p3": [{"q": f"TLN {i+1}", "ans": "1", "subject": subject, "explain": "x"} for i in range(n3)],
    }


class Tram3SinhDeButtonAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_sinh_btn.db")
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

    def _open_tram3(self, grade_label: str, subject: str):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.secrets["GEMINI_API_KEY"] = "qa-fake-key"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def _click_sinh_de(self, at, subject, grade, counts):
        if subject != "Ngữ văn":
            by_label = {n.label: int(n.value) for n in at.number_input}
            counts = (
                by_label["Số câu TN P.I:"],
                by_label["Số câu Đ/S P.II:"],
                by_label["Số câu TLN P.III:"],
            )
        fake = _fake_exam(subject, grade, counts)

        def _gen(*_a, **_k):
            return json.dumps(fake, ensure_ascii=False)

        with patch("google.genai.Client") as client:
            response = client.return_value.__enter__.return_value.models.generate_content
            response.return_value = SimpleNamespace(text=_gen(), candidates=[])
            # Also cover non-context-manager Client paths used by some app versions.
            client.return_value.models.generate_content.return_value = SimpleNamespace(
                text=_gen(), candidates=[]
            )
            with patch("app.call_gemini_with_fallback", side_effect=lambda *a, **k: _gen()):
                btn = next(b for b in at.button if b.label == "🚀 Sinh đề")
                btn.click().run(timeout=90)
        return at

    def test_sinh_de_starts_testing_for_matrix_cells(self):
        from services.academic_context import subjects_for_grade

        cells = []
        for grade in (6, 8, 9, 10, 12):
            for subject in subjects_for_grade(grade):
                if subject == "Ngữ văn":
                    continue
                counts = (4, 0, 0) if subject == "Tiếng Anh" else (3, 1, 0)
                cells.append((f"Lớp {grade}", subject, grade, counts))
        self.assertGreaterEqual(len(cells), 20)
        for grade_label, subject, grade, counts in cells:
            with self.subTest(subject=subject, grade=grade):
                at = self._open_tram3(grade_label, subject)
                _assert_subject_topics(self, at, subject, grade)
                _assert_simple_controls(self, at, subject, grade)
                at = self._click_sinh_de(at, subject, grade, counts)
                self.assertEqual([e.message for e in at.exception], [])
                self.assertEqual(at.session_state.get("exam_state"), "testing")
                exam = at.session_state.get("exam_data") or {}
                self.assertEqual(exam.get("subject"), subject)
                radios = [r for r in at.radio if str(r.label).startswith("Lựa chọn câu")]
                self.assertGreaterEqual(len(radios), 1)

    def test_sinh_de_grades_7_and_11(self):
        from services.academic_context import subjects_for_grade

        cells = []
        for grade in (7, 11):
            for subject in subjects_for_grade(grade):
                if subject == "Ngữ văn":
                    continue
                counts = (4, 0, 0) if subject == "Tiếng Anh" else (3, 1, 0)
                cells.append((f"Lớp {grade}", subject, grade, counts))
        for grade_label, subject, grade, counts in cells:
            with self.subTest(subject=subject, grade=grade):
                at = self._open_tram3(grade_label, subject)
                _assert_subject_topics(self, at, subject, grade)
                _assert_simple_controls(self, at, subject, grade)
                at = self._click_sinh_de(at, subject, grade, counts)
                self.assertEqual([e.message for e in at.exception], [])
                self.assertEqual(at.session_state.get("exam_state"), "testing")
                self.assertEqual((at.session_state.get("exam_data") or {}).get("subject"), subject)


if __name__ == "__main__":
    unittest.main()
