import numpy as np
import joblib
import os
import pandas as pd

class MLPPredictor:
    """Mô-đun Bộ não AI bằng Mạng Nơ-ron MLP (Decision Brain)"""
    
    def __init__(self, model_path='models/mlp_irrigation_model.pkl', scaler_path='models/irrigation_scaler.pkl'):
        self.model = None
        self.scaler = None
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        else:
            print(f"Cảnh báo: Không tìm thấy mô hình tại {model_path}. Cần chạy scripts/train_models.py trước.")

    def decide(self, temp, humidity, rain, soil_moisture):
        """Ra quyết định tưới (0 hoặc 1) dựa trên trí tuệ nhân tạo"""
        if self.model is None or self.scaler is None:
            return 0
            
        # Chuẩn bị dữ liệu đầu vào (phải đúng tên cột như lúc huấn luyện)
        input_data = pd.DataFrame([[temp, humidity, rain, soil_moisture]], 
                                 columns=['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture'])
        
        # Chuẩn hóa
        input_scaled = self.scaler.transform(input_data)
        
        # Dự đoán
        prediction = self.model.predict(input_scaled)[0]
        return int(prediction)

    def get_probabilities(self, temp, humidity, rain, soil_moisture):
        """Lấy xác suất tin cậy của AI"""
        if self.model is None or self.scaler is None:
            return [1.0, 0.0]
            
        input_data = pd.DataFrame([[temp, humidity, rain, soil_moisture]], 
                                 columns=['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture'])
        input_scaled = self.scaler.transform(input_data)
        return self.model.predict_proba(input_scaled)[0]
