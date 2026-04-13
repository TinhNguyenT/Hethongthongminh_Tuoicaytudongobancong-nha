import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyIrrigationController:
    """Mô-đun Hệ chuyên gia Logic mờ (Phase 1)"""
    
    def __init__(self):
        # Định nghĩa các biến mờ
        self.moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'moisture')
        self.temp = ctrl.Antecedent(np.arange(0, 51, 1), 'temp')
        self.rain = ctrl.Antecedent(np.arange(0, 101, 1), 'rain')
        self.duration = ctrl.Consequent(np.arange(0, 31, 1), 'duration')

        # Cấu hình hàm liên thuộc
        self._setup_membership_functions()
        # Thiết lập bộ luật
        self.sim = self._setup_rules()

    def _setup_membership_functions(self):
        self.moisture['dry'] = fuzz.trimf(self.moisture.universe, [0, 0, 45])
        self.moisture['moist'] = fuzz.trimf(self.moisture.universe, [35, 55, 75])
        self.moisture['wet'] = fuzz.trimf(self.moisture.universe, [65, 100, 100])

        self.temp['cool'] = fuzz.trimf(self.temp.universe, [0, 0, 22])
        self.temp['warm'] = fuzz.trimf(self.temp.universe, [18, 30, 35])
        self.temp['hot'] = fuzz.trimf(self.temp.universe, [30, 50, 50])

        self.rain['none'] = fuzz.trimf(self.rain.universe, [0, 0, 2])
        self.rain['light'] = fuzz.trimf(self.rain.universe, [1, 5, 10])
        self.rain['heavy'] = fuzz.trimf(self.rain.universe, [8, 100, 100])

        self.duration['none'] = fuzz.trimf(self.duration.universe, [0, 0, 5])
        self.duration['short'] = fuzz.trimf(self.duration.universe, [3, 10, 15])
        self.duration['medium'] = fuzz.trimf(self.duration.universe, [12, 18, 22])
        self.duration['long'] = fuzz.trimf(self.duration.universe, [20, 30, 30])

    def _setup_rules(self):
        rules = [
            # Khi đất ướt -> Không bao giờ tưới
            ctrl.Rule(self.moisture['wet'], self.duration['none']),
            
            # Khi đất khô
            ctrl.Rule(self.moisture['dry'] & self.temp['hot'] & self.rain['none'], self.duration['long']),
            ctrl.Rule(self.moisture['dry'] & self.temp['warm'] & self.rain['none'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.temp['cool'] & self.rain['none'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.rain['light'], self.duration['medium']),
            ctrl.Rule(self.moisture['dry'] & self.rain['heavy'], self.duration['none']),
            
            # Khi đất hơi ẩm (moist)
            ctrl.Rule(self.moisture['moist'] & self.temp['hot'] & self.rain['none'], self.duration['medium']),
            ctrl.Rule(self.moisture['moist'] & self.temp['warm'] & self.rain['none'], self.duration['short']),
            ctrl.Rule(self.moisture['moist'] & self.temp['cool'] & self.rain['none'], self.duration['none']),
            ctrl.Rule(self.moisture['moist'] & self.rain['heavy'], self.duration['none']),
        ]
        system = ctrl.ControlSystem(rules)
        return ctrl.ControlSystemSimulation(system)

    def decide(self, moisture_val, temp_val, predicted_rain_mm):
        """Ra quyết định thời gian tưới dựa trên các thông số đầu vào"""
        self.sim.input['moisture'] = moisture_val
        self.sim.input['temp'] = temp_val
        self.sim.input['rain'] = predicted_rain_mm
        
        try:
            self.sim.compute()
            return round(float(self.sim.output['duration']), 2)
        except:
            return 0.0
