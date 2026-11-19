# -*- coding: utf-8 -*-
"""Giọng nam tiếng Việt miễn phí (owner 18/11/2026), phát được trên Android, iOS, macOS, Windows.

Máy chủ Streamlit tạo sẵn MP3 bằng edge-tts (giọng Microsoft vi-VN-NamMinhNeural), trình duyệt chỉ
phát file MP3 nên không phụ thuộc giọng cài trên từng máy. Đây là đường truy cập không chính thức:
dịch vụ có thể từ chối bất kỳ lúc nào (đo 18/11: 403 ở bản 7.2.8, chập chờn ở 7.3.1), nên mọi lỗi
đều trả b"" để app giữ nguyên giọng nữ hiện tại.
"""
import asyncio
import re
import time

MALE_VOICE = "vi-VN-NamMinhNeural"
CHUNK_CHARS = 1800
ATTEMPTS = 6


def split_chunks(text, limit=CHUNK_CHARS):
    """Chia theo câu, mỗi đoạn ≤ limit ký tự (một câu quá dài thì cắt ở khoảng trắng)."""
    parts, cur = [], ""
    for sentence in re.split(r"(?<=[.!?…])\s+|\n+", str(text or "")):
        sentence = sentence.strip()
        if len(sentence) > limit and cur:   # giữ đúng thứ tự đọc
            parts.append(cur)
            cur = ""
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit) or limit
            if cut <= 0:
                cut = limit
            parts.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if not sentence:
            continue
        if cur and len(cur) + 1 + len(sentence) > limit:
            parts.append(cur)
            cur = sentence
        else:
            cur = (cur + " " + sentence).strip()
    if cur:
        parts.append(cur)
    return [p for p in parts if p]


async def _synth(text, voice, rate):
    import edge_tts
    audio = bytearray()
    async for chunk in edge_tts.Communicate(text, voice, rate=rate).stream():
        if chunk.get("type") == "audio":
            audio += chunk["data"]
    return bytes(audio)


def synthesize_male_mp3(text, voice=MALE_VOICE, rate="-5%", synth=None, sleep=time.sleep):
    """MP3 cả bài; b"" nếu thư viện thiếu hoặc dịch vụ từ chối sau ATTEMPTS lần mỗi đoạn."""
    chunks = split_chunks(text)
    if not chunks:
        return b""
    if synth is None:
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            return b""

        def synth(t):
            # Web 19/11/2026: luồng script Streamlit Cloud đã có event loop chạy sẵn nên asyncio.run()
            # báo lỗi ngay ở mọi lần thử. Chạy trong luồng riêng có event loop riêng.
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, _synth(t, voice, rate)).result(timeout=120)
    out = bytearray()
    for part in chunks:
        data = b""
        for attempt in range(ATTEMPTS):
            try:
                data = synth(part)
            except Exception:
                data = b""
            if data:
                break
            sleep(0.6 * (attempt + 1))
        if not data:
            return b""
        out += data  # MP3 cùng định dạng ghép nối tiếp phát liền mạch
    return bytes(out)
