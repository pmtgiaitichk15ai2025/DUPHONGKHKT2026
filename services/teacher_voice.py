# -*- coding: utf-8 -*-
"""Giọng Thầy Trí (owner duyệt mẫu B ngày 19/11/2026): MP3 tạo trên Space riêng tư Hugging Face (VieNeu-TTS CPU).

Máy chủ Streamlit gọi Space bằng token trong Secrets (HF_TOKEN) rồi gửi MP3 cho trình duyệt → phát được trên
Android, iOS, macOS, Windows. Token không bao giờ xuống trình duyệt. Mọi lỗi trả b"" để giữ giọng nữ/nam.
"""
import hashlib
import time

SPACE_ID = "pmtgiaitichk15ai2025/gsai-giong-thay-tri"
CHUNK_CHARS = 700        # VieNeu CPU: đoạn ngắn ổn định hơn và tiến độ đều
_CACHE = {}
CACHE_MAX = 40


def _client(token):
    from gradio_client import Client
    return Client(SPACE_ID, token=token, verbose=False)


def synthesize_teacher_mp3(text, token, client_factory=_client, attempts=2, sleep=time.sleep):
    """MP3 cả bài giọng Thầy Trí; b"" nếu thiếu token/thư viện hoặc Space lỗi."""
    text = str(text or "").strip()
    if not text or not token:
        return b""
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
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
                path = client.predict(part, "thay_tri", api_name="/speak")
                with open(path, "rb") as fh:
                    data = fh.read()
            except Exception:
                data = b""
            if data:
                break
            sleep(2 * (attempt + 1))
        if not data:
            return b""
        out += data
    result = bytes(out)
    if len(_CACHE) >= CACHE_MAX:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = result
    return result
