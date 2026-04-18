import joblib
import os
import numpy as np

class MLPPredictor:
    def __init__(self, model_path='data/mlp_forecasting.pkl'):
        # Load model and scaler
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.features = data['features']
            print(f"MLP Model loaded from {model_path}")
            print(f"Features expected: {self.features}")
        else:
            self.model = None
            self.scaler = None
            self.features = []
            print(f"Warning: MLP Model not found at {model_path}")

    def predict(self, temp, humidity, current_soil):
        """
        Dự báo độ ẩm đất sau 15 phút.
        Input:
            temp: Nhiệt độ hiện tại (C)
            humidity: Độ ẩm không khí (%)
            current_soil: Độ ẩm đất hiện tại (%)
        Output:
            predicted_soil: Độ ẩm đất dự báo (%)
        """
        if self.model is None or self.scaler is None:
            # Fallback nếu không có model (giữ nguyên độ ẩm hiện tại)
            return current_soil

        # Chuẩn bị dữ liệu đầu vào (phải đúng thứ tự FEATURES trong training)
        # FEATURES = ['Temperature_C', 'humidity', 'water_level']
        # Lưu ý: water_level trong training chính là soil moisture
        input_data = np.array([[temp, humidity, current_soil]])
        
        # Scale dữ liệu
        input_scaled = self.scaler.transform(input_data)
        
        # Dự báo
        prediction = self.model.predict(input_scaled)[0]
        
        # Giới hạn trong khoảng vật lý [0, 100]
        return float(np.clip(prediction, 0, 100))

    def decide(self, temp, humidity, rain, current_soil):
        """
        Hàm cũ để tương thích với app.py hiện tại (nếu cần). 
        Tuy nhiên, logic mới sẽ dùng predict() rồi quăng vào Fuzzy.
        """
        pred = self.predict(temp, humidity, current_soil * 100 if current_soil <= 1.0 else current_soil)
        # Giả sử trả về 1 nếu đất dự báo < 40% (logic cũ đơn giản)
        return 1 if pred < 40 else 0

if __name__ == "__main__":
    # Test nhanh
    predictor = MLPPredictor('data/mlp_forecasting.pkl')
    # Thử với 1 sample
    p = predictor.predict(30, 60, 45)
    print(f"Dự báo sau 15p: {p:.2f}%")
