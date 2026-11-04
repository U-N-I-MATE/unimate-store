# UNI MATE Jin

> "Dạ em là Jin ạ. Điều gì có căn cứ, em trả lời chính xác; điều gì chưa có, em xin phép ghi nhận
> để người phụ trách phản hồi anh/chị."

Jin là trợ lý chăm sóc khách hàng của UNI MATE, dùng được cho mọi ngành: cửa hàng thực phẩm, mỹ
phẩm, spa, trung tâm đào tạo, nhà phân phối hay dịch vụ kỹ thuật. Phần tính cách, quy cách nhắn
tin và nguyên tắc làm việc đã có sẵn. Bạn chỉ cần cho Jin biết **cửa hàng của bạn là ai và bán gì**.

## Jin làm việc thế nào

- **Chỉn chu.** Câu chữ gọn, đúng chính tả, xưng hô nhất quán, con số chính xác.
- **Tận tâm.** Nghe hết ý khách rồi mới trả lời, nghĩ trước điều khách cần tiếp theo, gợi ý đúng
  lúc nhưng không ép mua.
- **Ấm áp.** Lễ độ mà không cứng nhắc. Khách không vui thì Jin bỏ biểu tượng cảm xúc, xin lỗi
  chân thành và đi thẳng vào xử lý.
- **Minh bạch.** Giá, khuyến mãi, phí giao hàng, bảo hành: tài liệu chưa có thì Jin nói thật là
  chưa có và ghi nhận để người phụ trách trả lời. Jin không tự giảm giá, không hứa thay chủ.
- **Đúng phạm vi.** Câu hỏi không liên quan tới cửa hàng (bài tập, lập trình, chính trị...) Jin
  từ chối nhã nhặn rồi mời khách quay lại chủ đề chính.
- **Trung thực.** Jin không nhận mình là người thật. Khách hỏi thẳng thì Jin trả lời mình là trợ
  lý ảo, và chuyển người phụ trách khi cần.

## Bắt đầu sau khi cài (khoảng 10 phút)

### Bước 1. Điền thẻ nhân viên

Vào trang **Agents**, mở **UNI MATE Jin**, sửa **MỤC 1. THẺ NHÂN VIÊN**:

- Tên gọi của trợ lý (mặc định Jin, đổi được)
- Tên cửa hàng hoặc thương hiệu
- Người phụ trách trả lời thay Jin
- Lĩnh vực và sản phẩm chính, một hai câu
- Kênh liên hệ người thật: hotline, Zalo, email
- Giờ làm việc

Ô nào chưa điền thì để nguyên dấu ngoặc vuông. Jin không đọc ngoặc vuông cho khách mà tự nói
"bên em", "bộ phận phụ trách bên em".

### Bước 2. Cho Jin biết về sản phẩm

- **Sản phẩm chủ lực:** chép mẫu ở **MỤC 6. SỔ SẢN PHẨM**, mỗi sản phẩm một khối (mô tả, đối
  tượng, giá, ưu đãi, cách đặt mua, câu hỏi thường gặp, lưu ý khi tư vấn).
- **Thông tin dài** (bảng giá đầy đủ, chính sách đổi trả, câu hỏi thường gặp): lưu thành tài liệu
  trong brain hoặc gắn vào mục **Tài liệu và link** của trợ lý. Jin tự tra trước khi trả lời.

Nên dùng **một brain riêng** cho việc trả lời khách và chỉ để vào đó thông tin được phép công
khai. Mọi thứ trong brain của Jin đều có thể tới tai khách.

### Bước 3. Giao ca cho Jin

Vào trang **Chatbot**, bấm **Bot mới**, chọn kênh **Zalo** hoặc **Telegram**, chọn **UNI MATE
Jin** làm Agent. Lần đầu nên để mức quyền **Chỉ đọc**. Hướng dẫn chi tiết ở
[tài liệu Chatbot của UNI MATE](https://github.com/U-N-I-MATE/UNI-MATE/blob/main/docs/25-chatbot.md).

### Bước 4. Thử trước khi mở cho khách

Nhắn cho bot như một khách thật: hỏi giá một sản phẩm có trong tài liệu, hỏi một câu chắc chắn
chưa có, nhắn "alo", hỏi "em là người hay máy". Chỗ nào chưa vừa ý thì sửa thẻ nhân viên hoặc bổ
sung tài liệu rồi thử lại.

## Dặn thêm cho Jin

Khi trò chuyện với Jin trong UNI MATE, bạn dặn như dặn nhân viên mới:

- "Khách hỏi giao tỉnh thì báo 2-3 ngày."
- "Ngừng giới thiệu mẫu cũ, đã hết hàng."
- "Đơn từ 02 sản phẩm thì nhắc khách được miễn phí giao hàng."

UNI MATE lưu các lời dặn này vào mục **Luật chủ dặn** trong bộ nhớ của Jin, và Jin làm theo từ
lượt sau. Luật chủ dặn được ưu tiên hơn hướng dẫn gốc, trừ 03 điều không đổi: không nói điều chưa
có căn cứ, không nhận là người thật, không xin mật khẩu hay mã OTP của khách.

Những câu khách hỏi mà Jin chưa trả lời được nằm ở tab **Bot bí** trên trang Chatbot. Mỗi tuần
xem qua và bổ sung tài liệu cho các câu hay gặp, Jin sẽ trả lời tốt lên rõ rệt.

## Tuỳ chỉnh thêm

- Agent để `model: ""`, tức chạy theo engine mặc định bạn đang dùng. Muốn trả lời nhanh và tiết
  kiệm, chọn một model nhỏ ở ô Model của trợ lý.
- Skill gắn sẵn là `query-wiki` (skill hệ thống, brain nào cũng có), không cần cài thêm.
- Trợ lý được ghi vào **brain đang mở lúc bấm Cài**. UNI MATE không ghi đè trợ lý bạn đã tự tạo
  trùng tên, và gỡ gói chỉ xoá những gì bạn chưa sửa.
