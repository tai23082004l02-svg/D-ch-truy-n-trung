# Lấy văn bản chương từ CZBooks

Công cụ dòng lệnh dùng Python 3.9 trở lên, không cần cài thư viện ngoài.
Chỉ dùng cho nội dung bạn được phép sao chép. Không vượt đăng nhập,
CAPTCHA, khóa trả phí hay hạn chế truy cập. Nếu gặp 403/429, công cụ dừng.

## Cách chạy

Mở terminal tại thư mục chứa `czbooks_raw.py`. Trên Windows có thể thay
`python3` bằng `py -3`.

Xem trước tên trang và thứ tự chương:

```sh
python3 czbooks_raw.py https://czbooks.net/n/s6lf47
```

Kiểm tra tên truyện và tác giả trên trang trước khi tải: URL được cung cấp
chưa được xác minh là *修真聊天群*. Số chương của công cụ là vị trí trong
mục lục, có thể khác số trong tiêu đề nếu có lời tựa hoặc ngoại truyện.

Tải thử hai chương đầu và kiểm tra nội dung:

```sh
python3 czbooks_raw.py https://czbooks.net/n/s6lf47 --download --start 1 --end 2
```

Sau khi kiểm tra, thay khoảng chương theo nhu cầu:

```sh
python3 czbooks_raw.py https://czbooks.net/n/s6lf47 --download --start 1 --end 100 --delay 3
```

Tệp UTF-8 nằm trong `raw/s6lf47/`: mỗi chương một TXT, một manifest để kiểm tra
khi tiếp tục, và `combined-00001-00100.txt` ghép khoảng đã chọn. Chạy lại cùng
lệnh sẽ bỏ qua các chương đã lưu và còn nguyên vẹn. Không chỉnh sửa các TXT
gốc nếu muốn tiếp tục tải; hãy sao chép sang thư mục dịch riêng. Nếu cấu trúc
mục lục thay đổi, công cụ dừng khi gặp tệp không khớp thay vì ghi đè.

Khoảng cách giữa các yêu cầu tối thiểu hai giây. Chương lưu thành công vẫn
được giữ nếu quá trình bị lỗi; tệp ghép chỉ được cập nhật khi tải xong toàn bộ
khoảng đã chọn. Không tự động thử lại lỗi truy cập.

## Kiểm chứng và giới hạn

```sh
python3 -m unittest -v test_czbooks_raw.py
```

Kiểm thử sử dụng HTML mẫu: lọc và sắp thứ tự liên kết, tách nội dung, lưu và
ghép TXT, tiếp tục tải, bảo vệ tệp bị chỉnh sửa. Chưa xác minh trực tiếp với
CZBooks vì proxy của môi trường chặn tên miền. Bộ tách hiện dựa trên liên kết
`/n/BOOK_ID/CHAPTER_ID`, phần `.content` và tiêu đề `.name` hoặc `h1`; cần
đối chiếu hai chương thử với trình duyệt trước khi tải nhiều. Không tự chuyển
chữ phồn thể sang giản thể, không dịch và không loại quảng cáo nằm sẵn trong
nội dung chương. Nếu trang cần JavaScript hoặc thay đổi cấu trúc, công cụ có
thể cần điều chỉnh.
