import pandas as pd
import os

def preprocess_soil_datasets():
    print("Starting Sensor Data Preprocessing...")
    
    # 1. Danh sách các file cần gộp (bỏ file trùng lặp plant_vase1(2).CSV)
    files = ['data/plant_vase1.CSV', 'data/plant_vase2.CSV']
    
    df_list = []
    for f in files:
        if os.path.exists(f):
            print(f"Đang đọc: {f}")
            df = pd.read_csv(f)
            df_list.append(df)
        else:
            print(f"Cảnh báo: Không tìm thấy file {f}")

    if not df_list:
        print("Lỗi: Không có dữ liệu để xử lý.")
        return

    # 2. Gộp dữ liệu
    full_df = pd.concat(df_list, ignore_index=True)
    
    # 3. Tính toán Soil Moisture trung bình
    # Có 5 cảm biến: moisture0 -> moisture4
    moisture_cols = ['moisture0', 'moisture1', 'moisture2', 'moisture3', 'moisture4']
    full_df['soil_moisture_avg'] = full_df[moisture_cols].mean(axis=1)
    
    # 4. Sửa lỗi chính tả cột 'irrgation' -> 'irrigation'
    if 'irrgation' in full_df.columns:
        full_df.rename(columns={'irrgation': 'irrigation'}, inplace=True)
        # Chuyển đổi True/False thành 1/0 để dễ huấn luyện AI
        full_df['irrigation'] = full_df['irrigation'].apply(lambda x: 1 if str(x).lower() == 'true' else 0)
    
    # 5. Tạo cột Timestamp chuẩn (YYYY-MM-DD HH:MM:SS)
    # Convert columns to integers to avoid issues with datetime conversion
    time_cols = ['year', 'month', 'day', 'hour', 'minute', 'second']
    for col in time_cols:
        full_df[col] = full_df[col].astype(int)
        
    full_df['timestamp'] = pd.to_datetime(full_df[time_cols])
    
    # 6. Loại bỏ các dòng trùng lặp (nếu có sau khi gộp)
    full_df = full_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
    
    # 7. Lưu kết quả
    output_path = 'data/consolidated_soil_moisture.csv'
    full_df.to_csv(output_path, index=False)
    
    print(f"Success! Created: {output_path}")
    print(f"Total records: {len(full_df)}")
    print(f"Time range: {full_df['timestamp'].min()} to {full_df['timestamp'].max()}")

if __name__ == "__main__":
    import sys
    # Reconfigure stdout to support utf-8 if possible
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    preprocess_soil_datasets()
