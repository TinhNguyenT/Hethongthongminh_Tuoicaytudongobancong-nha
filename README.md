# Hệ Thống Tưới Cây Thông Minh AI - Ban Công & Nhà Ở

Dự án này là một hệ thống tưới cây tự động tích hợp các công nghệ AI (Fuzzy Logic, MLP, CNN) và dữ liệu khí tượng thực tế từ Việt Nam.

## Cấu Trúc Thư Mục (Modular Architecture)
Dự án được tổ chức theo cấu trúc mô-đun hóa để dễ dàng quản lý:

- app.py: Server chính phục vụ Dashboard web.
- core/: Chứa các bộ não AI (Fuzzy Logic, MLP, CNN Scanner).
- models/: Lưu trữ các mô hình đã huấn luyện (.pkl).
- data/: Lưu trữ các tập dữ liệu CSV và biểu đồ kết quả.
- scripts/: Chứa các công cụ thu thập dữ liệu và huấn luyện.
- frontend/: Giao diện người dùng Web (React/Vite).

## Yêu Cầu Cài Đặt
```bash
pip install flask flask-cors pandas requests scikit-fuzzy matplotlib scikit-learn joblib
```

## Hướng Dẫn Vận Hành

### Bước 1: Thu thập dữ liệu khí tượng (NASA/OpenWeather)
```bash
python scripts/fetch_data.py
```

### Bước 2: Xử lý dữ liệu cảm biến & Tạo tập huấn luyện
```bash
python scripts/preprocess_soil_data.py
python scripts/build_final_dataset.py
```

### Bước 3: Huấn luyện bộ não AI (MLP)
```bash
python scripts/train_models.py
```

### Bước 4: Khởi chạy Web Dashboard
```bash
python app.py
```
Link: http://127.0.0.1:5000

---

Người 1: Xây dựng Module MLP (Mạng nơ-ron dự báo)


Nhiệm vụ: Không dùng MLP để phân loại (0/1) nữa, mà dùng nó để dự báo (Regression/Forecasting) giống như cách thầy dự báo nhiệt độ.

Đầu vào (Input): Nhiệt độ, Độ ẩm không khí hiện tại.

Đầu ra (Output): Dự báo Độ ẩm đất trong 1 giờ tới (Hoặc dự báo khả năng có mưa).

Bản chất: Module này giúp hệ thống "nhìn trước" được thời tiết để không tưới dư thừa.

Người 2: Xây dựng Module FLC (Logic Mờ)


Nhiệm vụ: Tạo bộ luật điều khiển để ra lệnh cho máy bơm.

Đầu vào (Input): 1. Độ ẩm đất hiện tại (từ cảm biến).
2. Độ ẩm đất dự báo (nhận từ người 1).

Đầu ra (Output): Thời gian bật bơm (Ví dụ: Tắt, Bơm 10 giây, Bơm 30 giây).


Bản chất: Ví dụ luật mờ: NẾU đất hiện tại "Hơi khô" VÀ dự báo 1 giờ tới "rất khô" THÌ bơm "30 giây".