import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyIrrigationController:
    """Mô-đun Hệ chuyên gia Logic mờ Nâng cao (FLC)"""
    
    def __init__(self):
        # Định nghĩa các biến mờ (Antecedents & Consequent)
        # Vũ trụ (Universe) cho các biến
        self.moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'moisture')
        self.temp = ctrl.Antecedent(np.arange(0, 51, 1), 'temp')
        self.humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')
        self.rain = ctrl.Antecedent(np.arange(0, 101, 1), 'rain')
        self.duration = ctrl.Consequent(np.arange(0, 11, 1), 'duration')

        # Cấu hình hàm liên thuộc
        self._setup_membership_functions()
        # Thiết lập bộ luật
        self.sim = self._setup_rules()

    def _setup_membership_functions(self):
        # Độ ẩm đất (Sử dụng trapmf cho các đầu biên)
        self.moisture['very_dry'] = fuzz.trapmf(self.moisture.universe, [0, 0, 15, 30])
        self.moisture['dry'] = fuzz.trimf(self.moisture.universe, [20, 40, 60])
        self.moisture['moist'] = fuzz.trimf(self.moisture.universe, [50, 70, 85])
        self.moisture['wet'] = fuzz.trapmf(self.moisture.universe, [75, 90, 100, 100])

        # Nhiệt độ
        self.temp['cold'] = fuzz.trapmf(self.temp.universe, [0, 0, 10, 18])
        self.temp['cool'] = fuzz.trimf(self.temp.universe, [15, 22, 28])
        self.temp['warm'] = fuzz.trimf(self.temp.universe, [25, 32, 38])
        self.temp['hot'] = fuzz.trapmf(self.temp.universe, [35, 42, 50, 50])

        # Độ ẩm không khí
        self.humidity['low'] = fuzz.trapmf(self.humidity.universe, [0, 0, 30, 50])
        self.humidity['medium'] = fuzz.trimf(self.humidity.universe, [40, 60, 80])
        self.humidity['high'] = fuzz.trapmf(self.humidity.universe, [70, 85, 100, 100])

        # Lượng mưa dự báo
        self.rain['none'] = fuzz.trapmf(self.rain.universe, [0, 0, 1, 3])
        self.rain['light'] = fuzz.trimf(self.rain.universe, [2, 5, 12])
        self.rain['heavy'] = fuzz.trapmf(self.rain.universe, [10, 20, 100, 100])

        # Thời gian tưới (Đầu ra) - Đã thu nhỏ cho chậu nhỏ (0-10 phút)
        self.duration['none'] = fuzz.trapmf(self.duration.universe, [0, 0, 0.5, 1.5])
        self.duration['short'] = fuzz.trimf(self.duration.universe, [1, 3, 5])
        self.duration['medium'] = fuzz.trimf(self.duration.universe, [4, 6, 8])
        self.duration['long'] = fuzz.trapmf(self.duration.universe, [7, 9, 10, 10])

    def _setup_rules(self):
        rules = [
            # NHÓM LUẬT AN TOÀN (Ngắt ngay nếu đủ ẩm hoặc mưa lớn)
            ctrl.Rule(self.moisture['wet'], self.duration['none']),
            ctrl.Rule(self.rain['heavy'], self.duration['none']),
            
            # NHÓM LUẬT ĐẤT RẤT KHÔ (Very Dry)
            ctrl.Rule(self.moisture['very_dry'] & self.temp['hot'], self.duration['long']),
            ctrl.Rule(self.moisture['very_dry'] & self.temp['warm'] & self.humidity['low'], self.duration['long']),
            ctrl.Rule(self.moisture['very_dry'] & self.temp['warm'] & self.humidity['medium'], self.duration['medium']),
            ctrl.Rule(self.moisture['very_dry'] & self.temp['warm'] & self.humidity['high'], self.duration['medium']),
            ctrl.Rule(self.moisture['very_dry'] & self.temp['cool'], self.duration['medium']),
            ctrl.Rule(self.moisture['very_dry'] & self.rain['light'], self.duration['short']),
            
            # NHÓM LUẬT ĐẤT KHÔ (Dry)
            ctrl.Rule(self.moisture['dry'] & self.temp['hot'] & self.humidity['low'], self.duration['long']),
            ctrl.Rule(self.moisture['dry'] & self.temp['hot'] & self.humidity['medium'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.temp['hot'] & self.humidity['high'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.temp['warm'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.temp['cool'], self.duration['short']),
            ctrl.Rule(self.moisture['dry'] & self.rain['light'], self.duration['none']),
            
            # NHÓM LUẬT ĐẤT HƠI ẨM (Moist)
            ctrl.Rule(self.moisture['moist'] & self.temp['hot'] & self.humidity['low'], self.duration['medium']),
            ctrl.Rule(self.moisture['moist'] & self.temp['hot'] & self.humidity['medium'], self.duration['short']),
            ctrl.Rule(self.moisture['moist'] & self.temp['hot'] & self.humidity['high'], self.duration['short']),
            ctrl.Rule(self.moisture['moist'] & self.temp['warm'], self.duration['short']),
            ctrl.Rule(self.moisture['moist'] & self.temp['cool'], self.duration['none']),
            ctrl.Rule(self.moisture['moist'] & self.rain['light'], self.duration['none']),

            # BỔ SUNG LUẬT CHO CÁC TRƯỜNG HỢP CỰC ĐOAN KHÁC
            ctrl.Rule(self.temp['cold'], self.duration['none']), # Trời lạnh quá không tưới
            ctrl.Rule(self.humidity['high'] & self.moisture['moist'], self.duration['none']),
        ]
        
        system = ctrl.ControlSystem(rules)
        return ctrl.ControlSystemSimulation(system)

    def decide(self, moisture_val, temp_val, predicted_rain_mm, humidity_val=50.0):
        """Ra quyết định thời gian tưới dựa trên các thông số đầu vào"""
        
        # CHUẨN HÓA ĐẦU VÀO: 
        # Nếu moisture_val truyền vào dạng 0.0-1.0 (như trong simulator), nhân với 100
        if moisture_val <= 1.0:
            moisture_val = moisture_val * 100.0
            
        # Kẹp (Clip) giá trị trong phạm vi vũ trụ để tránh lỗi skfuzzy
        moisture_val = np.clip(moisture_val, 0, 100)
        temp_val = np.clip(temp_val, 0, 50)
        humidity_val = np.clip(humidity_val, 0, 100)
        predicted_rain_mm = np.clip(predicted_rain_mm, 0, 100)

        self.sim.input['moisture'] = moisture_val
        self.sim.input['temp'] = temp_val
        self.sim.input['humidity'] = humidity_val
        self.sim.input['rain'] = predicted_rain_mm
        
        try:
            self.sim.compute()
            return round(float(self.sim.output['duration']), 2)
        except Exception as e:
            # Nếu không trúng luật nào hoặc lỗi tính toán, mặc định 0.0
            return 0.0
