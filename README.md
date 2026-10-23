# Công cụ lấy raw CZBooks

Lưu chương tiếng Trung thành TXT UTF-8, ghép khoảng chương và tiếp tục tải
khi gián đoạn. Chỉ cần Python 3.9+, không có thư viện ngoài.

## Chạy online bằng GitHub Actions

1. Mở tab **Actions** của kho mã, chọn **CZBooks Raw**.
2. Bấm **Run workflow**, chọn nhánh `main`, nhập link mục lục và khoảng chương.
3. Lần đầu giữ **Tải TXT** ở trạng thái bỏ chọn để xem tên trang và mục lục
   trong log **Read selected chapters**. Sau khi kiểm tra đúng truyện, chạy lại
   và chọn **Tải TXT**. Mặc định thử chương 1–2; tối đa 200 chương mỗi lần.
4. Khi chạy xong, mở lần chạy đó và tải gói **czbooks-raw-…** tại **Artifacts**.
   Gói ZIP chứa TXT từng chương, TXT ghép và manifest. Kết quả được giữ 7 ngày.

Nếu GitHub yêu cầu bật Actions cho kho mã, bật tại tab Actions trước khi chạy.
Mỗi lần chạy dùng máy mới; dữ liệu không tự tiếp tục từ lần chạy trước. Nếu lỗi
giữa chừng, các chương đã lưu vẫn được đưa vào artifact khi có thể.

## Mở terminal online bằng Codespaces

Chọn **Code → Codespaces → Create codespace on main**. Cấu hình trong
`.devcontainer/devcontainer.json` chuẩn bị Python 3.12 và chạy kiểm thử.
Sau đó dùng các lệnh trong [hướng dẫn](RAW_GUIDE.md). Codespaces/Actions sử
dụng hạn mức của tài khoản GitHub; tính sẵn có phụ thuộc tài khoản.

## Chạy trên máy hoặc môi trường Codex

```sh
python3 -m unittest -v test_czbooks_raw.py
python3 czbooks_raw.py https://czbooks.net/n/s6lf47 --start 1 --end 2
python3 czbooks_raw.py https://czbooks.net/n/s6lf47 --download --start 1 --end 2
```

Xem [hướng dẫn đầy đủ và giới hạn](RAW_GUIDE.md). Nội dung tải về được bỏ qua
bởi Git; không được tự đẩy lên kho mã.

## Trạng thái kiểm chứng

Kiểm thử bằng HTML mẫu đã chạy trong môi trường phát triển. Chưa xác minh
trực tiếp việc tải từ CZBooks: mạng hiện tại chặn tên miền. GitHub Actions
cũng có thể gặp CAPTCHA hoặc 403/429; công cụ sẽ dừng, không vượt hạn chế.
Kiểm tra đúng tên truyện và nội dung hai chương trước khi tải nhiều. Chỉ dùng
với nội dung bạn có quyền sao chép.
