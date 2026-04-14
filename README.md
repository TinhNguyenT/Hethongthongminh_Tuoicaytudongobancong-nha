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

