# -*- coding: utf-8 -*-
"""Web 18/11/2026: Trạm 4 trả rỗng ở mọi model khi học sinh kể bị thầy cô đối xử bất công."""
import pathlib
import unittest

from google.genai import types

from services.counseling_safety import COUNSELING_SAFETY_SETTINGS


class CounselingSafety(unittest.TestCase):
    def test_only_high_risk_blocked_sexual_untouched(self):
        cats = {s.category: s.threshold for s in COUNSELING_SAFETY_SETTINGS}
        self.assertNotIn(types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, cats)
        self.assertTrue(all(t == types.HarmBlockThreshold.BLOCK_ONLY_HIGH for t in cats.values()))

    def test_station4_passes_settings_and_crisis_gate_runs_first(self):
        src = pathlib.Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        call = src.index("safety_settings=COUNSELING_SAFETY_SETTINGS)")
        self.assertLess(src.rindex("_crisis = is_crisis_text(_user_msg)", 0, call), call)
        self.assertIn("cfg.safety_settings = safety_settings", src)
        self.assertIn("bộ lọc an toàn chặn câu hỏi", src)


if __name__ == "__main__":
    unittest.main()


class ViolenceDisclosureGetsListeningReply(unittest.TestCase):
    """Owner 18/11/2026: ca "hiếp dâm" từng được AI trả lời thấu cảm; ca "xâm hại" chỉ ra khung cứng ngắn."""

    def test_keywords_and_safety_block(self):
        from services.school_counseling import is_crisis_text, is_violence_disclosure, violence_safety_block
        for msg in ("Em bị hiếp dâm", "Em bị xâm hại tình dục ở trường", "bị quấy rối tình dục"):
            self.assertTrue(is_violence_disclosure(msg), msg)
            self.assertFalse(is_crisis_text(msg), msg)
        block = violence_safety_block()
        for must in ("Em không có lỗi", "111", "115"):
            self.assertIn(must, block)

    def test_only_crisis_stops_at_fixed_template_violence_goes_to_ai_with_block_first(self):
        src = pathlib.Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        self.assertIn("        if _crisis:\n            _safe = crisis_resources_md()", src.replace("\r\n", "\n"))
        self.assertNotIn("if _crisis or _violence:", src)
        self.assertIn(r'_reply = violence_safety_block() + "\n\n" + _reply', src)


class TraumaInformedInstruction(unittest.TestCase):
    """Owner 18/11/2026: ca bị thầy xâm hại ra bảng quy trình + pháp lý + khẩu hiệu — đúng nhưng lạnh."""

    def _si(self, trauma):
        from services.school_counseling import counseling_system_instruction
        return counseling_system_instruction(student_name="em", grade=12, subject="Toán học", theme_label="x",
                                             journey_context="", legal_block="LEGAL", trauma=trauma)

    def test_trauma_mode_keeps_lock_and_forbids_cold_patterns(self):
        si = self._si(True)
        self.assertTrue(si.startswith("[TRAM5_COUNSELING_LOCK_V1]"))
        for must in ("CHẾ ĐỘ SANG CHẤN", "thầy tin em", "KHÔNG phải lỗi của em", "an toàn lúc này",
                     "không cần qua người đó", "câu mở lời", "Khung pháp lý", "khẩu hiệu"):
            self.assertIn(must, si)

    def test_general_mode_is_warm_too(self):
        si = self._si(False)
        self.assertIn("GIỌNG THẤU CẢM", si)
        self.assertIn("mời em kể tiếp", si)

    def test_trauma_reply_gets_no_slogan_footer(self):
        from services.school_counseling import PHILOSOPHY, enforce_tram5_reply
        out, flags = enforce_tram5_reply("Thầy tin em.", trauma=True)
        self.assertNotIn(PHILOSOPHY, out)
        out2, _ = enforce_tram5_reply("Thầy tin em.")
        self.assertIn(PHILOSOPHY, out2)
