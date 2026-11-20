"""Concurrent audio requests share work, without mixing lessons or voices."""
import unittest
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event
from unittest.mock import patch

from services.audio_cache import AudioCache


class AudioCacheTests(unittest.TestCase):
    def concurrent_result(self, result=b"MP3", error=False):
        cache = AudioCache({}, 2)
        started, release, waiting = Event(), Event(), Event()
        calls = []

        class ObservedFuture(Future):
            def result(self, timeout=None):
                waiting.set()
                return super().result(timeout=timeout)

        def produce():
            calls.append(1)
            started.set()
            if not release.wait(5):
                raise TimeoutError("test did not release producer")
            if error:
                raise ValueError("provider failed")
            return result

        with patch("services.audio_cache.Future", ObservedFuture), ThreadPoolExecutor(3) as pool:
            first = pool.submit(cache.get_or_create, "same", produce)
            try:
                self.assertTrue(started.wait(5))
                second = pool.submit(cache.get_or_create, "same", produce)
                self.assertTrue(waiting.wait(5))
                # An unrelated subject/grade/voice must continue independently.
                other = pool.submit(cache.get_or_create, "other", lambda: b"OTHER")
                self.assertEqual(other.result(5), b"OTHER")
            finally:
                release.set()
            if error:
                for request in (first, second):
                    with self.assertRaisesRegex(ValueError, "provider failed"):
                        request.result(5)
            else:
                self.assertEqual(first.result(5), result)
                self.assertEqual(second.result(5), result)
        self.assertEqual(calls, [1])
        self.assertEqual(cache._pending, {})
        return cache

    def test_duplicate_requests_share_one_synthesis(self):
        cache = self.concurrent_result()
        self.assertEqual(cache.get_or_create("same", lambda: self.fail("cached")), b"MP3")

    def test_empty_audio_and_exceptions_release_waiters_and_allow_retry(self):
        for error in (False, True):
            with self.subTest(error=error):
                cache = self.concurrent_result(b"", error)
                self.assertNotIn("same", cache.completed)
                self.assertEqual(cache.get_or_create("same", lambda: b"RETRY"), b"RETRY")

    def test_bounded_cache_keeps_exact_keys(self):
        cache = AudioCache({}, 2)
        for key in ("Toan12/male", "Van6/teacher", "Anh10/male"):
            self.assertEqual(cache.get_or_create(key, lambda: key.encode()), key.encode())
        self.assertEqual(list(cache.completed), ["Van6/teacher", "Anh10/male"])

    def test_both_providers_use_shared_coordinator(self):
        from services import male_voice, teacher_voice
        with patch.object(male_voice._AUDIO_CACHE, "get_or_create", return_value=b"MALE") as male:
            self.assertEqual(male_voice.synthesize_male_mp3("Bai hoc"), b"MALE")
            male_voice.synthesize_male_mp3("Bai hoc", rate="-10%")
            self.assertNotEqual(male.call_args_list[0].args[0], male.call_args_list[1].args[0])
        with patch.object(teacher_voice._AUDIO_CACHE, "get_or_create", return_value=b"TEACHER") as teacher:
            for token in ("credential-one", "credential-two"):
                self.assertEqual(teacher_voice.synthesize_teacher_mp3("Bai hoc", token), b"TEACHER")
            keys = [call.args[0] for call in teacher.call_args_list]
            self.assertNotEqual(*keys)
            self.assertTrue(all("credential" not in key for key in keys))
            self.assertEqual(teacher_voice.synthesize_teacher_mp3("Bai hoc", ""), b"")
            self.assertEqual(teacher.call_count, 2)
