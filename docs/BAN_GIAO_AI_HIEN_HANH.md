# BÀN GIAO HIỆN HÀNH CHO MỌI AI (Claude, Codex, Cursor, …) — đọc ĐẦU TIÊN

> Chủ dự án: thầy Phan Minh Trí (không lập trình — hướng dẫn từng bước bấm, trả lời tiếng Việt, ngắn gọn, trung thực).
> Repo: `pmtgiaitichk15ai2025/DUPHONGKHKT2026` (nhánh `main`). App: `https://duphongkhkt2026.streamlit.app`.
> Thư mục làm việc trên máy chủ dự án: `E:\4 TRẠM THI KHKT_FINAL KHKT 2026` (mã trong repo; bằng chứng ở `qa_evidence\`).
> Cập nhật lần cuối: 19/11/2026 — commit `788e8a5` (Claude).

## 0. LỜI DẶN BẮT BUỘC CHO MỌI AI TIẾP NHẬN

1. Đọc theo thứ tự: **file này** → `AGENTS.md` (luật cứng) → mục đầu `E:\...\qa_evidence\HANDOFF_CURRENT.md` (nhật ký mới nhất) → `docs/HUONG_DAN_SU_DUNG.md` (chức năng từng nút, 5 trạm) → `docs/HANDOFF_CLAUDE_20261119.md` (chi tiết đợt 17–19/11).
2. **Làm xong mỗi việc** (hoặc trước khi hết lượt/đổi công cụ): cập nhật mục 3–5 của file này + thêm 1 mục ngắn ở đầu `qa_evidence/HANDOFF_CURRENT.md` (ngày, commit, đã làm, kết quả hồi quy, chưa kiểm, bước tiếp). AI sau phải hiểu ngay đang ở đâu mà không cần hỏi lại chủ dự án.
3. Không xóa lời dặn này; chuyển nguyên văn cho AI kế tiếp nếu tạo file bàn giao mới.

## 1. Quy trình làm việc chủ dự án yêu cầu

- Vá → **hồi quy toàn bộ** `python -X faulthandler -m unittest discover -s tests -t .` (~60–95 phút, chạy nền; máy hay ngủ/sập nguồn → kiểm `python.exe` còn chạy không trước khi chạy lại) → commit + push thẳng `main` → chép log vào `qa_evidence/regression_fullNN.log` → ghi `HANDOFF_CURRENT.md` → báo mã commit, nhờ chủ dự án **Reboot** app → kiểm lại trên web.
- Commit: `git -c user.name=pmtgiaitichk15ai2025 -c user.email=pmtgiaitichk15ai2025@users.noreply.github.com commit -F msg.txt`.
- `app.py` (~18k dòng) xuống dòng hỗn hợp CRLF/LF: sửa bằng thay thế chính xác, không chuẩn hóa cả file. Có test trích code app.py bằng AST (vd `tests/test_station1_export_reload.py`) — đổi câu lệnh liên quan phải cập nhật test.
- **Cấm đọc/ghi ổ F.** Không in/ghi khóa API, token. Thử Gemini local qua khóa DPAPI `C:/Users/pmtgi/AppData/Local/GSAI/credentials/gemini_qa.dpapi` (giải mã trong bộ nhớ). Chủ dự án tự dán khóa/token vào Streamlit Secrets; không nhận khóa qua chat.
- Mọi lượt AI trong app đi qua cổng chung `call_gemini_with_fallback` / `stream_gemini_with_fallback` (app.py): system instruction được tính 1 lần trước vòng thử model → model dự phòng nhận y hệt. Quy tắc mới phải gắn ở đây (đã có: bố cục bước, neo học thuật, văn phong Nam Bộ lời thầy) và có test hợp đồng.
- Neo căn cứ: CT GDPT 2018 + sửa đổi còn hiệu lực, sách KNTT, văn bản pháp quy của Bộ — qua `services/curriculum_policy.policy_prompt`. Không tạo bộ căn cứ thứ hai.

## 2. Ý chí chủ dự án (đã chốt, không tự đổi)

- **Trạm 4**: nơi học sinh gửi niềm tin — thấu cảm, ấm áp, không bao giờ lạnh lùng (`services/school_counseling.py`: sứ mệnh trạm, chế độ sang chấn, khung khẩn cấp cố định ấm áp; danh bạ trường `services/school_contacts.py`).
- **Lời thầy văn phong Nam Bộ**, kiến thức giữ chuẩn SGK (`services/voice_style.py`).
- **Lịch sử, GDKT&PL, Ngữ văn, GDCD không sinh bản song ngữ** (nhạy cảm chính trị – pháp lý; chỉ mở khi giáo viên bộ môn duyệt).
- **Giọng Thầy Trí**: mẫu `r5_106` (~90% giống), tốc độ chậm rãi ngắt theo dấu câu (đã duyệt). Space riêng tư HF `pmtgiaitichk15ai2025/gsai-giong-thay-tri`; mã Space + bản thu ở `E:\...\voice_space\` (KHÔNG đưa lên GitHub).
- Thuật ngữ Anh–Việt chỉ in khi đã đối chiếu (≥2 nguồn) hoặc chủ dự án duyệt; tồn tại phải ghi rõ (`data/subject_glossary/`).

## 3. Trạng thái hiện tại (19/11/2026)

- main `788e8a5`; mã gần nhất `2290744` hồi quy **1223/1223 OK**, đã kiểm web: Trạm 4 khung khẩn cấp mới, gia sư Trạm 1 văn phong Nam Bộ, giọng Thầy Trí/nam, phiếu Sen Việt song ngữ, học liệu tiếng Anh.
- Secrets trên Cloud đã có: khóa Gemini chung, `ADMIN_PASS`, `HF_TOKEN`. CHƯA có `SCHOOL_SUPPORT_CONTACTS`.

## 4. Việc tiếp theo (theo thứ tự ưu tiên)

1. **Giảm độ trễ** (chủ dự án yêu cầu 19/11, chưa bắt đầu): (a) gắn đo thời gian từng phần trên web — không đổi chức năng; (b) tách vùng chạy riêng `st.fragment` cho khu nặng (phiếu in, thanh đọc, Lab, phòng thi), từng khu một + hồi quy; (c) kho bài/đề làm sẵn + tạo giọng chạy ngầm sau khi soạn bài; (d) giọng Thầy Trí lên ZeroGPU (gói PRO 40 phút/ngày) và đánh thức app/Space trước giờ học. Không hứa "độ trễ 0" — phần AI sinh nội dung luôn cần vài giây.
2. Chủ dự án hỏi ý từng người rồi tự dán `SCHOOL_SUPPORT_CONTACTS` (mẫu trong `services/school_contacts.py`).
3. Chủ dự án báo giọng nam "không phát": web thử lại phát được; chờ mô tả (thông báo gì, nút nào, trình duyệt nào).
4. Thuật ngữ khối 11, 10 cho Lý/Hóa/Sinh/Tin/Công nghệ/Địa (quy trình như khối 12: Claude soạn → Wikipedia vi↔en hai chiều → chủ dự án duyệt).
5. Chưa kiểm web: thanh đọc gia sư Trạm 3; phiếu Sen Việt môn Lịch sử (đã có test chặn 2 lớp).

## 5. Tồn tại đã biết

- Giọng Thầy Trí trên CPU: bài dài 1–4 phút lần đầu (có nhớ sẵn). Giọng nam (edge-tts) là đường không chính thức, có lúc từ chối.
- Bảng thuật ngữ chưa đối chiếu từng trang SGK (kho sách ở ổ F bị cấm).
- Lỗi trong mẫu infographic Bài 5 (tác giả NCE): Luyện tập 1 huyết áp P'(5) = −250/169 ≈ −1,479 (mẫu ghi −0,740).
