# Bàn giao phiên Claude 17–19/11/2026 — đọc trước khi tiếp tục dự án Gia Sư AI

Viết ngày 19/11/2026 theo yêu cầu chủ dự án (thầy Phan Minh Trí) trước khi đổi tài khoản Claude.
Bản sao chính trên máy: `E:\4 TRẠM THI KHKT_FINAL KHKT 2026\qa_evidence\HANDOFF_CLAUDE_20261119.md`.
Đọc kèm `AGENTS.md` (luật cứng của dự án) và mục đầu `qa_evidence/HANDOFF_CURRENT.md`.

## 1. Cách làm việc chủ dự án yêu cầu (giữ nguyên)

- Vá → chạy **hồi quy toàn bộ** (`python -X faulthandler -m unittest discover -s tests -t .`, ~50–70 phút, chạy nền) → commit + push thẳng `main` (repo `pmtgiaitichk15ai2025/DUPHONGKHKT2026`) → ghi mục đầu `qa_evidence/HANDOFF_CURRENT.md` → chép log vào `qa_evidence/regression_fullNN.log` → báo mã commit, nhờ chủ dự án **Reboot** app Streamlit (`duphongkhkt2026.streamlit.app`) → kiểm lại trên web.
- Commit: `git -c user.name=pmtgiaitichk15ai2025 -c user.email=pmtgiaitichk15ai2025@users.noreply.github.com commit -F msg.txt`; message kết thúc bằng dòng Co-Authored-By theo hướng dẫn hệ thống.
- `app.py` xuống dòng hỗn hợp CRLF/LF: sửa bằng thay thế byte chính xác, không chuẩn hóa toàn file.
- Có test trích dòng code từ app.py bằng AST (vd `tests/test_station1_export_reload.py`): đổi câu gán `export_html` phải cập nhật scope test.
- **Không đọc/ghi ổ F.** Phạm vi: `E:\4 TRẠM THI KHKT_FINAL KHKT 2026`. Không in/ghi khóa API. Thử Gemini local qua DPAPI `C:/Users/pmtgi/AppData/Local/GSAI/credentials/gemini_qa.dpapi` (giải mã trong bộ nhớ, không in).
- Chủ dự án không lập trình: hướng dẫn từng bước bấm; trả lời tiếng Việt, ngắn gọn, trung thực, không phóng đại.
- Khi máy ngủ/ứng dụng Claude khởi động lại, tiến trình hồi quy có thể vẫn chạy ngầm và giữ file log (kiểm `python.exe` trước khi chạy lượt mới).

## 2. Đã phát hành lên main (theo thứ tự)

| Commit | Nội dung | Hồi quy |
|---|---|---|
| 158ecf0 → 0b55f7d | Model Gemini 3.x; hint Socratic Oxyz; 👍/👎 hint → Sheets Trạm 5; mũi tên véc tơ/ký hiệu góc; hình Oxyz + 3D xoay + bản in | OK |
| 7b0e445, ac320ec, b86d63c | Hình bay đúng đoạn đề; dọn repo nhóm 1; nút đánh giá ngang hàng | 1174 OK |
| eb9864c | Câu hỏi Trạm 1 bắt buộc tiếng Việt + cảnh báo | 1176 OK |
| 96e5d4a, d74cf17 | Giọng nam miễn phí edge-tts NamMinh (MP3 máy chủ); sửa lỗi event loop trên Cloud | 1181/1189 OK |
| e931083, d74cf17 | **Trạm 4 thấu cảm**: sứ mệnh trạm, chế độ sang chấn (xâm hại/bạo lực), giữ bằng chứng 72 giờ, bộ lọc Gemini BLOCK_ONLY_HIGH; tự tử giữ khung cố định | 1188 OK |
| 731a6cf | Phiếu **"Vở ghi tay song ngữ – Hoa sen Việt"** + bảng thuật ngữ Anh–Việt | 1207 OK |
| c5fc202 | Song ngữ không lủng (nút dịch tiếp), từ vựng mọi môn/lớp (AI đề xuất có kiểm), dấu ⚠ lệch thuật ngữ, **học liệu tiếng Anh** (Khan/Bitesize/CK-12/Wikipedia/YouTube), nhớ giọng nam theo bài | 1212 OK |

Đã kiểm trên web sau Reboot: Trạm 4 (ca xâm hại có 72 giờ, chưa tắm rửa…), giọng nam phát MP3, phiếu Sen Việt song ngữ dịch đủ.

## 3. Đang dở (chưa commit lúc viết bàn giao — xem mục 6)

1. **Bộ đọc khoa học bản Python** `services/scientific_speech.py` (khớp 12/12 câu với bản JS, test parity) — ĐÃ nối vào `create_pedagogical_tts_component`: giọng nữ, nam, Thầy Trí đều đọc qua `speech_text`.
2. **Giọng Thầy Trí** — chủ dự án chọn mẫu **r5_106** (Recording 5, giây 106–126, temperature 0.5, denoise tắt) ≈ 90% giống. Space DEFAULT đã đổi. App: nút "🎙️ Tạo giọng Thầy Trí đọc bài" chỉ hiện khi Secrets có `HF_TOKEN`; token chỉ ở máy chủ. `gradio_client` đã thêm vào requirements. **Chủ dự án cần tự dán HF_TOKEN** (token loại Read) vào Streamlit → Settings → Secrets: dòng `HF_TOKEN = "hf_..."`.
3. **Thanh đọc gia sư** — ĐÃ thêm: Trạm 1 (mọi câu trả lời, kể cả chốt nhân sinh), Trạm 3 (hỏi bài); Trạm 2 đã có sẵn.
(Trạng thái commit/hồi quy: xem mục đầu qa_evidence/HANDOFF_CURRENT.md.)
4. **Văn phong Nam Bộ**: đề xuất (chờ chủ dự án xác nhận) — nội dung kiến thức giữ tiếng Việt chuẩn SGK; chỉ lời thầy nói thêm (chào, dặn, động viên, chốt nhân sinh) dùng văn phong Nam Bộ lễ độ ("nghen", "nha", "tụi em"), đưa vào lời dặn chung mọi AI kể cả dự phòng.

## 4. Giọng Thầy Trí — trạng thái

- Hugging Face: tài khoản `pmtgiaitichk15ai2025` đã **PRO** (19/11). Space riêng tư `pmtgiaitichk15ai2025/gsai-giong-thay-tri` (Gradio, CPU, VieNeu-TTS v3 Turbo ONNX), API `/speak(text, voice)`; `voice="thay_tri"` dùng DEFAULT, `"thu:<mẫu>:<temperature>:<denoise 0|1>"` để thử.
- Mã Space: `E:\4 TRẠM THI KHKT_FINAL KHKT 2026\voice_space\` (app.py, reference*.wav — **bản thu giọng thầy, không đưa lên GitHub**). Bản thu gốc: `E:\...\voice_ref\` (Recording (5).m4a, ĐỌC ĐOẠN 1.m4a; gốc ở OneDrive Sound Recordings).
- Chủ dự án nghe: mẫu 11 giây (B) "chưa giống, phải giọng Nam Bộ"; `full_A` gần nhất nhưng chưa đạt; sau thử 6 đoạn 20 giây của Recording 5 → **r5_106 ≈ 90%, đã chọn làm DEFAULT**. Hồ sơ 02/11 cũng ghi: clone từ Recording (5) nghe ra Nam Bộ; preset "Thái Sơn" là giọng Bắc (loại).
- Đề xuất đang chờ chủ dự án: Nấc 1 (thử 6–8 đoạn mẫu trong Recording 5 + chấm độ giống bằng speaker embedding, gửi 2–3 bản tốt nhất); Nấc 2 (ZeroGPU của PRO, VieNeu bản lớn có ref_text); Nấc 3 (chủ dự án thu 20–30 phút theo kịch bản → fine-tune riêng giọng; cách duy nhất tiến gần 95–99%). Không hứa 99%.
- Sau khi chọn: đổi `DEFAULT` trong `voice_space/app.py`, upload lại (`HfApi().upload_folder`, token đã đăng nhập bằng `huggingface_hub.login()` trên máy).

## 5. Song ngữ + thuật ngữ — quy tắc đã chốt

- Lượt dịch song ngữ = 1 lượt AI khi người dùng bấm, qua `call_gemini_with_fallback` (mọi model dự phòng nhận cùng system instruction), mở đầu bằng `policy_prompt` (CT2018/KNTT/pháp quy), kèm bảng thuật ngữ; kiểm bằng chương trình (token công thức, thuật ngữ bảng thắng AI, từ AI phải có trong đoạn).
- Bảng thuật ngữ `data/subject_glossary/` (index.json): Toán 10/11/12, Lý/Hóa/Sinh/Tin/Công nghệ/Địa 12. Trạng thái `dat_2_nguon` (Claude + Wikipedia vi↔en) hoặc `chu_du_an_duyet` (`provisional` + `known_issues` hiện trên phiếu). Chính tả Anh (British).
- Bẫy đã gặp: cực âm/dương ≠ cathode/anode ở pin; Wikipedia vi "Quy tắc nhân" trỏ nhầm Product rule; từ đơn "trội/lặn" bắt nhầm. Chưa đối chiếu từng trang SGK (kho ở F bị cấm).
- Thứ tự tiếp: Lịch sử/GDKT&PL/Ngữ văn 12 (mọi từ cần chủ dự án duyệt) → khối 11 → khối 10. Người dùng báo thuật ngữ sai qua "✍️ Báo thuật ngữ dịch sai" → USER_FEEDBACK → Sheets Trạm 5.
- Lỗi trong mẫu infographic Bài 5 của tác giả NCE: Luyện tập 1 huyết áp P'(5) = −250/169 ≈ −1,479 mmHg/s (mẫu ghi −0,740). Đã bỏ dòng "Thiết kế bởi NCE" theo yêu cầu.

## 6. Việc tiếp theo đề xuất (theo thứ tự)

1. Chủ dự án chọn hướng giọng (Nấc 1/2/3) và xác nhận cách tách văn phong Nam Bộ.
2. Nối `scientific_speech.speech_text` vào cả 3 giọng máy chủ (thay bộ làm sạch cũ) + test.
3. Thanh đọc cho gia sư Trạm 1/3 (+ rà Trạm 2).
4. Nối giọng Thầy Trí khi đã duyệt; hướng dẫn dán HF_TOKEN vào Secrets.
5. Hồi quy toàn bộ → push → Reboot → kiểm web.
6. Danh bạ hỗ trợ trường (Trạm 4) — chờ chủ dự án duyệt (số lưu ở Secrets, tự ẩn người bị nhắc tên).
7. Khung khẩn cấp ca tự tử (Trạm 4) còn lạnh — chờ chủ dự án đồng ý viết lại ấm hơn (giữ cố định, không để AI viết).

## 7. Tồn tại đã biết

- 5 tên model trong `MODELS_PROFILE_*` (gemini-3-flash-preview, flash-lite-latest, 3.1-flash-lite-preview, flash-latest, 3.1-pro-preview) trả 404 với key của chủ dự án; chưa xóa vì chưa chắc hỏng với mọi key.
- edge-tts (giọng nam) là đường không chính thức của Microsoft, có lúc từ chối; app thử lại 6 lần/đoạn và nhớ MP3 theo bài.
- Một lần hồi quy Python crash 0xC0000005 không tái hiện (chạy lại bằng `-X faulthandler` đạt).
