import requests
import pandas as pd
import json
import time

def fetch_vietnam_weather_data(lat=10.82, lon=106.63, start="20260101", end="20260401"):
    """
    Tải dữ liệu thời tiết thực tế từ NASA POWER API cho tọa độ tại Việt Nam.
    Parameters:
    - T2M: Temperature at 2 Meters (C)
    - RH2M: Relative Humidity at 2 Meters (%)
    - PRECTOTCORR: Precipitation (mm/day)
    """
    print(f"[*] Đang kết nối tới NASA POWER API để lấy dữ liệu cho tọa độ ({lat}, {lon})...")
    
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,RH2M,PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Trích xuất dữ liệu chuỗi thời gian
        base_data = data['properties']['parameter']
        dates = list(base_data['T2M'].keys())
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(dates, format='%Y%m%d'),
            'Temp_C': [base_data['T2M'][d] for d in dates],
            'Humidity_pct': [base_data['RH2M'][d] for d in dates],
            'Precipitation_mm': [base_data['PRECTOTCORR'][d] for d in dates]
        })
        
        print(f"[+] Đã tải thành công {len(df)} ngày dữ liệu thực tế tại Việt Nam.")
        return df
        
    except Exception as e:
        print(f"[!] Lỗi khi tải dữ liệu: {e}")
        return None

def simulate_moisture_from_real_weather(weather_df):
    """
    Mô phỏng độ ẩm đất dựa trên dữ liệu khí tượng thực tế.
    """
    if weather_df is None:
        return
    
    print("[*] Đang bắt đầu mô phỏng độ ẩm đất dựa trên thời tiết thật...")
    
    soil_moisture = []
    pump_status = []
    
    current_moisture = 65.0 # Độ ẩm khởi đầu
    
    for index, row in weather_df.iterrows():
        temp = row['Temp_C']
        humid = row['Humidity_pct']
        rain = row['Precipitation_mm']
        
        # 1. Tính toán bốc hơi (Evapotranspiration đơn giản)
        # Nhiệt độ cao + Độ ẩm thấp = Bốc hơi nhanh
        evap_factor = (temp / 35.0) * (1.1 - (humid / 100.0)) * 2.5
        current_moisture -= evap_factor
        
        # 2. Ảnh hưởng của mưa (1mm mưa ~ tăng 2% độ ẩm đất, giới hạn 15% tăng/ngày)
        if rain > 0.1:
            rain_gain = min(rain * 2.0, 15.0)
            current_moisture += rain_gain
            
        # 3. Logic Máy bơm thông minh
        pump_on = 0
        # Nếu đất khô (< 45%) VÀ không có mưa đáng kể (< 2mm)
        if current_moisture < 45.0 and rain < 2.0:
            pump_on = 1
            current_moisture += 20.0 # Bơm đẩy độ ẩm lên
            
        # Giới hạn độ ẩm trong khoảng [15%, 98%]
        current_moisture = max(15.0, min(98.0, current_moisture))
        
        soil_moisture.append(round(current_moisture, 2))
        pump_status.append(pump_on)
        
    weather_df['Soil_Moisture_pct'] = soil_moisture
    weather_df['Pump_Action'] = pump_status
    
    return weather_df

if __name__ == "__main__":
    # Bước 1: Lấy dữ liệu VN thật
    vn_weather = fetch_vietnam_weather_data()
    
    if vn_weather is not None:
        # Bước 2: Sinh dữ liệu Soil Moisture tương ứng
        final_df = simulate_moisture_from_real_weather(vn_weather)
        
        # Bước 3: Lưu file
        output_file = "vietnam_smart_irrigation_dataset.csv"
        final_df.to_csv(output_file, index=False)
        
        print(f"\n[THÀNH CÔNG] Dataset tổng hợp đã được lưu tại: {output_file}")
        print("-" * 50)
        print("Xem thử 5 dòng dữ liệu đầu tiên:")
        print(final_df.head())
    else:
        print("[!] Không thể tiếp tục do lỗi tải dữ liệu.")
