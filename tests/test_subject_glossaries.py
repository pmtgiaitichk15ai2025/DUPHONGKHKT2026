# -*- coding: utf-8 -*-
"""Mọi bảng thuật ngữ Anh–Việt (owner 19/11/2026): chỉ từ đã đối chiếu/đã duyệt mới lên phiếu in."""
import json
import pathlib
import unittest

from services.subject_glossary import APPROVED, approved_terms, terms_in

DIR = pathlib.Path("data/subject_glossary")
VALID = APPROVED | {"can_duyet"}


class Glossaries(unittest.TestCase):
    def test_index_files_and_statuses(self):
        index = json.loads((DIR / "index.json").read_text(encoding="utf-8"))
        for subject, grades in index.items():
            if subject.startswith("_"):
                continue
            for grade, name in grades.items():
                doc = json.loads((DIR / name).read_text(encoding="utf-8"))
                self.assertEqual((doc["subject"], str(doc["grade"])), (subject, grade), name)
                for t in doc["terms"]:
                    self.assertIn(t["status"], VALID, (name, t["vi"]))
                    if t["status"] in APPROVED:
                        self.assertTrue(t["sources"], (name, t["vi"]))
                anchors = doc.get("anchors") or {}
                self.assertIn("32/2018/TT-BGDĐT", anchors.get("program", ""), name)   # neo CT GDPT 2018
                self.assertTrue(anchors.get("textbook") and anchors.get("curriculum_topics"), name)
                vi = [t["vi"].casefold() for t in doc["terms"]]
                self.assertEqual(len(vi), len(set(vi)), f"{name}: trùng thuật ngữ")

    def test_pending_terms_never_printed(self):
        doc = json.loads((DIR / "congnghe_12.json").read_text(encoding="utf-8"))
        pending = [t["vi"] for t in doc["terms"] if t["status"] == "can_duyet"]
        approved_terms.cache_clear()
        printed = [vi for vi, _ in approved_terms("Công nghệ", 12)]
        self.assertFalse(set(pending) & set(printed))

    def test_known_traps(self):
        """Bẫy đã gặp khi đối chiếu: cực âm/dương ≠ cathode/anode ở pin; 'quy tắc nhân' ≠ product rule đạo hàm."""
        approved_terms.cache_clear()
        chem = dict(approved_terms("Hóa học", 12))
        self.assertNotIn("Cực âm", chem)
        self.assertEqual(dict(approved_terms("Toán học", 10)).get("Quy tắc nhân"), "rule of product")
        self.assertEqual(terms_in("Sản phẩm vượt trội; mặt trời lặn.", "Sinh học", 12), [])


    def test_translation_uses_shared_curriculum_anchor(self):
        """Lượt dịch nhận đúng khối neo CT2018/KNTT/pháp quy của lượt sinh bài, không bộ căn cứ thứ hai."""
        from services.curriculum_policy import policy_prompt
        from services.lesson_translation import translation_request
        system, _ = translation_request([("a", "Tìm tiệm cận đứng.")], "Toán học", 12, "Khảo sát hàm số")
        self.assertTrue(system.startswith(policy_prompt("Toán học", 12, 1, "Khảo sát hàm số")))
        self.assertIn("CHỈ DỊCH SONG NGỮ", system)
        self.assertIn("CT GDPT 2018 và sách KNTT", system)


    def test_provisional_terms_are_declared_as_known_issues(self):
        """Owner 19/11/2026: từ chưa chắc vẫn dùng nhưng phải ghi rõ tồn tại để vá theo phản hồi."""
        for name in ("vatly_12.json", "hoahoc_12.json", "sinhhoc_12.json", "tinhoc_12.json", "congnghe_12.json", "dialy_12.json"):
            doc = json.loads((DIR / name).read_text(encoding="utf-8"))
            provisional = [t for t in doc["terms"] if t.get("provisional")]
            self.assertTrue(provisional, name)
            self.assertTrue(any("provisional" in x for x in doc["known_issues"]), name)
            self.assertTrue(any("Chưa đối chiếu từng trang SGK" in x for x in doc["known_issues"]), name)

    def test_term_feedback_uses_existing_channel(self):
        from services.lesson_translation import build_term_feedback_entry
        e = build_term_feedback_entry(subject="Vật lý", grade=12, topic="Từ trường", text="cảm ứng từ")
        self.assertEqual((e["type"], e["category"]), ("USER_FEEDBACK", "Thuật ngữ song ngữ"))
        src = pathlib.Path("app.py").read_text(encoding="utf-8")
        self.assertIn("sync_event(build_term_feedback_entry(", src)


if __name__ == "__main__":
    unittest.main()
