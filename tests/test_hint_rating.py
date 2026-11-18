# -*- coding: utf-8 -*-
"""Nút 👍/👎 đánh giá gợi ý Socratic đi qua đường USER_FEEDBACK sẵn có (owner 17/11/2026)."""
import json
import unittest

from services.hint_rating import (HINT_RATING_CATEGORY, TOOLTIP_DOWN, TOOLTIP_UP,
                                  build_hint_rating_entry, hint_id)


class HintRatingEntry(unittest.TestCase):
    def test_up_entry_uses_existing_feedback_channel(self):
        e = build_hint_rating_entry(liked=True, station="Trạm 1", subject="Toán học", grade="Lớp 12",
                                    question_text="u+v là", hint="Em ơi, cộng từng thành phần?")
        self.assertEqual(e["type"], "USER_FEEDBACK")
        self.assertEqual(e["category"], HINT_RATING_CATEGORY)
        self.assertEqual(e["rating"], 5)
        detail = json.loads(e["detail"])
        self.assertEqual(detail["verdict"], "up")
        self.assertEqual(detail["reason"], "")
        self.assertEqual(detail["hint_id"], hint_id("Trạm 1", "u+v là", "Em ơi, cộng từng thành phần?"))

    def test_down_entry_keeps_reason(self):
        e = build_hint_rating_entry(liked=False, station="Trạm 3", subject="Toán học", grade="Lớp 12",
                                    question_text="q", hint="h", reason="Chung chung, không bám câu hỏi", note="x")
        detail = json.loads(e["detail"])
        self.assertEqual(e["rating"], 1)
        self.assertEqual(detail["verdict"], "down")
        self.assertEqual(detail["reason"], "Chung chung, không bám câu hỏi")

    def test_tooltips_say_what_the_button_does(self):
        for tip in (TOOLTIP_UP, TOOLTIP_DOWN):
            self.assertIn("Đánh giá lời hướng dẫn của hệ thống", tip)


class HintRatingLayout(unittest.TestCase):
    """Owner 18/11/2026: hai nút phải nằm ngang hàng, có nhãn luôn hiện (không chỉ tooltip)."""

    def test_buttons_in_one_horizontal_row_with_visible_label(self):
        import contextlib
        from services.hint_rating import render_hint_rating
        calls = []

        class FakeSt:
            session_state = {}

            def container(self, **kw):
                calls.append(('container', kw))
                return contextlib.nullcontext()

            def caption(self, text):
                calls.append(('caption', text))

            def button(self, label, key=None, help=None, width=None):
                calls.append(('button', label, help))
                return False

        render_hint_rating(FakeSt(), lambda e: None, key="k", station="Trạm 1", subject="Toán học",
                           grade="Lớp 12", question_text="q", hint="Em ơi?")
        container = [c for c in calls if c[0] == 'container'][0][1]
        self.assertTrue(container.get('horizontal'))
        self.assertFalse(container.get('wrap'))
        self.assertIn(('caption', 'Đánh giá lời hướng dẫn của hệ thống:'), calls)
        self.assertEqual([c[2] for c in calls if c[0] == 'button'], [TOOLTIP_UP, TOOLTIP_DOWN])


if __name__ == "__main__":
    unittest.main()
