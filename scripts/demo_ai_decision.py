import joblib
import pandas as pd
import os
import sys

def demo_ai():
    print("="*50)
    print(" CÔNG CỤ KIỂM CHỨNG BỘ N\u00c3O AI (MLP CLASSIFIER)")
    print("="*50)
    print("Dự án: Hệ thống tưới cây thông minh")
    print("Mục tiêu: Chứng minh AI tự quyết định, không dùng if-else.")
    print("-" * 50)

    # 1. Load Model
    model_path = 'models/mlp_irrigation_model.pkl'
    scaler_path = 'models/irrigation_scaler.pkl'
    
    if not os.path.exists(model_path):
        print("Lỗi: Không tìm thấy bộ não AI. Vui lòng chạy huấn luyện trước.")
        return
        
    mlp = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    try:
        # 2. Nhập dữ liệu từ người dùng
        print("\nVui lòng nhập các thông số môi trường để AI 'suy luận':")
        temp = float(input("1. Nhiệt độ không khí (°C) [Ví dụ: 35]: "))
        humid = float(input("2. Độ ẩm không khí (%) [Ví dụ: 40]: "))
        rain = float(input("3. Dự báo lượng mưa (mm) [Ví dụ: 0]: "))
        soil = float(input("4. Độ ẩm đất (0.0 - 1.0) [Ví dụ: 0.35]: "))

        # 3. AI Suy luận
        # Prepare input
        input_data = pd.DataFrame([[temp, humid, rain, soil]], 
                                 columns=['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture'])
        
        # Scale input
        input_scaled = scaler.transform(input_data)
        
        # Predict
        decision = mlp.predict(input_scaled)[0]
        # Get probability (to show it's math!)
        proba = mlp.predict_proba(input_scaled)[0]

        # 4. Hiển thị kết quả
        print("\n" + "-"*30)
        print("KẾT QUẢ TỪ BỘ N\u00c3O AI:")
        if decision == 1:
            print(">>> QUYẾT ĐỊNH: [ BẬT MÁY BƠM ]")
        else:
            print(">>> QUYẾT ĐỊNH: [ TẮT MÁY BƠM ]")
            
        print(f"\nĐộ tin cậy của AI:")
        print(f"- Xác suất Tắt: {proba[0]*100:.2f}%")
        print(f"- Xác suất Bật: {proba[1]*100:.2f}%")
        print("-" * 30)
        print("Bằng chứng: Kết quả trên được tính toán bằng các ma trận trọng số (Weights),")

    except ValueError:
        print("Lỗi: Vui lòng chỉ nhập các con số.")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    demo_ai()