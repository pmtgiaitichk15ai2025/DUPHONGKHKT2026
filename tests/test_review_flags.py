# -*- coding: utf-8 -*-
"""Hai tồn tại 17/11/2026: khóa bài tối ưu/tham số chưa ai xác nhận; ngữ liệu Ngữ văn gán tác giả thật."""
import json
import unittest

from services.curriculum_policy import literature_source_notice
from services.independent_answer_check import (MISMATCH_MARK, UNVERIFIED_MARK, count_review_flags,
                                               mark_independent_mismatches)


def _exam():
    return {"p1": [{"q": "Giá trị lớn nhất của hàm số trên [0;2] là", "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "B"},
                   {"q": "Hàm số nào đồng biến?", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": "A"}],
            "p2": [],
            "p3": [{"q": "Có bao nhiêu giá trị nguyên của tham số m để hàm số đồng biến?", "ans": "4"},
                   {"q": "Tính đạo hàm tại x = 1.", "ans": "3"}]}


class UnverifiedHighRisk(unittest.TestCase):
    def _run(self, solved):
        return mark_independent_mismatches(_exam(), "Toán", 12, lambda s, u: json.dumps(solved))

    def test_null_on_high_risk_is_flagged_not_withheld(self):
        exam, report = self._run({"p1": [None, "A"], "p2": [], "p3": [None, None]})
        self.assertTrue(exam["p1"][0].get(UNVERIFIED_MARK))
        self.assertTrue(exam["p3"][0].get(UNVERIFIED_MARK))
        self.assertFalse(exam["p3"][1].get(UNVERIFIED_MARK))  # câu thường không bị gắn cờ
        self.assertFalse(any(q.get(MISMATCH_MARK) for q in exam["p1"] + exam["p3"]))
        self.assertEqual(len(report["unverified"]), 2)
        exam["independent_answer_check"] = report
        self.assertEqual(count_review_flags(exam), 2)

    def test_confirmed_answers_raise_no_flag(self):
        exam, report = self._run({"p1": ["B", "A"], "p2": [], "p3": ["4", "3"]})
        self.assertNotIn("unverified", report)
        self.assertEqual(count_review_flags(exam), 0)

    def test_too_many_mismatches_counts_for_teacher(self):
        exam, report = self._run({"p1": ["C", "B"], "p2": [], "p3": ["5", "3"]})
        self.assertEqual(report["status"], "too_many_mismatches_teacher_review")
        exam["independent_answer_check"] = report
        self.assertEqual(count_review_flags(exam), 3)


class LiteratureSource(unittest.TestCase):
    def test_real_author_needs_teacher_check(self):
        notice = literature_source_notice({"part_doc_hieu": {"author": "Xuân Quỳnh", "source": "Thơ Xuân Quỳnh"}})
        self.assertIn("Xuân Quỳnh", notice)

    def test_self_composed_passage_is_quiet(self):
        for author in ("Ngữ liệu biên soạn", "", "Khuyết danh"):
            self.assertEqual(literature_source_notice({"part_doc_hieu": {"author": author}}), "")
        self.assertEqual(literature_source_notice({"part_doc_hieu": {"author": "Nhóm GV", "source": "Biên soạn phục vụ luyện tập"}}), "")


if __name__ == "__main__":
    unittest.main()
