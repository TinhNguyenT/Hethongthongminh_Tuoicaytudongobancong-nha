from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import os
import time
import threading
from core.fuzzy_logic import FuzzyIrrigationController
from core.mlp_network import MLPPredictor

app = Flask(__name__)
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
    sim_soil = 0.65 # Bắt đầu ở mức 65%
    
    while True:
        row = weather_2026.iloc[row_idx % len(weather_2026)]
        
        # Mô phỏng đất khô dần (nếu ko tưới)
        if system_data["current"]["pump_status"] == 1:
            sim_soil += 0.2 # Tưới làm tăng độ ẩm
        else:
            # Khô nhanh hơn nếu trời nóng
            evap = (row['Temp_C'] / 35.0) * 0.02
            sim_soil -= evap
        
        sim_soil = max(0.05, min(0.95, sim_soil))
        
        # HỎI BỘ N\u00c3O AI
        decision = mlp.decide(row['Temp_C'], row['Humidity_pct'], row['Precipitation_mm'], sim_soil)
        probs = mlp.get_probabilities(row['Temp_C'], row['Humidity_pct'], row['Precipitation_mm'], sim_soil)
        
        # Cập nhật trạng thái
        current_data = {
            "timestamp": time.strftime("%H:%M:%S"),
            "air_temp": round(row['Temp_C'], 1),
            "air_humidity": round(row['Humidity_pct'], 1),
            "rain_mm": round(row['Precipitation_mm'], 1),
            "soil_moisture": round(sim_soil, 2),
            "pump_status": decision,
            "ai_confidence": round(max(probs) * 100, 1),
            "source": "NASA 2026 SIM"
        }
        
        system_data["current"] = current_data
        system_data["history"].append(current_data)
        if len(system_data["history"]) > 50:
            system_data["history"].pop(0)
            
        row_idx += 1
        time.sleep(5) # Mỗi 5 giây cập nhật một mốc thời gian mới

# Chạy Simulator trong luồng riêng
threading.Thread(target=start_simulation, daemon=True).start()

# --- CÁC ENDPOINT ROUTE ---

@app.route('/')
def index():
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

        # Hỏi AI
        decision = mlp.decide(temp, humidity, rain, soil)
        
        # Cập nhật hệ thống bằng dữ liệu thật
        current_data = {
            "timestamp": time.strftime("%H:%M:%S"),
            "air_temp": temp,
            "air_humidity": humidity,
            "rain_mm": rain,
            "soil_moisture": soil,
            "pump_status": decision,
            "ai_confidence": 100.0, # Giả sử hardware thì tin cậy input
            "source": "HARDWARE (ESP32)"
        }
        system_data["current"] = current_data
        
        return jsonify({
            "status": "success",
            "pump_action": decision, # ESP32 nhận cái này để bật Relay
            "message": "AI Brain processed successfully"
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('dashboard', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("AI SMART IRRIGATION DASHBOARD IS RUNNING")
    print("Simulation: ACTIVE (NASA 2026 Data)")
    print("Endpoint Hardware: /api/hardware")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
