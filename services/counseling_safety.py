# -*- coding: utf-8 -*-
"""Ngưỡng bộ lọc an toàn Gemini cho Trạm 4 – Tư vấn tâm lý học đường (owner 18/11/2026).

Mặc định của Gemini chặn cả lời kể bình thường của học sinh (bị thầy cô phân biệt đối xử, căng thẳng,
xung đột bạn bè) nên Trạm 4 không trả lời được. Chỉ nới các nhóm "quấy rối / thù ghét / nguy hiểm"
xuống mức chỉ chặn nội dung rủi ro CAO; nội dung tình dục giữ mặc định. Ca khủng hoảng và bạo lực
được app chặn cứng bằng từ khóa và chuyển tài nguyên hỗ trợ trước khi gọi AI.
"""
from google.genai import types

COUNSELING_SAFETY_SETTINGS = [
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
    types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
]
