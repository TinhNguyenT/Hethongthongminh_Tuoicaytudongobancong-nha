# Hệ Thống Tưới Cây Thông Minh AI - Ban Công & Nhà Ở

Dự án này là một hệ thống tưới cây tự động tích hợp các công nghệ AI (Logic mờ, Mạng Nơ-ron) và dữ liệu khí tượng thực tế từ Việt Nam để tối ưu hóa việc sử dụng nước.

## Tính Năng Hiện Có
1.  **Thu thập dữ liệu thực tế**: Tự động lấy dữ liệu thời tiết (Nhiệt độ, Độ ẩm, Lượng mưa) từ vệ tinh NASA cho khu vực Việt Nam (mặc định TP.HCM năm 2025-2026).
2.  **Hệ chuyên gia Logic mờ (Fuzzy Logic)**: Quyết định thời gian tưới dựa trên sự kết hợp thông minh giữa Độ ẩm đất, Nhiệt độ và Dự báo mưa.
3.  **Dashboard Giám sát**: Giao diện web hiện đại (Dark Mode, Glassmorphism) hiển thị biểu đồ và thông số thời gian thực.

## Yêu Cầu Cài Đặt
Trước khi chạy, hãy đảm bảo máy tính đã cài đặt Python và các thư viện cần thiết:

```bash
pip install flask pandas requests scikit-fuzzy matplotlib
```

## Hướng Dẫn Chạy Hệ Thống

Bạn thực hiện theo 3 bước sau để vận hành hệ thống:

### Bước 1: Cập nhật dữ liệu thời tiết (Tùy chọn)
Nếu bạn muốn lấy dữ liệu mới nhất từ NASA:
```bash
python vn_data_pipeline.py
```
*Kết quả: Tạo file vietnam_smart_irrigation_dataset.csv.*

### Bước 2: Chạy bộ não AI (Fuzzy Logic)
Xử lý dữ liệu thời tiết qua hệ chuyên gia mờ để tính toán lịch tưới:
```bash
python smart_irrigation.py
```
*Kết quả: Tạo file fuzzy_irrigation_results.csv và biểu đồ mô phỏng fuzzy_simulation_plot.png.*

### Bước 3: Khởi chạy Giao diện Dashboard
Mở máy chủ web để theo dõi trực quan:
```bash
python app.py
```
Sau đó, mở trình duyệt web và truy cập vào địa chỉ:
Link: http://127.0.0.1:5000

---

## Cấu Trúc Thư Mục
- app.py: Server Backend (Flask).
- smart_irrigation.py: Triển khai Logic mờ (AI Phase 1).
- vn_data_pipeline.py: Thu thập dữ liệu từ NASA.
- dashboard/: Chứa mã nguồn giao diện (HTML, CSS, JS).
- *.csv: Các bộ dữ liệu thu thập và kết quả tính toán.

## Lộ Trình Phát Triển Tiếp Theo
- Phase 2 (MLP): Huấn luyện mạng Nơ-ron để dự báo mưa chính xác hơn.
- Phase 3 (CNN): Tích hợp camera nhận diện tình trạng héo/tươi của lá cây.
