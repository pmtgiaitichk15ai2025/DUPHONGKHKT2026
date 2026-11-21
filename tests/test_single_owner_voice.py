import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class SingleOwnerVoiceTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((ROOT / 'app.py').read_text(encoding='utf-8'))
        self.node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                         and n.name == 'create_pedagogical_tts_component')

    def run_reader(self, text='Em đã hiểu.', subject='Ngữ văn', clicked=False,
                   token='private-test-token', result=b'MP3', state=None, selection=None, comp_key='reader-test'):
        class Spinner:
            def __enter__(self): return self
            def __exit__(self, *_): return False
        state = {} if state is None else state
        st = SimpleNamespace(session_state=state, button=Mock(return_value=clicked),
                             spinner=Mock(return_value=Spinner()), audio=Mock(),
                             warning=Mock(), caption=Mock())
        ns = {'st': st, 'get_secret': lambda *args: token}
        exec(compile(ast.Module(body=[self.node], type_ignores=[]), 'reader', 'exec'), ns)
        with patch('services.owner_voice_selection.selected_text', return_value=selection), \
             patch('services.teacher_voice.synthesize_teacher_mp3', return_value=result) as synth:
            ns[self.node.name](text, subject, comp_key)
        return st, synth, state

    def test_no_background_calls_and_empty_initializers_do_nothing(self):
        st, synth, _ = self.run_reader()
        synth.assert_not_called()
        st.audio.assert_not_called()
        st, synth, _ = self.run_reader(text='', clicked=True)
        st.button.assert_not_called()
        synth.assert_not_called()

    def test_every_subject_and_grade_uses_only_owner_voice(self):
        from services.academic_context import subjects_for_grade
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(grade=grade, subject=subject):
                    st, synth, _ = self.run_reader(subject=subject, clicked=True)
                    synth.assert_called_once()
                    self.assertEqual(synth.call_args.args[1], 'private-test-token')
                    st.audio.assert_called_once_with(b'MP3', format='audio/mp3')

    def test_cached_audio_does_not_synthesize_again(self):
        _, synth, state = self.run_reader(clicked=True)
        synth.assert_called_once()
        st, synth, _ = self.run_reader(state=state)
        synth.assert_not_called()
        st.audio.assert_called_once()

    def test_failure_does_not_switch_voice_or_cache_error(self):
        st, synth, state = self.run_reader(clicked=True, result=b'')
        synth.assert_called_once()
        st.warning.assert_called_once()
        st.audio.assert_not_called()
        self.assertFalse(state['owner_voice_mp3'])

    def test_revision_invalidates_audio_and_secret_never_goes_to_player(self):
        _, _, state = self.run_reader(clicked=True)
        with patch('services.teacher_voice.VOICE_REVISION', 'changed-reference'):
            st, synth, _ = self.run_reader(state=state)
        synth.assert_not_called()
        st.audio.assert_not_called()
        self.assertNotIn('private-test-token', repr(state))

    def test_counseling_only_assistant_messages_get_reader(self):
        source = (ROOT / 'app.py').read_text(encoding='utf-8')
        self.assertIn('if _m.get("role", "assistant") == "assistant":', source)
        self.assertIn('f"t4_msg_{_counsel_index}"', source)

    def test_missing_token_never_calls_provider(self):
        st, synth, _ = self.run_reader(clicked=True, token='')
        synth.assert_not_called()
        st.audio.assert_not_called()
        self.assertTrue(st.button.call_args.kwargs['disabled'])

    def test_selected_excerpt_uses_same_voice_once_and_full_button_still_works(self):
        selection = {'text': 'Đoạn được chọn.', 'request': 123}
        st, synth, state = self.run_reader(selection=selection)
        synth.assert_called_once_with('Đoạn được chọn.', 'private-test-token')
        st, synth, state = self.run_reader(selection=selection, state=state)
        synth.assert_not_called()
        st, synth, _ = self.run_reader(selection=selection, state=state, clicked=True)
        synth.assert_called_once_with('Em đã hiểu.', 'private-test-token')


class CounselingVoiceCacheTests(unittest.TestCase):
    def test_counseling_bypasses_shared_cache_and_reset_releases_session_audio(self):
        reader = SingleOwnerVoiceTests()
        reader.setUp()
        _, synth, state = reader.run_reader(clicked=True, comp_key='t4_msg_1')
        synth.assert_called_once_with('Em đã hiểu.', 'private-test-token', use_shared_cache=False)
        self.assertNotIn('owner_voice_mp3', state)
        self.assertTrue(state['owner_counsel_voice_mp3'])
        _, synth, _ = reader.run_reader(state=state, comp_key='t4_msg_1')
        synth.assert_not_called()
        from services.owner_voice_selection import clear_counsel_voice
        state.update(owner_voice_mp3={'lesson': b'keep'}, owner_selection_t4_msg_1={'text': 'x'},
                     owner_selection_seen_t4_msg_1=123)
        clear_counsel_voice(state)
        self.assertNotIn('owner_counsel_voice_mp3', state)
        self.assertNotIn('owner_selection_t4_msg_1', state)
        self.assertNotIn('owner_selection_seen_t4_msg_1', state)
        self.assertEqual(state['owner_voice_mp3'], {'lesson': b'keep'})

    def test_service_private_requests_never_reuse_or_fill_shared_cache(self):
        import services.teacher_voice as tv
        before = dict(tv._CACHE)
        with patch.object(tv, '_synthesize', return_value=b'private') as synth:
            for _ in range(2):
                self.assertEqual(tv.synthesize_teacher_mp3('private-fixture', 'test-token', use_shared_cache=False), b'private')
            self.assertEqual(synth.call_count, 2)
        self.assertEqual(tv._CACHE, before)

    def test_private_service_uses_same_owner_voice_with_private_storage_flag(self):
        import tempfile
        import services.teacher_voice as tv
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'audio.mp3'
            path.write_bytes(b'MP3')
            client = SimpleNamespace(predict=Mock(return_value=str(path)))
            data = tv.synthesize_teacher_mp3('Private fixture.', 'test-token',
                    client_factory=lambda _: client, use_shared_cache=False)
            self.assertEqual(data, b'MP3')
            client.predict.assert_called_once_with('Private fixture.', 'thay_tri_private', api_name='/speak')
            self.assertFalse(path.exists())
            self.assertFalse(path.exists())
