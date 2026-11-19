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


if __name__ == "__main__":
    unittest.main()
