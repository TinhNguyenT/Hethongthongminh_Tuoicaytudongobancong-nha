import joblib
import sys

def extract_brain():
    print("\n" + "="*60)
    print("      CÔNG CỤ GIẢI PHẪU BỘ N\u00c3O AI (EXPLAINABLE AI)         ")
    print("="*60)
    
    try:
        mlp = joblib.load('models/mlp_irrigation_model.pkl')
    except Exception as e:
        print(f"Lỗi: {e}")
        return

    print("1. BẰNG CHỨNG CẤU TRÚC (Không có if-else):")
    print("   Mô hình không lưu bất kỳ dòng code logic nào.")
    print(f"   Thay vào đó, hàm kích hoạt là: '{mlp.activation.upper()}' và tối ưu bằng '{mlp.solver.upper()}'.")
    print(f"   Số lần nhẩm bài (Iterations) để học thuộc quy luật: {mlp.n_iter_} lần.")
    print("-"*60)
    
    print("2. BẰNG CHỨNG MA TRẬN TRỌNG SỐ (WEIGHTS):")
    print("   Dưới đây là kích thước các ma trận toán học bên trong bộ não:")
    
    total_connections = 0
    for i, matrix in enumerate(mlp.coefs_):
        neurons_in, neurons_out = matrix.shape
        connections = neurons_in * neurons_out
        total_connections += connections
        if i == 0:
            print(f"   - Lớp Học (Input -> Hidden 1): 4 yếu tố môi trường kết nối tới {neurons_out} Nơ-ron = {connections} phép nhân.")
        elif i == len(mlp.coefs_) - 1:
            print(f"   - Lớp Ra Quyết Định (Hidden -> Output): {neurons_in} Nơ-ron chốt hạ ra 1 Quyết định = {connections} phép nhân.")
        else:
            print(f"   - Lớp Ẩn (Hidden {i} -> Hidden {i+1}): {neurons_in} kết nối {neurons_out} Nơ-ron = {connections} phép nhân.")

    print(f"\n   >>> TỔNG CỘNG: AI cần thực hiện {total_connections} phép tính nhân ma trận cộng dồn ")
    print("       CHỈ ĐỂ đưa ra 1 quyết định Bật hoặc Tắt. (If-else không thể làm được việc này).")
    print("-"*60)

    print("3. TRÍCH XUẤT MỘT PHẦN 'KÝ ỨC' CỦA AI:")
    print("   Thử nhìn vào cách AI đánh giá 'Nhiệt độ' ở 5 Nơ-ron đầu tiên (Lớp 1):")
    # Lấy hàng đầu tiên của ma trận đầu tiên (ứng với Input 0: temp)
    temp_weights = mlp.coefs_[0][0][:5] 
    print("   Trọng số w:")
    for w in temp_weights:
        print(f"   [ {w:10.6f} ]")
    print("   (Các con số âm/dương này là cách máy tính 'cảm nhận' sự nóng lên của thời tiết).")
    
    print("\n" + "="*60)
    print("GỢI Ý CHO HỘI ĐỒNG:")
    print(" Thầy/Cô ạ, bản chất của AI này là một hàm toán học phức tạp f(x) = ReLU(W*x + b).")
    print(" Độ tự tin 100% không phải là học thuộc lòng, mà vì dữ liệu đào tạo (Logic mờ)")
    print(" là một hàm toán học hoàn hảo không có nhiễu ngẫu nhiên.")
    print("="*60)

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    extract_brain()
