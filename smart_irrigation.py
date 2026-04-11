import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib

def implement_hybrid_irrigation_system(dataset_path='vietnam_smart_irrigation_dataset.csv'):
    """
    Hệ thống tưới Hybrid kết hợp:
    1. MLP Neural Network: Dự báo lượng mưa từ dữ liệu thời tiết.
    2. Fuzzy Logic: Ra quyết định dựa trên độ ẩm đất và dự báo từ MLP.
    """
    
    # --- PHẦN 1: TẢI CÁC MÔ HÌNH ĐÃ TRAIN ---
    if not os.path.exists('mlp_model.pkl') or not os.path.exists('scaler.pkl'):
        print("[!] Không tìm thấy mô hình MLP. Vui lòng chạy train_mlp.py trước.")
        return

    print("[*] Đang tải mô hình Mạng Nơ-ron MLP...")
    mlp_model = joblib.load('mlp_model.pkl')
    scaler = joblib.load('scaler.pkl')

    # --- PHẦN 2: THIẾT LẬP HỆ MỜ (FUZZY LOGIC) ---
    # Giữ nguyên cấu trúc logic mờ như cũ nhưng tối ưu hóa
    moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'moisture')
    temp = ctrl.Antecedent(np.arange(0, 51, 1), 'temp')
    rain = ctrl.Antecedent(np.arange(0, 101, 1), 'rain')
    duration = ctrl.Consequent(np.arange(0, 31, 1), 'duration')

    # Membership functions
    moisture['dry'] = fuzz.trimf(moisture.universe, [0, 0, 45])
    moisture['moist'] = fuzz.trimf(moisture.universe, [35, 55, 75])
    moisture['wet'] = fuzz.trimf(moisture.universe, [65, 100, 100])

    temp['cool'] = fuzz.trimf(temp.universe, [0, 0, 22])
    temp['warm'] = fuzz.trimf(temp.universe, [18, 30, 35])
    temp['hot'] = fuzz.trimf(temp.universe, [30, 50, 50])

    # Rain input (MM) - MLP dự báo lượng mưa thực tế
    rain['none'] = fuzz.trimf(rain.universe, [0, 0, 2])
    rain['light'] = fuzz.trimf(rain.universe, [1, 5, 10])
    rain['heavy'] = fuzz.trimf(rain.universe, [8, 100, 100])

    duration['none'] = fuzz.trimf(duration.universe, [0, 0, 5])
    duration['short'] = fuzz.trimf(duration.universe, [3, 10, 15])
    duration['medium'] = fuzz.trimf(duration.universe, [12, 18, 22])
    duration['long'] = fuzz.trimf(duration.universe, [20, 30, 30])

    # Rules
    rules = [
        ctrl.Rule(moisture['wet'], duration['none']),
        ctrl.Rule(moisture['dry'] & temp['hot'] & rain['none'], duration['long']),
        ctrl.Rule(moisture['dry'] & rain['heavy'], duration['none']), # Có mưa to thì không tưới
        ctrl.Rule(moisture['dry'] & rain['light'], duration['medium']),
        ctrl.Rule(moisture['moist'] & rain['none'], duration['short']),
        ctrl.Rule(moisture['moist'] & rain['heavy'], duration['none']),
    ]

    irrigation_sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

    # --- PHẦN 3: CHẠY MÔ PHỎNG TÍCH HỢP (HYBRID) ---
    df = pd.read_csv(dataset_path)
    print(f"[*] Đang mô phỏng Hệ thống Hybrid (MLP + Fuzzy) trên {len(df)} dòng dữ liệu...")

    mlp_predictions = []
    final_durations = []

    for index, row in df.iterrows():
        # A. Dùng MLP để "Tiên đoán" lượng mưa (Forecasting)
        features = np.array([[row['Temp_C'], row['Humidity_pct']]])
        features_scaled = scaler.transform(features)
        predicted_rain = max(0, mlp_model.predict(features_scaled)[0])
        mlp_predictions.append(round(predicted_rain, 2))

        # B. Dùng kết quả Tiên đoán làm đầu vào cho Hệ mờ
        irrigation_sim.input['moisture'] = row['Soil_Moisture_pct']
        irrigation_sim.input['temp'] = row['Temp_C']
        irrigation_sim.input['rain'] = predicted_rain
        
        try:
            irrigation_sim.compute()
            res = irrigation_sim.output['duration']
        except:
            res = 0
            
        final_durations.append(round(res, 2))

    df['MLP_Predicted_Rain'] = mlp_predictions
    df['Fuzzy_Hybrid_Duration'] = final_durations
    
    # Xuất kết quả
    output_path = 'hybrid_irrigation_results.csv'
    df.to_csv(output_path, index=False)
    print(f"Hoàn thành! Kết quả Hybrid lưu tại: {output_path}")

    # Vẽ biểu đồ so sánh
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'][:50], df['Soil_Moisture_pct'][:50], label='Actual Soil Moisture', color='green')
    plt.bar(df['Date'][:50], df['Fuzzy_Hybrid_Duration'][:50], label='Hybrid Decision (min)', color='purple', alpha=0.5)
    plt.title('Hybrid AI Control: Using Neural Network Predictions for Fuzzy Decision')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('hybrid_simulation_plot.png')
    print("Đã lưu biểu đồ Hybrid: hybrid_simulation_plot.png")

if __name__ == "__main__":
    implement_hybrid_irrigation_system()
