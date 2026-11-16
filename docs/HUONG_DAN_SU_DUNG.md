# 📘 HƯỚNG DẪN SỬ DỤNG GIA SƯ AI (GSAI) — 5 TRẠM

> Dành cho **học sinh**, **giáo viên** và **ban giám khảo**.
> Tên nút, ô chọn và radio trong tài liệu này được lấy **nguyên văn** từ giao diện app (cập nhật 17/11/2026).
> Ký hiệu: 🔘 radio (chọn 1) · 🔽 hộp chọn · ☑️ ô tích · ⬜ ô nhập · 🔲 nút bấm · 📂 mục mở rộng (bấm để mở)

---

## MỤC LỤC

0. [Bắt đầu trong 3 phút](#0-bắt-đầu-trong-3-phút)
1. [Thanh bên trái (dùng chung mọi trạm)](#1-thanh-bên-trái-dùng-chung-mọi-trạm)
2. [📖 Trạm 1: Học Tập & Phòng Lab](#2--trạm-1-học-tập--phòng-lab)
3. [✍️ Trạm 2: Gia Sư Socratic & Nộp Bài](#3-️-trạm-2-gia-sư-socratic--nộp-bài)
4. [📝 Trạm 3: Luyện Tập & Khảo Thí](#4--trạm-3-luyện-tập--khảo-thí)
5. [💚 Trạm 4: Tư Vấn Tâm Lý Học Đường](#5--trạm-4-tư-vấn-tâm-lý-học-đường)
6. [📊 Trạm 5: Dữ Liệu & Nghiên Cứu (giáo viên)](#6--trạm-5-dữ-liệu--nghiên-cứu-giáo-viên)
7. [Câu hỏi thường gặp & xử lý lỗi](#7-câu-hỏi-thường-gặp--xử-lý-lỗi)

---

## 0. Bắt đầu trong 3 phút

1. Mở app (web hoặc `streamlit run app.py` trên máy).
2. Ở **thanh bên trái**:
   - ⬜ **Họ và tên của em:** gõ tên (không bắt buộc).
   - 🔽 **🎯 Chọn khối lớp:** chọn Lớp 6 → Lớp 12.
   - 🔽 **📚 Môn học cần hỗ trợ:** chọn môn (danh sách môn tự đổi theo lớp).
   - Nếu app chưa có khóa AI chung: dán khóa vào ⬜ **Dán mã API Key của em vào đây:**.
3. Bấm một trong **5 nút trạm** ở đầu trang:
   `📖 Trạm 1` · `✍️ Trạm 2` · `📝 Trạm 3` · `💚 Trạm 4` · `📊 Trạm 5`
4. Lộ trình gợi ý cho học sinh: **Trạm 1** (học) → **Trạm 2** (nộp bài, được gợi mở) → **Trạm 3** (luyện đề) → **Trạm 4** (khi cần tâm sự).

> 💡 Đổi lớp hoặc môn ở thanh bên thì **mọi trạm** đổi theo.

---

## 1. Thanh bên trái (dùng chung mọi trạm)

### 1.1. Cài đặt và khóa AI
| Điều khiển | Cách dùng |
| :--- | :--- |
| 📂 **📱 Quét mã QR vào app trên điện thoại** | Mở để lấy mã QR; dùng điện thoại quét là vào app. |
| 📂 **📲 Cài đặt Icon App vào Điện thoại & Máy tính (PWA)** | Hướng dẫn thêm biểu tượng app ra màn hình chính. |
| ⬜ **Dán mã API Key của em vào đây:** | Chỉ cần khi app chưa có khóa chung. Khóa chỉ dùng trong phiên, không lưu vào mã nguồn. |

### 1.2. 🤖 Điều phối model Gemini
🔽 **Chọn chiến lược / Model:**

| Lựa chọn | Khi nào dùng |
| :--- | :--- |
| ⚡ Phương án 1: Tối ưu Siêu tốc (Khuyên dùng) | Mặc định. App thử lần lượt các model nhanh, model lỗi thì tự chuyển model khác. |
| 📋 Phương án 2: Danh sách Chuyên gia (22/10/2026) | Dùng danh sách model chuyên gia, xếp model nhanh lên trước. |
| 🎯 Ghim: gemini-3-flash-preview … / gemini-flash-lite-latest … / gemini-3.6-flash … / gemini-3.5-flash-lite … / gemini-3.5-flash … | Ghim một model cố định (để thử nghiệm hoặc so sánh). Số giây ghi kèm là số đo tham khảo, có thể khác theo thời điểm. |

### 1.3. Thông tin học sinh
- ⬜ **Họ và tên của em:**
- 🔽 **🎯 Chọn khối lớp:** Lớp 6 → Lớp 12.
- 🔽 **📚 Môn học cần hỗ trợ:**
  - Lớp 6–9: Toán học, Ngữ văn, Tiếng Anh, Tin học, Công nghệ, Khoa học tự nhiên, Lịch sử & Địa lý, Giáo dục công dân.
  - Lớp 10–12: Toán học, Ngữ văn, Tiếng Anh, Tin học, Công nghệ, Vật lý, Hóa học, Sinh học, Lịch sử, Địa lý, Giáo dục kinh tế và pháp luật.

### 1.4. 📂 💾 Hồ sơ cá nhân trên thiết bị (Trạm 1–5)
Lưu tiến bộ học tập **trên máy của em**, không lưu trên máy chủ.

| Nút | Tác dụng |
| :--- | :--- |
| 🔲 **📦 Nén & tải hồ sơ cá nhân (.gsai.xz)** | Gom hồ sơ phiên thành một file nén. |
| 🔲 **⬇️ Tải file nén về máy** | Lưu file `.gsai.xz` về máy/điện thoại. |
| ⬜ **Khôi phục từ file .gsai.xz trên máy** → 🔲 **♻️ Nạp lại hồ sơ vào phiên** | Mở lại hồ sơ đã lưu lần trước. |
| 🔲 **🗑️ Xóa hồ sơ phiên trên thiết bị này** | Xóa hồ sơ trong phiên hiện tại (file đã tải về máy vẫn còn). |

> Lời khuyên: cuối mỗi buổi học, bấm **Nén & tải** để giữ hồ sơ.

### 1.5. 📂 🛠️ Báo lỗi ứng dụng & Góp ý trải nghiệm
1. 🔽 **Loại vấn đề gặp phải:** `📷 Lỗi nhận diện chữ` · `📊 Lỗi đồ thị Lab` · `🤖 AI giải thích khó hiểu` · `⏳ Ứng dụng chậm` · `💡 Đề xuất mới`.
2. ⬜ **Mô tả chi tiết:** ghi rõ trạm, môn, lớp, bước đang làm.
3. 🔲 **📤 Gửi phản hồi**.

### 1.6. Tài liệu tham khảo
- 📂 **📚 Thư Viện SGK KNTT - Lớp …** — liên kết sách điện tử (VniTeach, NXBGD), có mã QR lật sách song song.
- 📂 **⚖️ Căn Cứ Pháp Quy Bộ GD&ĐT Hiện Hành** — danh sách văn bản, ghi rõ văn bản nào **đã ban hành nhưng chưa có hiệu lực**.

---

## 2. 📖 Trạm 1: Học Tập & Phòng Lab

**Mục tiêu:** tự chiếm lĩnh một bài học: đọc tóm tắt → hỏi đáp với Thầy AI → làm câu hỏi kiểm tra → thực hành trong Phòng Lab.

### Bước 1 — Chọn bài
- 📂 **📚 Sách Giáo Khoa Điện Tử Kết Nối Tri Thức - [Môn] Lớp […]** — mở để đọc sách gốc song song.
- 🔽 **🎯 Chọn chủ đề gợi ý theo môn/lớp:** chọn bài có sẵn theo chương trình; **hoặc**
- ⬜ **📝 Bài học cần chiếm lĩnh kiến thức (hoặc gõ tên bài tùy ý):** gõ tên bài, ví dụ *"Khảo sát hàm số bậc ba"*.
- 🔲 **🚀 Soạn bài học** → AI soạn bản tóm tắt bài học cho học sinh tự học.

> ⚠️ Nếu em đang ở Lớp 12 mà gõ bài của Lớp 11, app hỏi lại và hiện nút 🔲 **👉 Chuyển nhanh sang Lớp … để học**. Bấm nút đó để học đúng lớp, hoặc học tiếp theo hướng ôn tập liên thông.

### Bước 2 — Đọc và lưu bài
- 📂 **📒 Phiếu bài học và infographic chữ viết tay**
  - 🔘 **Kiểu phiếu bài học:**
    - `Chữ viết tay trên giấy ô ly` — giống vở ghi.
    - `Infographic màu theo bài học` — sơ đồ màu, dễ nhớ.
    - `Bản in trắng đen` — tiết kiệm mực khi in.
  - 🔲 **📥 Tải phiếu HTML để xem / In PDF** (mở file → Ctrl+P → Lưu PDF).
  - 🔲 **📄 Tải nội dung gốc Markdown**.
  - 🔲 **🖋️ Tải prompt phong cách chữ viết tay**.
- 🔲 **📦 Tải đầy đủ bài học và câu hỏi (.json)** — lưu trọn bài để mở lại sau mà không cần gọi AI lại.

**Mở lại bài đã lưu:**
- 📂 **📦 Mở lại bài học và câu hỏi đầy đủ (.json)** → chọn file → 🔲 **Mở nội dung và câu hỏi từ bản lưu**.
- 📂 **📂 Mở lại phiếu bài học đã lưu (.md)** → chọn file → 🔽 **Kiểu phiếu từ bản lưu** (`Chữ viết tay` / `Bản màu` / `Trắng đen`) → 🔲 **Mở phiếu từ bản lưu** → 🔲 **📥 Tải lại phiếu HTML**.
- Khi AI trả nội dung chưa khớp ngữ cảnh, app giữ lại bản đó để đối chiếu: 🔲 **📥 Tải nguyên văn bài đang chờ đối chiếu ngữ cảnh** và 📂 **📚 Các bản chờ đối chiếu trước đó trong phiên**.

### Bước 3 — Vấn đáp Socratic
- 📂 **💬 Vấn đáp Socratic cùng Thầy AI về bài học '…'**
- ⬜ **Gõ câu trả lời hoặc chỗ chưa hiểu gửi Thầy...** → Enter.
- Thầy AI **hỏi gợi mở**, không đưa ngay đáp án. Hỏi lại bao nhiêu lần cũng được.

### Bước 4 — Trắc nghiệm kiểm tra nhanh
Với mỗi câu:
1. 🔘 **Chọn đáp án câu …:** chọn A/B/C/D.
2. (Khi bí) 📂 **💡 Gợi mở tư duy Socratic câu … (mở khi bí — không lộ đáp án)**.
3. 🔲 **🔍 Kiểm tra câu …** → biết đúng/sai và xem giải thích.

### Bước 5 — Phòng Lab
- 🔽 **Mô phỏng có sẵn (không cần API):** chọn mô phỏng → 🔲 **Mở mô phỏng có sẵn**. *(Không tốn lượt AI.)*
- ⬜ **Lệnh mô phỏng:** mô tả thí nghiệm muốn xem → 🔲 **✨ Khởi chạy Phòng Lab** (có dùng AI).
- 📂 **🌐 Mở Rộng: Phòng Thí Nghiệm Ảo Động 3D WebGL (Tương Tác Xoay 360°)**:
  - 🔽 **Chọn mô hình phân tử 3D:** Methane (CH4) · Ethanol (C2H5OH) · Acetic acid (CH3COOH).
  - 🔽 **Chọn hiện tượng sóng 3D:** Sóng dừng · Mặt sóng lan truyền đồng tâm.
  - 🔽 **Khám phá mô hình khoa học 3D:** các phân tử như trên.

**Các điều khiển trong mô phỏng** (xuất hiện tùy môn và bài):

| Mô phỏng | Điều khiển |
| :--- | :--- |
| Đồ thị hàm số / miền nghiệm | 🔘 **Cách hiển thị … để đối chiếu:** `SVG chính xác` (hình chuẩn, in được) / `Plotly tương tác` (kéo, phóng to) · 🔲 **Tải hình miền nghiệm (SVG)** · thanh trượt tham số |
| Mũ, lôgarit | ☑️ **Dùng cơ số tự nhiên Euler e** · ☑️ **Dùng Lôgarit tự nhiên (ln(x), cơ số e)** |
| Hình không gian | ☑️ **Tô mờ các mặt phẳng (3D Surfaces)** |
| Chuyển động (Vật lý) | ☑️ **Hiển thị đồ thị Vận tốc v(t)** · ☑️ **Hiển thị đồ thị Gia tốc a(t)** |
| Ném ngang | ⬜ **Độ cao H (m)**, **Vận tốc ngang ban đầu v₀ (m/s)**, **Gia tốc trọng trường g (m/s²)** · ☑️ **So sánh với vật thả rơi cùng lúc, cùng độ cao** · 🔲 **Tải bảng dữ liệu mô phỏng (CSV)** |
| Thẩm thấu tế bào (Sinh) | 🔘 **Loại tế bào:** `Động vật` / `Thực vật có thành` · 2 thanh trượt nồng độ trong/ngoài · 🔲 **Tải cấu hình và kết quả mô hình (.csv)** |
| Phân hủy H₂O₂ (Hóa) | Tab `Số liệu H₂O₂` · `Ảnh hưởng nồng độ` · `Ảnh hưởng nhiệt độ` · thanh chọn khoảng thời gian · 🔽 hệ số H₂O₂ · 🔲 **Tải dữ liệu nguồn để tự tính (CSV)** |
| Di truyền | ⬜ **Kiểu hình của AA và Aa (trội hoàn toàn):** · ⬜ **Kiểu hình của aa:** |
| Múi giờ (Địa) | ⬜ **Ngày tại điểm A:** · ⬜ **Độ lệch UTC tại A/B (phút):** |
| Cổng logic (Tin) | 🔘 **Bit A:** 0/1 · 🔘 **Bit B:** 0/1 · ⬜ **Giá trị x** |
| Mạch điện (Công nghệ) | ☑️ **Có nguồn điện** · 🔲 **Đặt lại trạng thái đèn** · 🔲 **Tải sơ đồ điều khiển (SVG)** |
| Phân loại đất | 🔲 **Tải sơ đồ phân loại đất (SVG)** |
| Bài thực hành có tư liệu | 🔘 câu nhận xét · 🔲 **Đối chiếu nhận xét với tư liệu** · 📂 **Căn cứ và phạm vi của bài thực hành** |

---

## 3. ✍️ Trạm 2: Gia Sư Socratic & Nộp Bài

**Mục tiêu:** nộp ảnh bài làm trên giấy; Thầy AI chỉ ra chỗ sai và **gợi mở để em tự sửa**.

### Bước 1 — Nộp bài
📂 **📤 NỘP BÀI LÀM CỦA EM (Chụp Camera nhiều trang hoặc Tải nhiều ảnh)**

**Cách A — Chụp bằng camera:**
1. ⬜ **Bật Camera chụp trang bài làm:** → chụp.
2. 🔲 **➕ Thêm trang này vào bài làm** (lặp lại cho từng trang).
3. Chụp nhầm: 🔲 **🗑️ Xóa các trang**.

**Cách B — Tải ảnh có sẵn:** ⬜ **Chọn 1 hoặc nhiều ảnh bài làm:**

### Bước 2 — Nhận xét
- 🔲 **🚀 Bắt đầu nhận xét bài làm** (hoặc **… (N trang)** khi nộp nhiều trang).
- 🔲 **🔄 Xóa hết / Đổi ảnh khác** để nộp lại.
- Nếu chữ trong ảnh mờ, AI hỏi lại thay vì đoán. Chụp rõ, đủ sáng, thẳng trang sẽ cho kết quả tốt nhất.

### Bước 3 — Hỏi tiếp
- ⬜ **Em chưa hiểu chỗ nào, hãy hỏi Thầy nhé...** → Enter.
- 📂 **🕸️ Bản Đồ Lỗ Hổng Kiến Thức & Năng Lực Sư Phạm (Radar Chart Đa Môn)** — xem mảng kiến thức còn yếu.
- 🔲 **🔄 Làm mới buổi học** — xóa hội thoại, bắt đầu buổi mới.

---

## 4. 📝 Trạm 3: Luyện Tập & Khảo Thí

Trạm 3 có **2 tab lớn**:
- **🎯 PHÒNG THI & LUYỆN TẬP CHUYÊN ĐỀ (Dành cho Học sinh / Thí sinh)**
- **🛠️ KHÔNG GIAN GIÁO VIÊN & NẠP ĐỀ MỞ RỘNG**

📂 **📋 Cấu trúc luyện tập tham khảo - Môn …** — xem cấu trúc đề của môn đang chọn.

### 4.1. Tab Học sinh — Sinh đề

**Bước 1 — Chọn chuyên đề**
- Lớp 12 có 3 tab: `🏷️ Lớp 12 (Trọng tâm)` · `🏷️ Lớp 11 (Ôn tập)` · `🏷️ Lớp 10 (Nền tảng)`.
- Lớp 11 có 2 tab: `🏷️ Lớp 11 (Trọng tâm)` · `🏷️ Lớp 10 (Ôn tập)`.
- ☑️ Tích các chuyên đề muốn luyện (chọn được nhiều chuyên đề).

**Bước 2 — Yêu cầu tùy biến (không bắt buộc)**
- ⬜ **💬 Yêu cầu ma trận / Ngữ liệu tùy biến (Prompt theo ý muốn):** ví dụ *"Ưu tiên câu có đồ thị, 2 câu vận dụng cao"*.
- 🔲 **Khóa yêu cầu tùy biến** → app báo *ĐÃ GHI NHẬN & KHÓA YÊU CẦU TÙY BIẾN!*. Đề sinh ra sẽ bám đúng yêu cầu này.

**Bước 3 — Cấu trúc đề**
| Điều khiển | Ý nghĩa |
| :--- | :--- |
| ⬜ **Số câu TN P.I:** | Số câu trắc nghiệm 4 lựa chọn. |
| ⬜ **Số câu Đ/S P.II:** | Số câu Đúng/Sai (mỗi câu 4 ý a, b, c, d). |
| ⬜ **Số câu TLN P.III:** | Số câu trả lời ngắn (điền số). |
| 🔽 **⏱️ Thời lượng bài thi (Phút):** | 15 · 30 · 45 · 50 · 60 · 90 · 120. |
| 🔽 **Định hướng môn học:** *(chỉ Tin học và Công nghệ)* | Tin học: `Khoa học máy tính` / `Tin học ứng dụng`. Công nghệ: `Công nghiệp` / `Nông nghiệp`. |
| 🔘 **Cách dùng kho đề Tin học:** *(chỉ Tin học 12)* | `Trộn theo cấu hình` hoặc `Đề gốc Bộ 2025 — mã 0530` (giữ nguyên đề và thứ tự của Bộ, không trộn, không gọi AI). |
| 🔽 **Mục đích bài đo (giáo viên)** | `practice` (luyện tập) · `pre` (đo đầu kỳ) · `post` (đo cuối kỳ) — dùng cho nghiên cứu ở Trạm 5. |
| ⬜ **Mã học sinh nghiên cứu (không dùng họ tên)** | Ví dụ `HS-12A1-07`. |

> Ngữ văn là **100% tự luận** nên không có ô số câu P.I/P.II/P.III. Tiếng Anh chỉ có trắc nghiệm 4 lựa chọn.

**Bước 4 — 🔲 🚀 Sinh đề** *(một nút duy nhất)*
1. App lấy câu trong **kho đề** đúng môn, lớp, chuyên đề và yêu cầu tùy biến.
2. Kho **chưa đủ** số câu → **AI sinh phần còn thiếu**, rồi cho qua bộ lọc kiểm tra.
3. Đề hợp lệ thì vào **phòng thi** ngay.

> ⚠️ Đề do AI sinh **cần giáo viên duyệt** trước khi dùng cho đánh giá chính thức.

### 4.2. Làm bài trong phòng thi
- Đồng hồ đếm ngược ở đầu bài. **Hết giờ app tự nộp.**
- **Phần I:** 🔘 **Lựa chọn câu …:** chọn A/B/C/D.
- **Phần II:** với mỗi ý a, b, c, d: 🔘 **Chọn Đúng/Sai cho câu …, ý …** → `Chưa chọn` / `Đúng` / `Sai`.
- **Phần III:** ⬜ **Nhập đáp số câu …:**
- **Ngữ văn:** ⬜ **Trả lời câu …:** (đọc hiểu) và ⬜ **Bài làm viết câu …:** (viết).
- Mỗi câu có 📂 **💡 Gợi mở tư duy Socratic câu … (mở khi bí — không lộ đáp án)**.
- 📂 **🖨️ In đề trắng / xuất bản trước khi vào phòng thi** — in đề giấy.
- Làm xong: 🔲 **🏁 Nộp bài & Chấm điểm tức thì**.

**Cách chấm Phần II (Đúng/Sai) theo QĐ 764/QĐ-BGDĐT:** đúng 1 ý được 0,1 điểm; 2 ý được 0,25; 3 ý được 0,5; cả 4 ý được 1,0.

### 4.3. Sau khi nộp
- Xem điểm, đáp án và lời giải từng câu.
- **Ngữ văn:** 🔲 **Chấm Ngữ văn theo tiêu chí (AI tham khảo)** — điểm chỉ mang tính tham khảo, giáo viên chấm chính thức.
- Hỏi lại Thầy: ⬜ **Hỏi Thầy về câu em làm sai hoặc chưa rõ trong bài thi...** → 🔲 **💬 Gửi hỏi Thầy**.
- 📂 **🏛️ BẢNG ĐỐI SOÁT CHÉO NGUỒN GỐC DÀNH CHO BAN GIÁM KHẢO & THANH TRA KHẢO THÍ** — nguồn gốc từng câu (kho / AI).
- 📂 **📋 Đối soát nhãn mức độ câu hỏi (chưa thẩm định)**.
- 🔲 **🔄 Làm đề khảo thí mới** — làm đề khác.

### 4.4. Xưởng xuất bản đề (in, Word, Azota, LaTeX)
📂 **🖨️ MỞ XƯỞNG XUẤT BẢN ĐỀ THI, BẢN IN A4, OVERLEAF LATEX & FILE WORD AZOTA (1-CHẠM)** → ☑️ **⚡ Kích hoạt Xưởng Xuất Bản (PDF A4 / LaTeX / Word Azota / Mã QR)**

1. 🔘 **📋 Chọn Mẫu Xuất Bản & In PDF (Chuyển đổi tức thì để so sánh):**
   - `🏛️ Mẫu 1: Chuẩn Khảo Thí Quốc Gia (Form Truyền Thống Công Phu - Thầy Phan Minh Trí)`
   - `📘 Mẫu 2: Chuẩn Sư Phạm Hiện Đại (Overleaf Typography - Gợi Mở Tư Duy)`
2. ☑️ **✅ In 1-Chạm: Kèm Toàn Bộ Đáp Án, Lời Giải Chi Tiết & Ma Trận Chấm Điểm Chuẩn Bộ** — bỏ tích để in đề cho học sinh, tích để in bản giáo viên.
3. 📂 **⚙️ Tùy Biến Tiêu Đề, Tên Trường, Giáo Viên & Chân Trang Triết Lý Giáo Dục:**
   ⬜ **🏫 Tên Trường / Đơn vị khảo thí:** · ⬜ **👨‍🏫 Tên Giáo viên biên soạn:** · ⬜ **💬 Trích dẫn triết lý giáo dục chân trang (Góc trái):** · ⬜ **✒️ Tác giả câu triết lý:** · ☑️ **☕ Hiển thị Mã VietQR MB Bank ủng hộ tác giả ở cuối trang đáp án**.
4. Các tab:

| Tab | Nút tải |
| :--- | :--- |
| 👁️ Xem Trước Bản In A4 (PDF Live Preview) | 🔲 **🖨️ Tải File In HTML (Mẫu 1/2)** → mở file → Ctrl+P → Lưu PDF |
| 📱 Quét Mã QR Trên Điện Thoại (Kép: Đề thi & VietQR) | Quét để mở đề trên điện thoại |
| 💻 Mã Nguồn LaTeX Overleaf (TikZ & Tabularx) | 🔲 **⬇️ Tải Nguồn LaTeX** · 🔲 **Tải mã TikZ của hình và bảng biến thiên (.tex)** |
| ⚡ Xuất Chuẩn Azota / LMS ($$...$$) | 🔲 **⚡ Tải Đề Chuẩn Azota (.txt)** · 🔲 **📄 Tải Đề Chuẩn Word (.docx Azota / LMS)** · 📂 **👁️ Xem trước nội dung file Azota (.txt)** |
| 💾 Tải Đề Dữ Liệu JSON | 🔲 **⬇️ Tải Đề Dữ Liệu JSON (Đầy đủ đồ thị & tham số)** |

### 4.5. Tab Giáo viên — Nạp đề mở rộng
**A. Yêu cầu ma trận riêng**
- ⬜ **💬 Nhập yêu cầu cấu hình ma trận / Ngữ liệu tùy biến:**
- ☑️ **🎯 Tự Động Trộn Ngữ Liệu Đề Thi Thật (…)**.

**B. 📂 📤 Tải Lên Đề Thi Từ Giáo Viên (Word .docx, PDF, Văn Bản)**
1. ⬜ **Tên Giáo viên / Tổ chuyên môn:** · ⬜ **Trường THPT / Đơn vị:** · ⬜ **Tiêu đề đề thi:**
2. 🔘 **Hình thức nạp đề:**
   - `Tải file Word (.docx) / PDF (.pdf)` → ⬜ **Chọn file đề thi (.docx, .pdf, .txt):**
   - `Dán văn bản trực tiếp` → ⬜ **Dán nội dung đề thi vào đây:**
3. 🔲 **⚙️ Phân Tích & Chuẩn Hóa Cấu Trúc Đề Thi** — app bóc tách câu, phương án, đáp án.
4. Chọn cách dùng:
   - 🔲 **🚀 Nạp Nguyên Đề** — làm đúng đề vừa tải.
   - 🔲 **🔀 Trộn Đề Mới (Quét + Quốc Gia)** — trộn với kho đề.
   - 🔲 **💾 Lưu Kho Đề Riêng** — lưu vào kho của giáo viên.
   - 🔲 **🏛️ Nạp Shard Quốc Gia** — đưa vào kho chung (**chỉ khi đã đăng nhập giáo viên**).

**C. 📂 🔍 Quét & Trích Xuất Ngữ Liệu Trực Tiếp Từ Link Đề Thi**
1. ⬜ **Nhập Link Chuyên Mục hoặc Link Bài Viết:**
2. 🔲 **🔎 Quét Danh Mục Tìm Đề Mới** *hoặc* 🔲 **⚡ Bóc Tách Trực Tiếp Từ Link Này**.
3. 🔽 **Chọn đề thi muốn bóc tách ngữ liệu:** → 🔲 **🚀 Bóc Tách File PDF & Nạp Làm Ngay**.

**D. 📂 ⚡ Mở Đề Thi Có Sẵn Từ Ngân Hàng Offline (… đề đã lưu)**
- 🔽 **Chọn đề từ ngân hàng:** → 🔲 **🚀 Nạp đề đang chọn**, hoặc 🔲 **🎲 Bốc ngẫu nhiên (… đề)**.

---

## 5. 💚 Trạm 4: Tư Vấn Tâm Lý Học Đường

> **Không cần mật khẩu.** Đây là nơi em được **lắng nghe**, **không phải** nơi chẩn đoán bệnh.
> 🚨 Nếu em có ý nghĩ làm hại bản thân, hãy **báo ngay** cho thầy cô, cha mẹ hoặc người lớn em tin. App cũng tự nhận diện các dấu hiệu nguy hiểm và hiện hướng dẫn an toàn.

### Học sinh
1. ⬜ **Em hãy kể bằng lời của mình — Thầy đang lắng nghe…** → Enter.
2. Thầy AI nhớ mạch câu chuyện trong phiên (kể cả khi em đổi chủ đề) và tôn trọng khi em chỉ muốn được nghe.
3. 🔲 **🔄 Bắt đầu phiên lắng nghe mới** — xóa cuộc trò chuyện, bắt đầu lại.

### Phần dành cho giáo viên
- 🔽 **Chủ đề đồng hành hôm nay (GV ghi nhận với HS):**
  `Áp lực học tập / thi cử` · `Tự tin & hình ảnh bản thân` · `Bạn bè, xung đột lớp, bắt nạt` · `Giao tiếp gia đình–học đường` · `An toàn mạng & ứng xử số` · `Định hướng nghề nhẹ / ý nghĩa học` · `Cảm xúc khó chịu, mất ngủ nhẹ, lo âu học đường` · `Em muốn kể theo cách của mình`.
- 📂 **Neo pháp lý & đạo đức tư vấn (đối chiếu bản chính thức)** — văn bản pháp lý làm căn cứ tư vấn.
- 📂 **Ngữ cảnh hành trình Trạm 1–3 (để Thầy tư vấn nhớ em)** — chỉ dùng khi học sinh đồng ý.
- 📂 **📏 Đo tiến bộ học đường (0đ · WHO-5 NC + check-in GSAI) — chỉ GV:**
  1. 🔘 **Mốc đo:** `session` (trong buổi) · `pre` (trước) · `post` (sau).
  2. Thanh trượt **Check-in học đường GSAI (0–10)**.
  3. ⬜ **Mục tiêu tuần của em (GBO giáo dục):** + thanh trượt **Mức đạt mục tiêu tuần (0–10)**.
  4. 5 câu **WHO-5** (cảm nhận trong 2 tuần gần nhất), mỗi câu chọn một mức.
  5. 🔲 **💾 Lưu chỉ số sang Trạm 5**.

> Hội thoại tư vấn **không tự động gửi sang Trạm 5**. Chỉ các chỉ số mà giáo viên bấm lưu mới được chuyển.

---

## 6. 📊 Trạm 5: Dữ Liệu & Nghiên Cứu (giáo viên)

### Mở khóa
⬜ **Mật khẩu giáo viên:** → 🔲 **🔓 Mở khóa Trạm 5**. Dùng xong bấm 🔲 **Khóa Trạm 5 (giáo viên)**.

### 6.1. 📂 🩺 Sức khỏe hệ thống
- 🔲 **Tải nhật ký (CSV)**.
- 🔲 **Tải bài chưa nộp đã giữ trong phiên**.
- 🔲 **Tải sự kiện chưa đồng bộ** · 🔲 **Thử gửi lại sự kiện** (khi mất mạng hoặc đồng bộ lỗi).

### 6.2. Dữ liệu học sinh
- 🔲 **⬇️ Tải CSV nghiên cứu (đã ẩn danh / không PII tư vấn thô)**.
- 📂 **Chi tiết hồ sơ từng học sinh** → 🔲 **Tải bảng Pre–Post cá nhân hóa (CSV)**.

### 6.3. Phân tích trước – sau (pre–post)
1. 🔘 **Nguồn dữ liệu:**

| Lựa chọn | Dùng khi |
| :--- | :--- |
| `Cơ sở dữ liệu thực (DB / SQL)` | Lấy bài thi đã lưu trong app. |
| `Nhập điểm thật` | Gõ điểm tay. |
| `Tải CSV/Excel` | Có bảng điểm sẵn. ⬜ **Bảng điểm theo từng học sinh** · 🔲 **Tải mẫu bảng trống** |
| `Nhật ký Trạm 3` | Lấy từ các bài làm ở Trạm 3 (🔽 **Lớp và môn nghiên cứu**). |
| `Mô phỏng minh họa` | **Chỉ để minh họa** cách dùng (thanh trượt **Số hàng minh họa**). **Không** dùng làm kết quả nghiên cứu. |

2. 🔽 **Môn học kiểm định:** · 🔽 **Khối lớp:**
3. Chọn cột: 🔽 **Cột mã học sinh** · 🔽 **Cột điểm trước** · 🔽 **Cột điểm sau** · 🔽 **Cột thời gian học (tùy chọn)**.
4. 🔲 **Phân tích các cặp điểm**.
5. Có nhóm đối chứng: 📂 **Đối chứng: nhóm dùng app vs không dùng app (Welch / Mann–Whitney)** → ⬜ **CSV/Excel nhóm đối chứng (không dùng app)** → 🔲 **So sánh với nhóm đối chứng**.

> Kết quả trước–sau **không có nhóm đối chứng** chỉ là quan sát, chưa đủ để kết luận app gây ra tiến bộ.

### 6.4. Đo lường đề và mô phỏng
- 📂 **📊 Thẩm Định Khảo Thí Chuẩn ETS: Hệ Số Tin Cậy Cronbach's Alpha (α) & Độ Phân Biệt (r_pbis)** → 🔲 **📥 Tải Báo Cáo Đo Lường Khảo Thí (CSV Item Analysis)**.
- 📂 **🎲 Mô phỏng Mở rộng Toàn tỉnh (Monte Carlo Simulation)**: ⬜ **Số lượt mô phỏng (N):** · 🔽 **Tỷ lệ bao phủ phân vị mô phỏng:** 0.95 / 0.99 · 🔲 **🚀 Kích hoạt Mô phỏng Monte Carlo**. *Đây là mô phỏng dựa trên giả định, không phải số liệu thật.*

### 6.5. Gửi yêu cầu cải tiến
⬜ **Mô tả lỗi hoặc cải tiến cần thực hiện** → 🔲 **Tải yêu cầu để gửi người phát triển**.

---

## 7. Câu hỏi thường gặp & xử lý lỗi

| Hiện tượng | Cách xử lý |
| :--- | :--- |
| AI không trả lời / báo lỗi khóa | Kiểm tra ô **Dán mã API Key**; thử 🔽 **Chọn chiến lược / Model:** → *Phương án 1*. |
| Bấm **🚀 Sinh đề** báo lỗi JSON | Bấm **Sinh đề** lại một lần. AI đôi khi trả dữ liệu chưa sạch, không phải lỗi máy chủ. |
| Đề có ít câu hơn đã chọn | Kho thiếu và AI chưa bù đủ. Thử chọn thêm chuyên đề hoặc giảm số câu. |
| Ảnh bài làm đọc sai chữ | Chụp lại: đủ sáng, thẳng trang, không bóng tay. |
| Mất bài đang làm khi tải lại trang | Thường xuyên dùng **📦 Nén & tải hồ sơ cá nhân** ở thanh bên. |
| Không vào được Trạm 5 | Cần mật khẩu giáo viên (`ADMIN_PASS` trong Secrets). |
| Muốn in đề | Trạm 3 → Xưởng xuất bản → **Tải File In HTML** → mở file → Ctrl+P → *Lưu dưới dạng PDF*. |
| Gặp lỗi khác | Thanh bên → **🛠️ Báo lỗi ứng dụng & Góp ý trải nghiệm**. |

---

*Dưỡng thiện tâm – Ươm nhân tài.*
