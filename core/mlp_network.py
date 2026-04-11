import numpy as np
import joblib
import os

class MLPPredictor:
    """Mô-đun dự báo lượng mưa bằng Mạng Nơ-ron MLP (Phase 2)"""
    
    def __init__(self, model_path='models/mlp_model.pkl', scaler_path='models/scaler.pkl'):
        self.model = None
        self.scaler = None
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        else:
            print(f"Cảnh báo: Không tìm thấy mô hình tại {model_path}. Cần huấn luyện MLP trước.")

    def predict_rain(self, temp, humidity):
        """Dự báo lượng mưa dựa trên nhiệt độ và độ ẩm"""
        if self.model is None or self.scaler is None:
            return 0.0
            
        features = np.array([[temp, humidity]])
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        return max(0, float(prediction))
