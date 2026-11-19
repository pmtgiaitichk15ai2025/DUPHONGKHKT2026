# -*- coding: utf-8 -*-
"""Giọng nam miễn phí (owner 18/11/2026): chia đoạn, thử lại khi dịch vụ chập chờn, lỗi thì trả rỗng."""
import unittest

from services.male_voice import ATTEMPTS, CHUNK_CHARS, split_chunks, synthesize_male_mp3


class SplitChunks(unittest.TestCase):
    def test_chunks_bounded_and_keep_all_words(self):
        text = "Câu một ngắn. " * 400 + "x" * 5000
        parts = split_chunks(text)
        self.assertTrue(all(len(p) <= CHUNK_CHARS for p in parts))
        self.assertEqual("".join(text.split()), "".join("".join(parts).split()))

    def test_empty(self):
        self.assertEqual(split_chunks("  \n "), [])


class Synthesize(unittest.TestCase):
    def test_retries_flaky_service_then_joins(self):
        calls = []

        def synth(part):
            calls.append(part)
            return b"" if len(calls) % 2 else b"MP3"   # mỗi đoạn lỗi 1 lần rồi được
        out = synthesize_male_mp3("Chào các em. " * 300, synth=synth, sleep=lambda s: None)
        n = len(split_chunks("Chào các em. " * 300))
        self.assertEqual(out, b"MP3" * n)
        self.assertEqual(len(calls), 2 * n)

    def test_gives_up_quietly_so_female_voice_stays(self):
        def synth(part):
            raise RuntimeError("403")
        tries = []
        out = synthesize_male_mp3("Chào các em.", synth=synth, sleep=tries.append)
        self.assertEqual(out, b"")
        self.assertEqual(len(tries), ATTEMPTS)


class NarratorWiring(unittest.TestCase):
    def test_app_registers_male_source_and_button(self):
        import pathlib
        src = pathlib.Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        self.assertIn("if (config.male) sources.set('nam_bo', config.male);", src)
        self.assertIn("from services.male_voice import synthesize_male_mp3", src)


class RunsInsideStreamlitEventLoop(unittest.TestCase):
    """Web 19/11/2026: Streamlit Cloud có event loop chạy sẵn → asyncio.run() hỏng mọi lần thử."""

    def test_default_synth_works_when_loop_already_running(self):
        import asyncio
        from unittest import mock
        import services.male_voice as mv

        async def fake(text, voice, rate):
            return b"MP3"

        async def inside():
            with mock.patch.object(mv, "_synth", fake):
                return mv.synthesize_male_mp3("Chào các em.", sleep=lambda s: None)
        self.assertEqual(asyncio.run(inside()), b"MP3")



class SharedCache(unittest.TestCase):
    """Owner 19/11/2026: bài đã tạo giọng nam thì lần sau phát ngay, kể cả khi Microsoft chập chờn."""

    def test_success_cached_failure_not_cached(self):
        from unittest import mock
        import services.male_voice as mv
        mv._CACHE.clear()
        calls = []

        async def ok(text, voice, rate):
            calls.append(text)
            return b"MP3"
        with mock.patch.object(mv, "_synth", ok):
            self.assertEqual(mv.synthesize_male_mp3("Chào các em.", sleep=lambda s: None), b"MP3")
            self.assertEqual(mv.synthesize_male_mp3("Chào các em.", sleep=lambda s: None), b"MP3")
        self.assertEqual(len(calls), 1)

        async def bad(text, voice, rate):
            raise RuntimeError("403")
        with mock.patch.object(mv, "_synth", bad):
            self.assertEqual(mv.synthesize_male_mp3("Bài khác.", sleep=lambda s: None), b"")
        self.assertEqual(len(mv._CACHE), 1)


class TeacherVoice(unittest.TestCase):
    """Owner 19/11/2026 chọn mẫu r5_106 (~90%): giọng Thầy Trí qua Space riêng tư, token chỉ ở máy chủ."""

    def test_chunks_cached_and_failures_quiet(self):
        import os
        import tempfile
        import services.teacher_voice as tv
        tv._CACHE.clear()
        calls = []

        class FakeClient:
            def predict(self, text, voice, api_name):
                calls.append((voice, api_name))
                f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                f.write(b"MP3")
                f.close()
                return f.name
        out = tv.synthesize_teacher_mp3("Chào các em. " * 120, "tok", client_factory=lambda t: FakeClient(), sleep=lambda s: None)
        self.assertTrue(out.startswith(b"MP3") and len(calls) > 1)
        self.assertEqual({c for c in calls}, {("thay_tri", "/speak")})
        n = len(calls)
        tv.synthesize_teacher_mp3("Chào các em. " * 120, "tok", client_factory=lambda t: FakeClient())
        self.assertEqual(len(calls), n)   # đã nhớ
        self.assertEqual(tv.synthesize_teacher_mp3("x y z", ""), b"")   # thiếu token

        def boom(t):
            raise RuntimeError("space asleep")
        self.assertEqual(tv.synthesize_teacher_mp3("Bài khác.", "tok", client_factory=boom), b"")

    def test_app_wiring_keeps_token_server_side(self):
        import pathlib
        src = pathlib.Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        self.assertIn('get_secret("HF_TOKEN", "")', src)
        self.assertIn("if (config.teacher) sources.set('thay_tri', config.teacher);", src)
        self.assertNotIn('"token": _teacher_token', src)


if __name__ == "__main__":
    unittest.main()
