# zlocket-nyan

> [!WARNING]
> **Dự án vẫn đang trong quá trình hồi sinh và chưa hoàn thiện.** Phiên bản hiện
> tại chỉ mô phỏng luồng hoạt động trong bộ nhớ, không kết nối tới Locket,
> Firebase, dịch vụ token của Thanh Diệu hay bất kỳ máy chủ bên ngoài nào. Vì
> vậy, dự án **chưa thể sử dụng với tài khoản hoặc dịch vụ thật**.

## Giới thiệu

`zlocket-nyan` là phiên bản đang được refactor từ source zLocket cũ. Mục tiêu
hiện tại là xây dựng lại cấu trúc chương trình rõ ràng, có kiểm thử và có thể
tích hợp với một môi trường staging được cấp quyền trong tương lai.

Source cũ phụ thuộc vào một dịch vụ cấp token bên thứ ba đã ngừng hoạt động,
sử dụng cấu hình API lỗi thời và thực hiện các tác vụ mạng không giới hạn. Do
đó, phiên bản cũ không còn hoạt động đúng như trước.

## Trạng thái hiện tại

Những phần đã hoàn thành:

- Tách riêng `AppCheckProvider`, `AuthAdapter` và `LocketApiAdapter`.
- Xây dựng workflow có giới hạn số tài khoản, worker và hành động.
- Thêm chế độ `--dry-run` chạy hoàn toàn offline.
- Thêm mock cho App Check, đăng nhập, tạo hồ sơ và gửi lời mời.
- Thêm kết quả dạng JSON để phục vụ kiểm thử tự động.
- Thêm unit test xác nhận chương trình không mở kết nối mạng.

Những phần chưa hoàn thành:

- Chưa có Firebase staging hợp lệ.
- Chưa có App Check provider dành cho staging.
- Chưa cập nhật API contract hiện tại.
- Chưa có adapter kết nối môi trường staging.
- Chưa có kiểm thử end-to-end với tài khoản test được cấp quyền.
- Chưa hỗ trợ môi trường production.

## Yêu cầu

- Python 3.12 trở lên.
- Phiên bản mô phỏng không cần thư viện runtime bên thứ ba.

Khuyến nghị tạo môi trường Python riêng:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Chạy bản mô phỏng

Chạy một chu kỳ mặc định:

```powershell
python locket.py --dry-run
```

Mô phỏng hai tài khoản, mỗi tài khoản thực hiện ba hành động và dùng hai worker:

```powershell
python locket.py --dry-run --accounts 2 --repeat 3 --threads 2 --target test_receiver
```

Mô phỏng hành vi lặp 51 lần của source lịch sử:

```powershell
python locket.py --dry-run --accounts 1 --repeat 51 --threads 1
```

Tất cả tài khoản, token, UID và request trong chế độ này đều là dữ liệu giả.
Không có lời mời thật nào được gửi đi.

Xuất kết quả dạng JSON:

```powershell
python locket.py --dry-run --json
```

## Chạy kiểm thử

```powershell
python -m unittest discover -s tests -v
```

Bộ test hiện kiểm tra giới hạn workflow, số hành động mô phỏng và xác nhận không
có kết nối mạng bên ngoài.

## Kiến trúc

```text
CLI
 `- WorkflowRunner
     |- AppCheckProvider
     |- AuthAdapter
     `- LocketApiAdapter
```

Hiện tại chỉ có các implementation dạng mock. Adapter staging trong tương lai
phải sử dụng Firebase project và API environment do developer kiểm soát, giữ
credential ngoài Git, xác minh TLS, giới hạn request và có cơ chế dọn dữ liệu
test.

## Lộ trình tiếp theo

1. Hoàn thiện tài liệu API contract dành cho staging.
2. Thêm cấu hình Firebase staging bằng biến môi trường.
3. Viết App Check provider được cấp quyền.
4. Viết Firebase Auth và Locket API adapter cho staging.
5. Kiểm thử một tài khoản và một request trong môi trường test.
6. Bổ sung logging, cleanup và giới hạn tải trước khi mở rộng kiểm thử.

## Source lịch sử

Source ban đầu vẫn có thể xem trong lịch sử Git trước phiên bản `2.0.0`. Nó
không còn được giữ làm entrypoint chạy trực tiếp vì phụ thuộc token broker đã
ngừng hoạt động, tắt xác minh TLS và thực hiện tác vụ mạng không giới hạn.

Cho tới khi các adapter staging được hoàn thiện và kiểm thử đầy đủ, repository
này nên được xem là **bản nghiên cứu/refactor chưa sẵn sàng để sử dụng thực tế**.
