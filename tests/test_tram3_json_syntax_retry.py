# -*- coding: utf-8 -*-
"""Sinh đề: JSON sai cú pháp dùng chung đúng một lượt thử lại sẵn có; câu lỗi lẻ không hủy cả đề.

Ca thật 17/11/2026 (Lịch sử 12, Tin học 12, GDKT&PL 11, Địa lý 10): model dự phòng khi quá tải trả
JSON sai cú pháp, hoặc một câu thiếu khóa trắc nghiệm, làm hỏng cả lượt Sinh đề.
"""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from tests.exam_cache_isolation import setUpModule, tearDownModule  # noqa: F401


def _exam(n, bad_key_index=None):
    p1 = []
    for i in range(n):
        p1.append({"q": f"Sự kiện lịch sử thứ {i + 1} diễn ra năm nào?", "topic": "Lịch sử",
                   "opt": ["A. 1945", "B. 1954", "C. 1975", "D. 1986"],
                   "ans": "" if i == bad_key_index else "B.", "explain": "x", "hint": "Em nhớ lại mốc thời gian nhé."})
    return {"subject": "Lịch sử", "grade": 12, "p1": p1, "p2": [], "p3": []}


class Tram3JsonSyntaxRetry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "retry.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()

    def _open(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 12").run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Lịch sử").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run()
        for label, value in (("Số câu TN P.I:", 3), ("Số câu Đ/S P.II:", 0)):
            next(n for n in at.number_input if n.label == label).set_value(value)
        at.run()
        return at

    def _generate(self, at, responses):
        import real_exam_engine as engine
        with patch("google.genai.Client") as client, \
                patch.object(engine, "get_baseline_questions_pool", return_value={"p1": [], "p2": [], "p3": []}), \
                patch.object(engine, "generate_blended_real_exam", return_value=None):
            reply = client.return_value.__enter__.return_value.models.generate_content
            reply.side_effect = [SimpleNamespace(text=text, candidates=[]) for text in responses]
            next(b for b in at.button if b.label == "🚀 Sinh đề").click().run(timeout=120)
            return reply.call_count

    def test_broken_json_uses_the_existing_single_retry(self):
        at = self._open()
        good = json.dumps(_exam(3), ensure_ascii=False)
        solver = json.dumps({"p1": [{"work": "", "ans": "B"}] * 3, "p2": [], "p3": []})
        broken = good[:-40] + '"q" "thiếu dấu phẩy"' + good[-40:]
        calls = self._generate(at, [broken, good, solver])
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["exam_state"], "testing")
        self.assertEqual(len(at.session_state["exam_data"]["p1"]), 3)
        self.assertEqual(calls, 3)  # lần sinh + đúng một lần thử lại + lượt giải độc lập

    def test_one_question_without_key_does_not_cancel_exam(self):
        at = self._open()
        solver = json.dumps({"p1": [{"work": "", "ans": "B"}] * 3, "p2": [], "p3": []})
        self._generate(at, [json.dumps(_exam(3, bad_key_index=1), ensure_ascii=False), solver])
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["exam_state"], "testing")
        exam = at.session_state["exam_data"]
        self.assertEqual(len(exam["p1"]), 2)  # câu thiếu khóa được để riêng, không bịa đáp án A
        self.assertTrue(all(q["ans"] == "B" for q in exam["p1"]))
        self.assertEqual(exam["context_recovery"]["withheld"], 1)


if __name__ == "__main__":
    unittest.main()
