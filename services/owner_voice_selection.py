"""Send selected text only when the learner explicitly asks to hear it."""
from pathlib import Path


def selected_text(key):
    import streamlit.components.v1 as components
    component = components.declare_component(
        'owner_voice_selection', path=str(Path(__file__).resolve().parents[1] / 'assets' / 'owner_voice_selection'))
    return component(key=key, default=None)


def clear_counsel_voice(state):
    """Release session counseling audio and selection requests on reset."""
    state.pop("owner_counsel_voice_mp3", None)
    for key in list(state):
        if str(key).startswith(("owner_selection_t4_msg_", "owner_selection_seen_t4_msg_")):
            state.pop(key, None)
