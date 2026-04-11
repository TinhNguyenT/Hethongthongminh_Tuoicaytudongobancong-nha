from flask import Flask, render_template, jsonify, send_from_directory, request
import pandas as pd
import os
import time
from core.fuzzy_logic import FuzzyIrrigationController
from core.mlp_network import MLPPredictor

app = Flask(__name__, static_folder='dashboard', template_folder='dashboard')

# Khởi tạo các bộ não AI
fuzzy = FuzzyIrrigationController()
mlp = MLPPredictor(model_path='models/mlp_model.pkl', scaler_path='models/scaler.pkl')

RESULTS_FILE = 'data/hybrid_irrigation_results.csv'

@app.route('/')
def index():
    """Hiển thị trang chủ dashboard"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API cho Dashboard (Lấy dữ liệu từ file CSV mô phỏng)"""
    if not os.path.exists(RESULTS_FILE):
        return jsonify({"error": "Results file not found."}), 404
    df = pd.read_csv(RESULTS_FILE)
    latest_data = df.tail(30).to_dict(orient='records')
    current = df.iloc[-1].to_dict()
    return jsonify({"current": current, "history": latest_data})

@app.route('/api/hardware', methods=['POST'])
def handle_hardware():
    """API dành riêng cho thiết bị ESP32 gửi dữ liệu thật"""
    try:
        data = request.json
        temp = data.get('temp')
        humidity = data.get('humidity')
        soil = data.get('soil_moisture')

        print(f"\n[HARDWARE] Nhận dữ liệu: Temp={temp}C, Humid={humidity}%, Soil={soil}%")

        # 1. Dùng MLP để dự báo lượng mưa dựa trên Temp/Humid thật
        predicted_rain = mlp.predict_rain(temp, humidity)

        # 2. Dùng Fuzzy để ra quyết định thời gian tưới
        irrigation_duration = fuzzy.decide(soil, temp, predicted_rain)

        # 3. Trả về lệnh cho ESP32
        response = {
            "status": "success",
            "irrigation_duration": irrigation_duration,
            "pump_on": True if irrigation_duration > 0 else False,
            "predicted_rain_mm": round(predicted_rain, 2)
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Lỗi xử lý dữ liệu hardware: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<path:path>')
def send_static(path):
    """Phục vụ các file tĩnh như css, js"""
    return send_from_directory('dashboard', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("SMART IRRIGATION SERVER IS STARTING...")
    print("Server đang lắng nghe cả Dashboard và Thiết bị ESP32")
    # Để ESP32 kết nối được, cần chạy host='0.0.0.0'
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
