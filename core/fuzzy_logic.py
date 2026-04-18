import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyIrrigationController:
    def __init__(self):
        # 1. Khởi tạo các biến (0-100% cho độ ẩm, 0-60s cho thời gian bơm)
        self.hien_tai = ctrl.Antecedent(np.arange(0, 101, 1), 'hien_tai')
        self.tuong_lai = ctrl.Antecedent(np.arange(0, 101, 1), 'tuong_lai')
        self.thoi_gian_bom = ctrl.Consequent(np.arange(0, 61, 1), 'thoi_gian_bom')

        # 2. Định nghĩa hàm liên thuộc cho Đầu vào 1 (Hiện tại)
        # Khô (0 - 45%), Vừa (35 - 75%), Ẩm (65 - 100%)
        self.hien_tai['kho'] = fuzz.trimf(self.hien_tai.universe, [0, 0, 45])
        self.hien_tai['vua'] = fuzz.trimf(self.hien_tai.universe, [35, 55, 75])
        self.hien_tai['am'] = fuzz.trapmf(self.hien_tai.universe, [65, 85, 100, 100])

        # 3. Định nghĩa hàm liên thuộc cho Đầu vào 2 (Tương lai/Dự báo 15p)
        # Khô (0 - 50%), Vừa (40 - 80%), Ẩm (70 - 100%)
        self.tuong_lai['kho'] = fuzz.trimf(self.tuong_lai.universe, [0, 0, 50])
        self.tuong_lai['vua'] = fuzz.trimf(self.tuong_lai.universe, [40, 60, 80])
        self.tuong_lai['am'] = fuzz.trapmf(self.tuong_lai.universe, [70, 90, 100, 100])

        # 4. Định nghĩa hàm liên thuộc cho Đầu ra (Thời gian bơm)
        # Tắt (0s), Ngắn (10-25s), Dài (30-60s)
        self.thoi_gian_bom['tat'] = fuzz.trimf(self.thoi_gian_bom.universe, [0, 0, 5])
        self.thoi_gian_bom['ngan'] = fuzz.trimf(self.thoi_gian_bom.universe, [10, 15, 25])
        self.thoi_gian_bom['dai'] = fuzz.trimf(self.thoi_gian_bom.universe, [30, 45, 60])

        # 5. Thiết lập các Luật Mờ (Fuzzy Rules)
        # Luật 1: Hiện tại Khô -> Bơm Dài (Ưu tiên cứu cây)
        rule1 = ctrl.Rule(self.hien_tai['kho'], self.thoi_gian_bom['dai'])
        
        # Luật 2: Hiện tại Vừa VÀ Dự báo Khô -> Bơm Ngắn (Đón đầu tương lai)
        rule2 = ctrl.Rule(self.hien_tai['vua'] & self.tuong_lai['kho'], self.thoi_gian_bom['ngan'])
        
        # Luật 3: Hiện tại Ẩm HOẶC Dự báo Ẩm -> Tắt (Tiết kiệm nước)
        rule3 = ctrl.Rule(self.hien_tai['am'] | self.tuong_lai['am'], self.thoi_gian_bom['tat'])

        # 6. Khởi tạo hệ thống điều khiển
        self.control_sys = ctrl.ControlSystem([rule1, rule2, rule3])
        self.simulator = ctrl.ControlSystemSimulation(self.control_sys)

    def decide(self, current_soil, predicted_soil):
        """
        Tính toán thời gian bơm dựa trên độ ẩm hiện tại và dự báo.
        Input: 
            current_soil: 0-1.0 (float) hoặc 0-100 (int)
            predicted_soil: 0-1.0 (float) hoặc 0-100 (int)
        Output:
            duration: float (giây)
        """
        # Chuyển đổi về thang 0-100 nếu đầu vào là 0-1.0
        if current_soil <= 1.0:
            current_soil *= 100
        if predicted_soil <= 1.0:
            predicted_soil *= 100

        try:
            self.simulator.input['hien_tai'] = current_soil
            self.simulator.input['tuong_lai'] = predicted_soil
            self.simulator.compute()
            return self.simulator.output['thoi_gian_bom']
        except Exception as e:
            # Trường hợp không khớp luật nào hoặc lỗi tính toán
            print(f"Fuzzy Compute Error: {e}")
            return 0.0

if __name__ == "__main__":
    # Test nhanh
    controller = FuzzyIrrigationController()
    tests = [
        (20, 30), # Khô + Khô -> Dài
        (50, 20), # Vừa + Khô -> Ngắn
        (80, 50), # Ẩm + Vừa -> Tắt
        (50, 80), # Vừa + Ẩm -> Tắt
    ]
    for cur, fut in tests:
        res = controller.decide(cur, fut)
        print(f"Hiện tại: {cur}%, Tương lai: {fut}% -> Bơm: {res:.1f} giây")
