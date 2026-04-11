import pandas as pd
import matplotlib.pyplot as plt
from core.fuzzy_logic import FuzzyIrrigationController
from core.mlp_network import MLPPredictor
# from core.cnn_scanner import CNNPlantScanner
import os

def run_hybrid_ai_simulation(dataset_path='data/vietnam_smart_irrigation_dataset.csv'):
    """
    Script điều phối chính: Kết hợp Fuzzy + MLP + CNN skeleton
    """
    if not os.path.exists(dataset_path):
        print(f"Lỗi: Không tìm thấy dữ liệu tại {dataset_path}. Vui lòng chạy scripts/fetch_data.py")
        return

    # 1. Khởi tạo các bộ não AI
    print("Đang khởi tạo các mô-đun AI...")
    mlp = MLPPredictor(model_path='models/mlp_model.pkl', scaler_path='models/scaler.pkl')
    fuzzy = FuzzyIrrigationController()
    # cnn = CNNPlantScanner() # Phase 3 skeleton (Tạm tắt)

    # 2. Đọc dữ liệu
    df = pd.read_csv(dataset_path)
    print(f"Bắt đầu mô phỏng tích hợp trên {len(df)} ngày dữ liệu...")

    mlp_preds = []
    final_decisions = []
    
    for index, row in df.iterrows():
        # Bước A: MLP dự báo mưa
        rain_prediction = mlp.predict_rain(row['Temp_C'], row['Humidity_pct'])
        mlp_preds.append(rain_prediction)

        # Bước B: CNN quét cây (Tạm tắt)
        plant_health = 0 

        # Bước C: Fuzzy ra quyết định cuối cùng
        decision = fuzzy.decide(
            moisture_val=row['Soil_Moisture_pct'], 
            temp_val=row['Temp_C'], 
            predicted_rain_mm=rain_prediction
        )
        
        # Logic tích hợp thêm từ CNN: Nếu cây héo (1), tăng thời gian tưới
        if plant_health == 1:
            decision = max(decision, 25.0) # Ưu tiên cứu cây héo
            
        final_decisions.append(decision)

    # 3. Lưu kết quả vào thư mục data/
    df['MLP_Predicted_Rain'] = mlp_preds
    df['Hybrid_Decision_min'] = final_decisions
    
    output_path = 'data/hybrid_irrigation_results.csv'
    df.to_csv(output_path, index=False)
    print(f"THÀNH CÔNG: Kết quả tích hợp đã lưu tại {output_path}")

    # 4. Trực quan hóa
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'][:30], df['Soil_Moisture_pct'][:30], label='Soil Moisture (%)', color='green')
    plt.bar(df['Date'][:30], df['Hybrid_Decision_min'][:30], label='AI Decision (min)', color='purple', alpha=0.5)
    plt.title('Hybrid AI Simulation (Fuzzy + MLP + CNN Skeleton)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('data/hybrid_simulation_plot.png')
    print("Đã lưu biểu đồ kết quả: data/hybrid_simulation_plot.png")

if __name__ == "__main__":
    run_hybrid_ai_simulation()
