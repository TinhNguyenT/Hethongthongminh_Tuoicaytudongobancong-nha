import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import matplotlib.pyplot as plt
import os

def implement_fuzzy_logic_controller(dataset_path='vietnam_smart_irrigation_dataset.csv'):
    """
    Triển khai Hệ chuyên gia Logic mờ (FLC) để quyết định thời gian tưới dựa trên:
    - Soil Moisture (Độ ẩm đất)
    - Temperature (Nhiệt độ)
    - Rain Probability (Khả năng mưa)
    """
    
    # 1. KHỞI TẠO CÁC BIẾN MỜ (ANTECEDENTS & CONSEQUENTS)
    # --------------------------------------------------
    # Antecedents: Đầu vào
    moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'moisture')
    temp = ctrl.Antecedent(np.arange(0, 51, 1), 'temp')
    rain = ctrl.Antecedent(np.arange(0, 101, 1), 'rain')
    
    # Consequent: Đầu ra (Thời gian tưới tính bằng phút)
    duration = ctrl.Consequent(np.arange(0, 31, 1), 'duration')

    # 2. ĐỊNH NGHĨA CÁC HÀM LIÊN THUỘC (MEMBERSHIP FUNCTIONS)
    # -------------------------------------------------------
    # Độ ẩm đất: Khô (Dry), Ẩm (Moist), Ướt (Wet)
    moisture['dry'] = fuzz.trimf(moisture.universe, [0, 0, 45])
    moisture['moist'] = fuzz.trimf(moisture.universe, [35, 55, 75])
    moisture['wet'] = fuzz.trimf(moisture.universe, [65, 100, 100])

    # Nhiệt độ: Mát (Cool), Ấm (Warm), Nóng (Hot)
    temp['cool'] = fuzz.trimf(temp.universe, [0, 0, 22])
    temp['warm'] = fuzz.trimf(temp.universe, [18, 30, 35])
    temp['hot'] = fuzz.trimf(temp.universe, [30, 50, 50])

    # Khả năng mưa: Thấp (Low), Vừa (Medium), Cao (High)
    rain['low'] = fuzz.trimf(rain.universe, [0, 0, 40])
    rain['medium'] = fuzz.trimf(rain.universe, [30, 60, 80])
    rain['high'] = fuzz.trimf(rain.universe, [70, 100, 100])

    # Thời gian tưới: Không (None), Ngắn (Short), TB (Medium), Dài (Long)
    duration['none'] = fuzz.trimf(duration.universe, [0, 0, 5])
    duration['short'] = fuzz.trimf(duration.universe, [3, 10, 15])
    duration['medium'] = fuzz.trimf(duration.universe, [12, 18, 22])
    duration['long'] = fuzz.trimf(duration.universe, [20, 30, 30])

    # 3. THIẾT LẬP CÁC BỘ LUẬT (RULE BASE)
    # ------------------------------------
    rules = [
        # Nhóm luật 1: Đất Ướt thì không tưới bất chấp các yếu tố khác
        ctrl.Rule(moisture['wet'], duration['none']),
        
        # Nhóm luật 2: Đất Khô VÀ Trời Nóng VÀ Sắp mưa ít -> Tưới lâu nhất
        ctrl.Rule(moisture['dry'] & temp['hot'] & rain['low'], duration['long']),
        
        # Nhóm luật 3: Đất Khô VÀ Trời Nóng VÀ Sắp mưa nhiều -> Giảm tưới xuống mức trung bình
        ctrl.Rule(moisture['dry'] & temp['hot'] & rain['high'], duration['medium']),
        
        # Nhóm luật 4: Đất Khô VÀ Trời Mát -> Tưới trung bình
        ctrl.Rule(moisture['dry'] & temp['cool'], duration['medium']),
        
        # Nhóm luật 5: Đất Ẩm VÀ Trời Nóng VÀ Sắp mưa ít -> Tưới ngắn
        ctrl.Rule(moisture['moist'] & temp['hot'] & rain['low'], duration['short']),
        
        # Nhóm luật 6: Đất Ẩm VÀ Sắp mưa nhiều -> Không tưới (đợi mưa)
        ctrl.Rule(moisture['moist'] & rain['high'], duration['none']),
        
        # Nhóm luật 7: Đất Ẩm VÀ Trời Ấm -> Tưới ngắn
        ctrl.Rule(moisture['moist'] & temp['warm'] & rain['low'], duration['short']),
    ]

    # 4. KHỞI TẠO BỘ ĐIỀU KHIỂN
    # -------------------------
    irrigation_ctrl = ctrl.ControlSystem(rules)
    irrigation_sim = ctrl.ControlSystemSimulation(irrigation_ctrl)

    # 5. MÔ PHỎNG VỚI DỮ LIỆU THỰC TẾ VIỆT NAM
    # ---------------------------------------
    if not os.path.exists(dataset_path):
        print(f"Không tìm thấy file {dataset_path}")
        return

    df = pd.read_csv(dataset_path)
    print(f"Đang chạy hệ mờ trên {len(df)} dòng dữ liệu...")

    fuzzy_results = []
    
    # Ở đây chúng ta tạm lấy Precipitation_mm làm Rain_Probability mô phỏng
    # Thực tế Probability sẽ là Output của MLP (Phần 2)
    for index, row in df.iterrows():
        # Gán đầu vào
        irrigation_sim.input['moisture'] = row['Soil_Moisture_pct']
        irrigation_sim.input['temp'] = row['Temp_C']
        
        # Giả lập Rain Prob: Nếu mưa thật > 5mm thì prob cao, ngược lại prob ngẫu nhiên (nhiễu)
        mock_rain_prob = 80 if row['Precipitation_mm'] > 5 else (row['Precipitation_mm'] * 10 + 10)
        mock_rain_prob = min(100, mock_rain_prob)
        irrigation_sim.input['rain'] = mock_rain_prob
        
        # Tính toán (Defuzzification)
        try:
            irrigation_sim.compute()
            res = irrigation_sim.output['duration']
        except Exception:
            res = 0 # Trường hợp không khớp rule nào (mặc định không tưới)
            
        fuzzy_results.append(round(res, 2))

    df['Fuzzy_Duration_min'] = fuzzy_results
    
    # Lưu kết quả
    output_path = 'fuzzy_irrigation_results.csv'
    df.to_csv(output_path, index=False)
    print(f"Hoàn thành! Kết quả lưu tại: {output_path}")

    # Vẽ biểu đồ kết quả mô phỏng (7 ngày đầu tiên)
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'][:30], df['Soil_Moisture_pct'][:30], label='Soil Moisture (%)', color='green')
    plt.bar(df['Date'][:30], df['Fuzzy_Duration_min'][:30], label='Irrigation (min)', color='blue', alpha=0.5)
    plt.title('30-Day Simulation: Real Weather + Fuzzy Control')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('fuzzy_simulation_plot.png')
    print("Đã lưu biểu đồ mô phỏng: fuzzy_simulation_plot.png")

if __name__ == "__main__":
    implement_fuzzy_logic_controller()
