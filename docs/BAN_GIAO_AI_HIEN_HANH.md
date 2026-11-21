# BÀN GIAO HIỆN HÀNH CHO MỌI AI (Claude, Codex, Cursor, …) — đọc ĐẦU TIÊN

> Chủ dự án: thầy Phan Minh Trí (không lập trình — hướng dẫn từng bước bấm, trả lời tiếng Việt, ngắn gọn, trung thực).
> Repo: `pmtgiaitichk15ai2025/DUPHONGKHKT2026` (nhánh `main`). App: `https://duphongkhkt2026.streamlit.app`.
> Thư mục làm việc trên máy chủ dự án: `E:\4 TRẠM THI KHKT_FINAL KHKT 2026` (mã trong repo; bằng chứng ở `qa_evidence\`).
> Cập nhật lần cuối: 20/11/2026 — Codex tiếp giảm tạo giọng trùng; trạng thái CI/Cloud mới nhất ở đầu qa_evidence/HANDOFF_CURRENT.md tại thư mục dự án gốc.

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
- **Giọng Thầy Trí**: quyết định mới21/11 dùng duy nhất mẫu WAV mới của owner, thay mẫu r5_106 cũ; độ giống mẫu mới chưa được owner xác nhận. Space riêng tư HF `pmtgiaitichk15ai2025/gsai-giong-thay-tri`; mã Space + bản thu ở `E:\...\voice_space\` (KHÔNG đưa lên GitHub).
- Thuật ngữ Anh–Việt chỉ in khi đã đối chiếu (≥2 nguồn) hoặc chủ dự án duyệt; tồn tại phải ghi rõ (`data/subject_glossary/`).

## 3. Trạng thái hiện tại (21/11/2026 — chuẩn bị phát hành)

- Owner yêu cầu push main. Mã nền b7f6afe, đợt này: duy nhất giọng mẫu21/11 ở Trạm1–4; revision cache; cache tư vấn riêng phiên + dọn file tạm; sửa test đồ thị làm ô nhiễm module Streamlit; mặc định ẩn bảng đối soát Trạm3, giữ nguyên mã/dữ liệu.
- Đã kiểm Chrome MCP local: Trạm3 phát MP3 104.291s, currentTime tăng9.162545/pausedfalse/errornull; Trạm4 33.2505s, currentTime5.137408/pausedfalse/errornull. T1/2 có bằng chứng phát trước đó. Không suy đạt Android/iOS hoặc owner đã duyệt độ giống mẫu. Chọn đoạn vẫn cần kiểm riêng.
- Full33:1238 tests OK(skipped2), trước bản cache tư vấn và cờẩn. Full34 sau cache bịMemoryError và máy restart, KHÔNG đạt/không còn chạy. Không chạy lại monolithic y hệt chỉ để gặp lại lỗi; GitHub CI sẽ kiểm toàn suite đúng commit đợt mới, phải lấy kết quả trước kết luận phát hành đạt CI.
- 29 focused cuối đã đạt; trước push kiểm lại focused + AppTestgraded bảngẩn, logs VOICE_RELEASE_FOCUSED_20261121.log và T3_AUDIT_HIDDEN_APPTEST_20261121.log tại rootQA. Kết quả/commit/push/CI mới nhất ở đầu root qa_evidence/HANDOFF_CURRENT.md. Không nhận đang chạy nếu không có process.
- Bảng đối soát chỉ bật lại khi owner yêu cầu bằng Secrets SHOW_TRAM3_SOURCE_AUDIT="true". Local fileWatcherType=none, sửa mã cần restart để nạp. Không commit secrets/cache/audio/DB. Private HF Space chỉ cập nhật code app.py commit86666b4b32ae2ccba1096ae2f4537a1ab01dc3e6; giữ private, cùng mẫuDEFAULT, tênfileprivateUUID/TTL600s khi lockrảnh; không claim zero-retention hoặc đã dọn cache cũ.
- Closure intent đã ở mainb7f6afe/CI đạt. Không mở lại ca đã đóng vì nhật ký cũ. Không có Gemini/TTS pending. ChromeMCP trực tiếp đã hoạt động, pageId phải list lại sau restart; chỉ tablocal ownerủyquyền, không tabriêng.
- Còn mở: Cloud nạp đúngcommit; kiểm đoạn chọn/browser di động/độ giống owner; tốc độ TTS lần đầu/streaming chưa triển khai; sốcâuUI1/0/0 nhưng nhận12/4/6 chưa rõ automationstate hay app; câu trảlời dài hơn yêu cầu; thuậtngữ/kho sách/phiếu lịch sử giữ phạmvi cũ. Không tuyên bố tấtcảmôn/lớp họcthuật đã nghiệmthu. Yêu cầu “hoàn thành mục mở” không tự cho phép trảphí, tăngAI/retry hoặc bịa nguồn.

## 4. Việc tiếp theo (theo thứ tự ưu tiên)

- Owner 21/11: hoàn tất một giọng đọc Trạm1–4, hồi quy toàn bộ, phát hành và kiểm thực; cập nhật nhật ký sau mốc. Không đưa WAV vào repo public, không fallback giọng khác.

0. Owner 20/11 ưu tiên điều tra và xử lý closure nhân sinh/chuyển trạm dùng chung; không kết luận mọi môn/lớp đều lỗi hoặc Android là nguyên nhân. Đã khóa ca ảnh Android, vá local và qua hồi quy toàn bộ; tiếp phát hành/CI/Cloud. Không thêm API/retry; không tự chuyển màn hình hoặc nhét bài nhân sinh cố định. Chưa biết lớp của ca ảnh, cơ chế dùng chung đã kiểm 65 môn/lớp.

1. **Giảm độ trễ** — bản vá gộp tạo MP3 trùng đã hồi quy đạt và push; kiểm trạng thái CI trong checkpoint rồi kiểm web bằng Chrome MCP đúng profile (phiên Codex tiếp nhận chưa có công cụ Chrome MCP).
   **Đo trước đây:** ĐÃ ĐO trên web 19/11 (Claude, trình duyệt, khóa trường):
   - Mở app lần đầu ~4,5 giây; chuyển trạm 0,3–0,8 giây; bấm radio/kiểm tra câu khi đã có bài ~0,3–0,5 giây
     (đo bằng trạng thái "Running" của Streamlit — phương pháp thô, sàn ~0,3 giây).
   - **Chậm thật:** AI soạn bài Nguyên hàm **36 giây**; giọng Thầy Trí cả bài **~4 phút** (câu ngắn ~20 giây);
     giọng nam bài dài tới vài chục giây; Space/app ngủ thì lần đầu 30–60 giây.
   - ⇒ Ưu tiên đúng chỗ: (c) kho bài/đề làm sẵn + hiện chữ dần khi soạn bài; tạo giọng chạy ngầm ngay sau khi soạn xong;
     (d) giọng Thầy Trí lên ZeroGPU; đánh thức app/Space trước giờ học. Mục (b) st.fragment chỉ làm sau, lợi ích nhỏ hơn.
   Kế hoạch ban đầu: (a) gắn đo thời gian từng phần trên web — không đổi chức năng; (b) tách vùng chạy riêng `st.fragment` cho khu nặng (phiếu in, thanh đọc, Lab, phòng thi), từng khu một + hồi quy; (c) kho bài/đề làm sẵn + tạo giọng chạy ngầm sau khi soạn bài; (d) giọng Thầy Trí lên ZeroGPU (gói PRO 40 phút/ngày) và đánh thức app/Space trước giờ học. Không hứa "độ trễ 0" — phần AI sinh nội dung luôn cần vài giây.
2. Chủ dự án hỏi ý từng người rồi tự dán `SCHOOL_SUPPORT_CONTACTS` (mẫu trong `services/school_contacts.py`).
3. Chủ dự án báo giọng nam "không phát": web thử lại phát được; chờ mô tả (thông báo gì, nút nào, trình duyệt nào).
4. Thuật ngữ khối 11, 10 cho Lý/Hóa/Sinh/Tin/Công nghệ/Địa (quy trình như khối 12: Claude soạn → Wikipedia vi↔en hai chiều → chủ dự án duyệt).
5. Thanh đọc Trạm3 đã kiểm phát Chrome. Phiếu Sen Việt môn Lịch sử vẫn cần bằng chứng web (đã có test chặn2lớp).

## 5. Tồn tại đã biết

- Single-voice đã kiểm phát Chrome Trạm1–4; Android/iOS, chọn đoạn qua component và độ giống mẫu chưa xác nhận. Space private đã đổi mẫu nhưng Cloud app cũ vẫn có thể giữ MP3 cũ đến khi nạp revision mới.

- Detector bỏ sót “Em đã hiểu rồi ạ”, “Em ko hỏi gì thêm”, “Em không hỏi gì nữa”; dùng chung cả 3 trạm. Closure Trạm1 chưa kiểm đủ nội dung nhân sinh trước ghi nhận, chuyển trạm hiện là lời mời trong prompt. Đã tái hiện đúng câu trong ảnh, sửa và đạt full; chờ phát hành/CI/Cloud; chưa nghiệm thu phản hồi AI thật. Hai CI của đợt audio 44718927851/44719623078 đã success.

- Chưa đo hiệu quả bản vá gộp tạo MP3 trên web; chỉ giảm lượt tạo trùng đồng thời, không giảm thời gian tổng hợp một bài mới.
- Giọng Thầy Trí trên CPU: bài dài 1–4 phút lần đầu (có nhớ sẵn). Giọng nam (edge-tts) là đường không chính thức, có lúc từ chối.
- Bảng thuật ngữ chưa đối chiếu từng trang SGK (kho sách ở ổ F bị cấm).
- Lỗi trong mẫu infographic Bài 5 (tác giả NCE): Luyện tập 1 huyết áp P'(5) = −250/169 ≈ −1,479 (mẫu ghi −0,740).
