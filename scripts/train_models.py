import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import sys

def train_irrigation_model(dataset_path='data/final_training_dataset.csv'):
    """
    Quy trình huấn luyện mạng MLP (Phân loại) để ra quyết định tưới cây.
    """
    if not os.path.exists(dataset_path):
        print(f"Error: Missing {dataset_path}")
        return

    # 1. TẢI DỮ LIỆU
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # 2. LỰA CHỌN TÍNH NĂNG (FEATURES) VÀ MỤC TIÊU (TARGET)
    X = df[['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture']]
    y = df['irrigation']

    # --- CÂN BẰNG DỮ LIỆU (UNDERSAMPLING) ---
    print("Balancing dataset (Undersampling)...")
    df_0 = df[df.irrigation == 0]
    df_1 = df[df.irrigation == 1]
    
    # Lấy số lượng mẫu của lớp ít nhất (lớp 1)
    n_samples = len(df_1)
    
    # Lấy ngẫu nhiên số lượng tương đương từ lớp 0
    df_0_balanced = df_0.sample(n=n_samples, random_state=42)
    
    # Gộp lại thành dataset cân bằng 50/50
    df_balanced = pd.concat([df_0_balanced, df_1], axis=0)
    
    # --- DATA AUGMENTATION (Sinh dữ liệu giả lập để mở rộng vùng hiểu biết của AI) ---
    print("Generating Synthetic Data to prevent Overfitting on narrowly ranged data...")
    import sys
    sys.path.append(os.getcwd())
    from core.fuzzy_logic import FuzzyIrrigationController
    fuzzy = FuzzyIrrigationController()
    
    np.random.seed(42)
    n_synthetic = 5000
    
    # Tạo các mẫu thời tiết và đất cực đoan ngẫu nhiên
    syn_temp = np.random.uniform(15, 45, n_synthetic)
    syn_humid = np.random.uniform(20, 100, n_synthetic)
    syn_rain = np.random.uniform(0, 50, n_synthetic)
    syn_soil = np.random.uniform(0.0, 1.0, n_synthetic)
    
    synthetic_df = pd.DataFrame({
        'air_temp': syn_temp,
        'air_humidity': syn_humid,
        'rain_mm': syn_rain,
        'soil_moisture': syn_soil
    })
    
    # Tự động dán nhãn cho dữ liệu sinh ra
    def get_synth_label(row):
        duration = fuzzy.decide(row['soil_moisture'] * 100, row['air_temp'], row['rain_mm'])
        return 1 if duration > 13 else 0
        
    synthetic_df['irrigation'] = synthetic_df.apply(get_synth_label, axis=1)
    
    # Gộp dữ liệu thật và dữ liệu sinh ra
    df_final = pd.concat([df_balanced, synthetic_df], axis=0)
    
    X_final = df_final[['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture']]
    y_final = df_final['irrigation']
    
    print(f"Final training distribution:\n{y_final.value_counts()}")

    # 3. TIỀN XỬ LÝ (PREPROCESSING)
    X_train, X_test, y_train, y_test = train_test_split(X_final, y_final, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. KHỞI TẠO VÀ HUẤN LUYỆN MLP CLASSIFIER (Nâng cấp cấu trúc)
    print("Training Upgraded MLP Classifier (128x64x32)...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        solver='adam',
        max_iter=2000,
        random_state=42,
        verbose=False
    )

    mlp.fit(X_train_scaled, y_train)

    # 5. ĐÁNH GIÁ MÔ HÌNH
    y_pred = mlp.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*30)
    print(f"TRAINING RESULTS (Balanced Set):")
    print(f"Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("="*30)

    # 6. LƯU MÔ HÌNH VÀ SCALER
    if not os.path.exists('models'):
        os.makedirs('models')
        
    joblib.dump(mlp, 'models/mlp_irrigation_model.pkl')
    joblib.dump(scaler, 'models/irrigation_scaler.pkl')
    print("Saved model to models/mlp_irrigation_model.pkl")

    # 7. TRỰC QUAN HÓA
    plt.figure(figsize=(10, 6))
    plt.plot(mlp.loss_curve_)
    plt.title('MLP Training Loss Curve')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.grid(True)
    plt.savefig('data/mlp_training_loss.png')
    
if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    train_irrigation_model()
