# Hệ Thống Tưới Cây Thông Minh AI - Ban Công & Nhà Ở

Dự án này là một hệ thống tưới cây tự động tích hợp các công nghệ AI (Fuzzy Logic, MLP, CNN) và dữ liệu khí tượng thực tế từ Việt Nam.

## Cấu Trúc Thư Mục (Modular Architecture)
Dự án được tổ chức theo cấu trúc mô-đun hóa để dễ dàng quản lý:

- app.py: Server chính phục vụ Dashboard web.
- main.py: Script chạy mô phỏng tích hợp (CLI).
- core/: Chứa các bộ não AI (Fuzzy Logic, MLP, CNN Scanner).
- models/: Lưu trữ các mô hình đã huấn luyện (.pkl).
- data/: Lưu trữ các tập dữ liệu CSV và biểu đồ kết quả.
- scripts/: Chứa các công cụ thu thập dữ liệu và huấn luyện.
- dashboard/: Giao diện người dùng Web.

## Yêu Cầu Cài Đặt
```bash
pip install flask pandas requests scikit-fuzzy matplotlib scikit-learn joblib
```

## Hướng Dẫn Vận Hành

### Bước 1: Thu thập dữ liệu
```bash
python scripts/fetch_data.py
```

### Bước 2: Huấn luyện bộ não MLP
```bash
python scripts/train_models.py
```

### Bước 3: Chạy mô phỏng tích hợp (Hybrid AI)
```bash
python main.py
```

### Bước 4: Khởi chạy Dashboard
```bash
python app.py
```
Link: http://127.0.0.1:5000

---

