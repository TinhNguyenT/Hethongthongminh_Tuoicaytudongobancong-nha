import joblib
import pandas as pd
import sys
import os

def run_batch_test():
    print("="*60)
    print(" CHẠY BÀI TEST 100 KỊCH BẢN ĐỂ KIỂM CHỨNG ĐỘ CHÍNH XÁC ")
    print("="*60)

    # 1. Load Model
    model_path = 'models/mlp_irrigation_model.pkl'
    scaler_path = 'models/irrigation_scaler.pkl'
    
    if not os.path.exists(model_path):
        print("Lỗi: Không tìm thấy file model.")
        return
        
    mlp = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Dữ liệu Test do người dùng đưa vào
    raw_test_data = """
1.  35, 40, 0, 0.05 -> BẬT
2.  38, 50, 0, 0.05 -> BẬT
3.  30, 60, 0, 0.10 -> BẬT
4.  28, 55, 0, 0.08 -> BẬT
5.  40, 30, 0, 0.05 -> BẬT
6.  33, 45, 1, 0.10 -> BẬT
7.  36, 50, 0, 0.12 -> BẬT
8.  32, 70, 0, 0.10 -> BẬT
9.  29, 65, 0, 0.15 -> BẬT
10. 37, 40, 0, 0.05 -> BẬT
11. 34, 50, 2, 0.10 -> BẬT
12. 31, 60, 0, 0.12 -> BẬT
13. 39, 35, 0, 0.08 -> BẬT
14. 33, 55, 0, 0.10 -> BẬT
15. 36, 45, 0, 0.07 -> BẬT
16. 35, 60, 0, 0.10 -> BẬT
17. 30, 50, 0, 0.12 -> BẬT
18. 38, 42, 0, 0.05 -> BẬT
19. 32, 48, 0, 0.10 -> BẬT
20. 34, 52, 0, 0.08 -> BẬT
21. 30, 50, 0, 0.30 -> BẬT
22. 30, 50, 5, 0.30 -> TẮT
23. 28, 60, 0, 0.35 -> BẬT
24. 28, 60, 10, 0.35 -> TẮT
25. 32, 55, 0, 0.40 -> BẬT
26. 32, 55, 15, 0.40 -> TẮT
27. 35, 45, 0, 0.30 -> BẬT
28. 35, 45, 20, 0.30 -> TẮT
29. 33, 50, 0, 0.45 -> BẬT
30. 33, 50, 8, 0.45 -> TẮT
31. 29, 65, 0, 0.35 -> BẬT
32. 29, 65, 12, 0.35 -> TẮT
33. 31, 55, 0, 0.40 -> BẬT
34. 31, 55, 7, 0.40 -> TẮT
35. 34, 50, 0, 0.38 -> BẬT
36. 34, 50, 9, 0.38 -> TẮT
37. 30, 60, 0, 0.42 -> BẬT
38. 30, 60, 6, 0.42 -> TẮT
39. 32, 58, 0, 0.37 -> BẬT
40. 32, 58, 11, 0.37 -> TẮT
51. 30, 50, 0, 0.60 -> TẮT
52. 35, 40, 0, 0.65 -> TẮT
53. 28, 60, 0, 0.70 -> TẮT
54. 32, 55, 0, 0.75 -> TẮT
55. 33, 50, 0, 0.80 -> TẮT
56. 31, 65, 0, 0.68 -> TẮT
57. 34, 45, 0, 0.72 -> TẮT
58. 29, 70, 0, 0.66 -> TẮT
59. 36, 40, 0, 0.78 -> TẮT
60. 30, 60, 0, 0.74 -> TẮT
61. 33, 55, 5, 0.65 -> TẮT
62. 32, 50, 10, 0.70 -> TẮT
63. 35, 45, 3, 0.75 -> TẮT
64. 31, 60, 8, 0.68 -> TẮT
65. 34, 50, 12, 0.72 -> TẮT
66. 30, 55, 7, 0.66 -> TẮT
67. 33, 52, 9, 0.78 -> TẮT
68. 29, 65, 4, 0.74 -> TẮT
69. 36, 40, 6, 0.80 -> TẮT
70. 31, 60, 10, 0.70 -> TẮT
81.  25, 90, 0, 0.20 -> BẬT
82.  40, 20, 0, 0.20 -> BẬT
83.  30, 50, 50, 0.20 -> TẮT
84.  35, 40, 100, 0.10 -> TẮT
85.  20, 80, 0, 0.25 -> BẬT
86.  20, 80, 20, 0.25 -> TẮT
87.  45, 30, 0, 0.50 -> TẮT
88.  10, 90, 0, 0.50 -> TẮT
89.  38, 50, 0, 0.49 -> BẬT
90.  38, 50, 0, 0.51 -> TẮT
91.  30, 50, 1, 0.48 -> BẬT
92.  30, 50, 3, 0.48 -> TẮT
93.  33, 55, 0, 0.49 -> BẬT
94.  33, 55, 0, 0.51 -> TẮT
95.  35, 60, 2, 0.45 -> BẬT
96.  35, 60, 6, 0.45 -> TẮT
97.  32, 50, 0, 0.50 -> BẬT
98.  32, 50, 5, 0.50 -> TẮT
99.  28, 65, 0, 0.20 -> BẬT
100. 28, 65, 15, 0.20 -> TẮT
"""
    
    # 2. Xử lý chuỗi
    lines = raw_test_data.strip().replace('→', '->').split('\n')
    
    correct_count = 0
    total_count = len(lines)
    
    print(f"{'Tình huống':<15} | {'Nhiệt / Ẩm / Mưa / Đất':<25} | {'Kỳ Vọng':<15} | {'Mạng MLP':<15} | {'Đánh Giá':<10}")
    print("-" * 95)
    
    for line in lines:
        if not line.strip(): continue
        try:
            parts = line.split("->")
            left_side = parts[0].strip()
            # Bỏ đi các comment dính kèm ở cuối, ví dụ "BẬT (vội vàng)" -> Lấy chữ "BẬT"
            expected_str = parts[1].split()[0].strip().replace('borderline', 'BẬT') 
            
            # Xử lý left_side e.g., "1.  35, 40, 0, 0.05"
            id_str, params = left_side.split(".", 1)
            temp, humid, rain, soil = [float(x.strip()) for x in params.strip().split(',')]
            
            # Label thực sự từ danh sách
            expected = 1 if 'BẬT' in expected_str else 0
            
            # 3. Mạng Neural Network DỰ ĐOÁN
            input_df = pd.DataFrame([[temp, humid, rain, soil]], columns=['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture'])
            input_scaled = scaler.transform(input_df)
            mlp_pred = mlp.predict(input_scaled)[0]
            
            # Logic Đánh giá
            if mlp_pred == expected:
                correct_count += 1
                eval_str = "✅ Trùng khớp"
            else:
                eval_str = "❌ Lệch"
            
            expected_disp = "BẬT MÁY BƠM" if expected == 1 else "TẮT MÁY BƠM"
            mlp_disp = "BẬT MÁY BƠM" if mlp_pred == 1 else "TẮT MÁY BƠM"
            params_disp = f"{temp:.0f}°C, {humid:.0f}%, {rain:.0f}mm, {soil:.2f}"
            
            print(f"Case {id_str.strip():<9} | {params_disp:<25} | {expected_disp:<15} | {mlp_disp:<15} | {eval_str:<10}")
            
        except Exception as e:
            print(f"Lỗi cú pháp tại dòng: {line} - {e}")
            
    print("=" * 95)
    
    # Tính Accuracy phần trăm như bạn yêu cầu
    accuracy = (correct_count / total_count) * 100
    
    print(f"✅ TỔNG KẾT ĐÁNH GIÁ MÔ HÌNH MLP:")
    print(f"Tổng số Tester đưa ra   : {total_count} kịch bản")
    print(f"Dự đoán trúng phóc      : {correct_count} kịch bản")
    print(f"ACCURACY (Độ chính xác) : {accuracy:.2f}%")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    run_batch_test()
