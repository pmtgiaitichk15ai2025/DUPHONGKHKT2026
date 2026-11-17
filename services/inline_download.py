# -*- coding: utf-8 -*-
"""Link tải nhúng dữ liệu (data URI) làm dự phòng cho st.download_button.

Ca thật 17/11/2026 trên Streamlit Cloud: nút tải trả 404 "File not found" khi phiên đã kết nối lại,
vì file của st.download_button chỉ nằm trong bộ nhớ phiên trên server.
"""
import base64
import html

MAX_INLINE_BYTES = 6 * 1024 * 1024


def inline_download_links(items):
    links = []
    for label, data, file_name, mime in items:
        if not data or len(data) > MAX_INLINE_BYTES:
            continue
        encoded = base64.b64encode(data).decode("ascii")
        links.append(f'<a download="{html.escape(file_name, quote=True)}" href="data:{mime};charset=utf-8;base64,{encoded}">'
                     f'{html.escape(label)}</a>')
    if not links:
        return ""
    return '<div style="font-size:0.85rem">Nút tải không phản hồi? Tải trực tiếp: ' + " · ".join(links) + "</div>"
