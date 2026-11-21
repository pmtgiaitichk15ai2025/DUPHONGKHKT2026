# -*- coding: utf-8 -*-
"""MP3 giọng mẫu owner 21/11/2026 từ Space riêng tư Hugging Face.

Token chỉ dùng trên máy chủ. Lỗi trả b""; không tự chuyển sang giọng khác.
Khả năng phát và độ giống mẫu cần kiểm trên từng thiết bị thực tế.
"""
import hashlib
import os
import time

SPACE_ID = "pmtgiaitichk15ai2025/gsai-giong-thay-tri"
VOICE_REVISION = "owner_20261121_ff54023116cf"
CHUNK_CHARS = 700        # VieNeu CPU: đoạn ngắn ổn định hơn và tiến độ đều
_CACHE = {}
CACHE_MAX = 40
from services.audio_cache import AudioCache
_AUDIO_CACHE = AudioCache(_CACHE, CACHE_MAX)


def _client(token):
    from gradio_client import Client
    return Client(SPACE_ID, token=token, verbose=False)


def synthesize_teacher_mp3(text, token, client_factory=_client, attempts=2, sleep=time.sleep, *, use_shared_cache=True):
    """MP3 cả bài giọng Thầy Trí; b"" nếu thiếu token/thư viện hoặc Space lỗi."""
    text = str(text or "").strip()
    if not text or not token:
        return b""
    if not use_shared_cache:
        return _synthesize(text, token, client_factory, attempts, sleep, voice="thay_tri_private")
    # Scope reuse to the credential without retaining the raw token in the key.
    key = hashlib.sha256((VOICE_REVISION + "\0" + str(token) + "\0" + text).encode("utf-8")).hexdigest()
    return _AUDIO_CACHE.get_or_create(
        key, lambda: _synthesize(text, token, client_factory, attempts, sleep))


def _synthesize(text, token, client_factory, attempts, sleep, voice="thay_tri"):
    from services.male_voice import split_chunks
    try:
        client = client_factory(token)
    except Exception:
        return b""
    out = bytearray()
    for part in split_chunks(text, CHUNK_CHARS):
        data = b""
        for attempt in range(attempts):
            try:
                path = client.predict(part, voice, api_name="/speak")
                with open(path, "rb") as fh:
                    data = fh.read()
                if voice == "thay_tri_private":
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
            except Exception:
                data = b""
            if data:
                break
            sleep(2 * (attempt + 1))
        if not data:
            return b""
        out += data
    return bytes(out)
