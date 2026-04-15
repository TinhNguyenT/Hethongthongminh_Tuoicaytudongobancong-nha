from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import time
import threading
import config
from core.fuzzy_logic import FuzzyIrrigationController
from core.mlp_network import MLPPredictor

app = Flask(__name__, static_folder='frontend/dist', template_folder='frontend/dist', static_url_path='/')
CORS(app) # Cho phép React gọi API

# 1. Khởi tạo các bộ não AI
fuzzy = FuzzyIrrigationController()
mlp = MLPPredictor()

# 2. Biến toàn cục để lưu trạng thái hệ thống (giả lập hoặc từ hardware)
system_data = {
    "current": {
        "timestamp": "N/A",
        "air_temp": 30.0,
        "air_humidity": 60.0,
        "rain_mm": 0.0,
        "soil_moisture": 0.5,
        "water_level": 85.0,
        "pump_status": 0,
        "ai_confidence": 0.0,
        "source": "SIMULATION"
    },
    "history": []
}

# --- CƠ CHẾ GIẢ LẬP DỮ LIỆU (Để chạy demo khi chưa có ESP32) ---
def start_simulation():
    global system_data
    # Load dữ liệu thời tiết thực tế 2026 để demo
    weather_2026 = pd.read_csv('data/data_raw/vietnam_weather_2026.csv')
    row_idx = 0
    sim_soil = 0.65      # Bắt đầu ở mức độ ẩm 65%
    sim_water = 100.0    # Bắt đầu ở mức nước 100% trong bình
    refilling = False    # Trạng thái đang châm nước
    refill_steps = 0     # Đếm số tick còn lại để châm đầy

    while True:
        try:
            row = weather_2026.iloc[row_idx % len(weather_2026)]

            # ----------------------------------------------------------------
            # XỬ LÝ CHÂM NƯỚC: Nếu nước < 20% thì bắt đầu châm đầy (mất 5 tick)
            # ----------------------------------------------------------------
            if sim_water < 20.0 and not refilling:
                refilling = True
                refill_steps = 5  # 5 tick × 5s = 25 giây để châm đầy

            if refilling:
                refill_steps -= 1
                sim_water = min(100.0, sim_water + (100.0 / 5))  # Châm từ từ qua 5 bước
                if refill_steps <= 0:
                    sim_water = 100.0
                    refilling = False

            # ----------------------------------------------------------------
            # BẢO VỆ BƠM: Nước < 10% thì không cho phép bơm
            # ----------------------------------------------------------------
            if sim_water < 10.0:
                forced_off = True
            else:
                forced_off = False

            # ----------------------------------------------------------------
            # MÔ PHỎNG ĐỘ ẨM ĐẤT (+ NHIỄU NGẪU NHIÊN)
            # ----------------------------------------------------------------
            # Thêm nhiễu thời tiết để không bị "đều quá"
            temp_noise = np.random.uniform(-0.8, 0.8)
            humid_noise = np.random.uniform(-1.5, 1.5)
            
            current_temp = row['Temp_C'] + temp_noise
            current_humid = row['Humidity_pct'] + humid_noise
            
            # Thêm nhiễu vào quá trình vật lý (bay hơi và tưới)
            soil_noise = np.random.uniform(-0.005, 0.005)
            
            if system_data["current"]["pump_status"] == 1:
                sim_soil += (0.08 + np.random.uniform(0, 0.04)) # Tưới không đều chằn chặn
            else:
                # Khô nhanh hơn nếu trời nóng
                evap = (current_temp / 35.0) * 0.012 + soil_noise
                sim_soil -= max(0, evap)

            sim_soil = max(0.05, min(0.95, sim_soil))

            # HỎI BỘ NÃO AI (Phần quyết định Có/Không)
            decision = mlp.decide(current_temp, current_humid, row['Precipitation_mm'], sim_soil)
            probs = mlp.get_probabilities(current_temp, current_humid, row['Precipitation_mm'], sim_soil)

            # TÍNH TOÁN THỜI LƯỢNG TƯỚI BẰNG LOGIC MỜ (Phần tối ưu hóa)
            duration = fuzzy.decide(sim_soil, current_temp, row['Precipitation_mm'], current_humid)

            # ----------------------------------------------------------------
            # CƯỠNG BỨC TẮT BƠM NẾU HẾT NƯỚC hoặc đang châm nước
            # ----------------------------------------------------------------
            if forced_off or refilling:
                decision = 0
                duration = 0.0

            # ----------------------------------------------------------------
            # GIẢM MỰC NƯỚC KHI BƠM HOẠT ĐỘNG
            # Tăng mức giảm nước lên 3.5% để nhìn thấy rõ ràng hơn
            # ----------------------------------------------------------------
            if decision == 1:
                sim_water -= 3.5 
                sim_water = max(0.0, sim_water)
            
            # Debug LOG ra terminal
            print(f"[{time.strftime('%H:%M:%S')}] Simulating... Pump: {'ON' if decision else 'OFF'} | Soil: {sim_soil:.2f} | Water: {sim_water:.1f}%")

            # Xác định trạng thái nguồn dữ liệu
            if refilling:
                sim_source = "HỆ THỐNG ĐANG TỰ CHÂM NƯỚC"
            elif forced_off:
                sim_source = "CẢNH BÁO: BÌNH NƯỚC ĐÃ CẠN"
            else:
                sim_source = "NASA 2026 (SIMULATED + NOISE)"

            # Cập nhật trạng thái
            current_data = {
                "timestamp": time.strftime("%H:%M:%S"),
                "air_temp": round(current_temp, 1),
                "air_humidity": round(current_humid, 1),
                "rain_mm": round(row['Precipitation_mm'], 1),
                "soil_moisture": round(sim_soil, 2),
                "water_level": round(sim_water, 1),
                "pump_status": int(decision),
                "pump_duration": round(duration, 1) if decision == 1 else 0.0,
                "ai_confidence": round(max(probs) * 100, 1),
                "source": sim_source
            }

            system_data["current"] = current_data
            system_data["history"].append(current_data)
            if len(system_data["history"]) > 50:
                system_data["history"].pop(0)

            row_idx += 1
        except Exception as e:
            print(f"Simulation Error: {e}")
            time.sleep(2) # Đợi một chút nếu lỗi để tránh loop tràn lan
        time.sleep(5)  # Mỗi 5 giây cập nhật một mốc thời gian mới

# Chạy Simulator trong luồng riêng nếu được bật
if config.USE_SIMULATION:
    threading.Thread(target=start_simulation, daemon=True).start()


# --- CÁC ENDPOINT ROUTE ---

@app.route('/')
def index():
    """Serve the React Frontend"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API cho Dashboard lấy dữ liệu hiển thị"""
    return jsonify(system_data)

@app.route('/api/hardware', methods=['POST'])
def handle_hardware():
    """API dành riêng cho thiết bị ESP32 thực tế sau này"""
    try:
        data = request.json
        temp = float(data.get('temp', 25.0))
        humidity = float(data.get('humidity', 60.0))
        soil = float(data.get('soil_moisture', 0.5)) / 100.0 # Chuyển về 0-1.0
        rain = float(data.get('rain_mm', 0.0))
        water = float(data.get('water_level', 100.0))

        # 1. Hỏi AI (MLP quyết định Có/Không)
        decision = mlp.decide(temp, humidity, rain, soil)
        # 2. Tính toán thời lượng bằng Logic mờ
        duration = fuzzy.decide(soil, temp, rain, humidity)
        
        # 3. Logic bảo vệ: Nếu mực nước quá thấp (< 10%), không cho phép bật máy bơm
        if water < 10:
            decision = 0
            duration = 0.0

        # Cập nhật hệ thống bằng dữ liệu thật
        current_data = {
            "timestamp": time.strftime("%H:%M:%S"),
            "air_temp": temp,
            "air_humidity": humidity,
            "rain_mm": rain,
            "soil_moisture": soil,
            "water_level": water,
            "pump_status": decision,
            "pump_duration": duration if decision == 1 else 0.0,
            "ai_confidence": 100.0, # Giả sử hardware thì tin cậy input
            "source": "HARDWARE (ESP32)"
        }
        system_data["current"] = current_data
        
        # Đưa vào history để biểu đồ có thể di chuyển
        system_data["history"].append(current_data)
        if len(system_data["history"]) > config.MAX_HISTORY_POINTS:
            system_data["history"].pop(0)

        
        return jsonify({
            "status": "success",
            "pump_action": decision, # 1 là bật, 0 là tắt
            "pump_duration": duration if decision == 1 else 0.0, # Số phút cần tưới
            "message": "AI Brain processed successfully"
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<path:path>')
def send_assets(path):
    """Serve static assets for React"""
    return send_from_directory('frontend/dist', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("AI SMART IRRIGATION DASHBOARD IS RUNNING")
    if config.USE_SIMULATION:
        print("Mode: SIMULATION (NASA 2026 Data)")
    else:
        print("Mode: HARDWARE (Waiting for ESP32 on /api/hardware)")
    print("Endpoint Hardware: /api/hardware")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
