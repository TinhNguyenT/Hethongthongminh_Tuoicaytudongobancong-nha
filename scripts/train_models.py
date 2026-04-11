import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import os

def train_rain_forecast_model(dataset_path='data/vietnam_smart_irrigation_dataset.csv'):
    """
    Quy trình huấn luyện mạng MLP để dự báo lượng mưa dựa trên thời tiết.
    """
    if not os.path.exists(dataset_path):
        print(f"Lỗi: Không tìm thấy file {dataset_path}")
        return

    # 1. TẢI DỮ LIỆU
    print("Đang tải dữ liệu huấn luyện...")
    df = pd.read_csv(dataset_path)
    
    # 2. LỰA CHỌN TÍNH NĂNG (FEATURES) VÀ MỤC TIÊU (TARGET)
    # Chúng ta dự báo Precipitation (Lượng mưa) dựa trên Temp và Humidity
    X = df[['Temp_C', 'Humidity_pct']]
    y = df['Precipitation_mm']

    # 3. TIỀN XỬ LÝ (PREPROCESSING)
    # Chia tập Train/Test (80-20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Chuẩn hóa dữ liệu (Scaling)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. KHỞI TẠO VÀ HUẤN LUYỆN MẠNG MLP
    print("Bắt đầu quy trình huấn luyện mạng MLP (Neural Network)...")
    # Cấu trúc: 1 lớp ẩn với 100 nơ-ron
    mlp = MLPRegressor(
        hidden_layer_sizes=(100, 50),
        activation='relu',
        solver='adam',
        max_iter=2000,
        random_state=42,
        verbose=True # Hiện quá trình học
    )

    mlp.fit(X_train_scaled, y_train)

    # 5. ĐÁNH GIÁ MÔ HÌNH (EVALUATION)
    y_pred = mlp.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    
    print("\n" + "-"*30)
    print(f"KẾT QUẢ HUẤN LUYỆN:")
    print(f"Độ khớp (R2 Score): {r2:.4f}")
    print(f"Sai số trung bình (MSE): {mse:.4f}")
    print("-"*30)

    # 6. LƯU MÔ HÌNH VÀ SCALER
    joblib.dump(mlp, 'models/mlp_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    print("Đã lưu mô hình thành công tại: models/mlp_model.pkl")

    # 7. TRỰC QUAN HÓA (VISUALIZATION)
    plt.figure(figsize=(10, 6))
    plt.plot(mlp.loss_curve_)
    plt.title('MLP Training Loss Curve')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.grid(True)
    plt.savefig('data/mlp_training_loss.png')
    print("Đã lưu biểu đồ quá trình học: data/mlp_training_loss.png")
    
    # Vẽ biểu đồ dự báo vs thực tế trên tập Test
    plt.figure(figsize=(10, 6))
    plt.plot(y_test.values[:50], label='Actual Rain', color='blue', alpha=0.6)
    plt.plot(y_pred[:50], label='Predicted Rain', color='red', linestyle='dashed')
    plt.title('Rain Forecast Accuracy (Test Set - First 50 samples)')
    plt.legend()
    plt.savefig('data/mlp_forecast_accuracy.png')
    print("Đã lưu biểu đồ so sánh dự báo: data/mlp_forecast_accuracy.png")

if __name__ == "__main__":
    train_rain_forecast_model()
