import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_datasets(num_days=365):
    """
    Sinh dữ liệu mô phỏng cho Weather (thời tiết) và Soil Moisture (độ ẩm đất).
    Dữ liệu này có thể dùng để train mạng MLP hoặc thiết kế luật mờ (Fuzzy Logic).
    """
    
    # 1. Cài đặt thời gian bắt đầu
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # -------------------------------------------------------------
    # 1. TẠO WEATHER DATASET (Dự báo thời tiết 1 lần/ngày)
    # -------------------------------------------------------------
    print("Đang tạo Weather Dataset...")
    
    # Giả lập Nhiệt độ trung bình (20 - 40 độ C, có tính chu kỳ mùa)
    temperatures = 25 + 10 * np.sin(np.linspace(0, 3.14 * 2, num_days)) + np.random.normal(0, 2, num_days)
    temperatures = np.clip(temperatures, 15, 45) # Ép trong khoảng thực tế ở VN
    
    # Giả lập Độ ẩm không khí (%)
    humidity = 70 - 15 * np.sin(np.linspace(0, 3.14 * 2, num_days)) + np.random.normal(0, 5, num_days)
    humidity = np.clip(humidity, 30, 95)
    
    # Giả lập khả năng có mưa (dựa vào độ ẩm không khí và yếu tố ngẫu nhiên)
    rain_prob = (humidity - 30) / 65 * 0.5 + np.random.uniform(0, 0.5, num_days)
    rain_prob = np.clip(rain_prob, 0, 1.0)
    
    # Xác định trạng thái thực tế có mưa không (nhãn cho MLP học)
    is_raining = (rain_prob > 0.6).astype(int) # 1 là mưa, 0 là không mưa

    weather_df = pd.DataFrame({
        'Date': dates,
        'Temperature_C': np.round(temperatures, 1),
        'Humidity_percent': np.round(humidity, 1),
        'Rain_Probability': np.round(rain_prob, 2),
        'Is_Raining': is_raining
    })
    
    weather_df.to_csv('weather_dataset.csv', index=False)
    print(f"Đã lưu 'weather_dataset.csv' với {num_days} bản ghi.")

    # -------------------------------------------------------------
    # 2. TẠO SOIL MOISTURE DATASET (Dữ liệu chênh lệch theo từng giờ)
    # -------------------------------------------------------------
    print("Đang tạo Soil Moisture Dataset...")
    
    # Mỗi ngày có 24 giờ
    hours = num_days * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    
    soil_moisture = []
    pump_status = []
    
    current_moisture = 60.0 # Bắt đầu ở hệ số 60%
    
    for i in range(hours):
        day_idx = i // 24 # Lấy Index của Weather Dataset tương ứng
        temp = temperatures[day_idx]
        rain = is_raining[day_idx]
        
        # Bốc hơi phụ thuộc 1 phần vào nhiệt độ (trời càng nóng bốc hơi càng nhanh)
        evaporation_rate = (temp / 40.0) * 1.2 + np.random.normal(0, 0.1)
        current_moisture -= evaporation_rate
        
        # Nếu đang là ngày mưa, độ ẩm tăng lên ngẫu nhiên
        if rain:
            current_moisture += np.random.uniform(5, 10)
            
        # Logic tưới cây (giả định dùng để sinh label cho bơm)
        pump_on = 0
        if current_moisture < 40.0:  # Ngưỡng khô: dưới 40%
            if not rain:             # Chỉ bơm khi không mưa
                pump_on = 1
                current_moisture += 25.0 # Lượng nước cung cấp đẩy độ ẩm lên
            
        # Chặn tối đa và tối thiểu của độ ẩm đất (chỉ nằm trong 15% - 95%)
        current_moisture = np.clip(current_moisture, 15, 95)
        
        soil_moisture.append(np.round(current_moisture, 1))
        pump_status.append(pump_on)
        
    soil_moisture_df = pd.DataFrame({
        'Datetime': timestamps,
        'Soil_Moisture': soil_moisture,
        'Pump_ON': pump_status
    })
    
    soil_moisture_df.to_csv('soil_moisture_dataset.csv', index=False)
    print(f"Đã lưu 'soil_moisture_dataset.csv' với {hours} bản ghi.")
    
if __name__ == "__main__":
    generate_datasets(365) # Sinh dữ liệu giả lập sử dụng cho 1 năm (365 ngày)
    print("-> TẠO DATASET THÀNH CÔNG!")
