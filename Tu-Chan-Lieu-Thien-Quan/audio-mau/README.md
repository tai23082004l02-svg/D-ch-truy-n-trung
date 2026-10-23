# Mẫu giọng đọc chương 1

Các mẫu dùng cùng đoạn văn 316 đơn vị tách bằng khoảng trắng từ bản dịch
chương 1, tạo bằng VieNeu-TTS 3.8.3, v3 Turbo, CPU fp32.

- [Xuân Vĩnh — mẫu ban đầu](xuan-vinh-chuong-1-mau.mp3)
- [Thanh Bình — mẫu ban đầu](thanh-binh-chuong-1-mau.mp3)
- [Thanh Bình v2 — chia theo câu, chỉnh khoảng nghỉ](thanh-binh-chuong-1-mau-v2.mp3)

Nếu GitHub không phát trực tiếp, chọn **View raw** hoặc tải tệp về để nghe.

## Thanh Bình v2

Giữ nguyên nội dung, chia thành 22 phần theo câu; câu dài có thể tách ở dấu
phẩy. Khoảng nghỉ tối thiểu mục tiêu: 0,18 giây khi tách mệnh đề, 0,3 giây
cuối câu, 0,38 giây sau câu hỏi/cảm, 0,5 giây cuối đoạn. Giữ nguyên mép âm
thanh do mô hình sinh; khoảng lặng tự nhiên của mô hình có thể dài hơn mức
mục tiêu. Không tăng tốc toàn bộ audio.

Đây là thử nghiệm cách chia và ghép đoạn, chưa khẳng định hết lỗi phát âm
hoặc hụt hơi. Kết quả sinh có tính ngẫu nhiên; cần nghe so sánh thực tế.

Bản v2 dài 77,01 giây, sinh mất khoảng 41,2 giây trên CPU, không tính nạp
mô hình. Kiểm tra tự động bằng nhận dạng cho kết quả rõ hơn ở âm đầu
“Vào mùa này” (00:04,5) và “Bạn cùng phòng” (00:51,3). Câu “Thuốc vẫn
chưa hết tác dụng à?” (01:11,5) vẫn bị nhận lệch, cần nghe kiểm chứng;
nhận dạng sai không tự chứng minh TTS đọc sai.
