# config.py
# File cấu hình trung tâm cho Hệ thống Tưới cây AI

# ---------------------------------------------------------
# CHẾ ĐỘ HOẠT ĐỘNG
# ---------------------------------------------------------
# Đặt thành False khi bạn kết nối phần cứng thật (ESP32/IoT)
# Đặt thành True nếu muốn dùng dữ liệu giả lập (khi code giao diện)
USE_SIMULATION = False

# ---------------------------------------------------------
# THIẾT LẬP SERVER & MẠNG
# ---------------------------------------------------------
HOST = "0.0.0.0"     # Lắng nghe mọi địa chỉ IP
PORT = 5000          # Cổng API cho Backend Flask

# ---------------------------------------------------------
# CẤU HÌNH AI & LOGIC
# ---------------------------------------------------------
# Mức dung lượng nước tối thiểu trong bình chứa (dưới mức này máy bơm sẽ khóa)
MIN_WATER_LEVEL_PROTECTION = 10.0

# Lưu tối đa số điểm dữ liệu trên biểu đồ (tránh tràn RAM)
MAX_HISTORY_POINTS = 50
