from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__, static_folder='dashboard', template_folder='dashboard')

# Đường dẫn tới file kết quả AI
RESULTS_FILE = 'fuzzy_irrigation_results.csv'

@app.route('/')
def index():
    """Hiển thị trang chủ dashboard"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API trả về dữ liệu thực tế từ hệ chuyên gia mờ"""
    if not os.path.exists(RESULTS_FILE):
        return jsonify({"error": "Results file not found"}), 404
    
    # Đọc dữ liệu từ CSV
    df = pd.read_csv(RESULTS_FILE)
    
    # Lấy 30 dòng gần nhất để hiển thị biểu đồ
    latest_data = df.tail(30).to_dict(orient='records')
    
    # Lấy thông số hiện tại (dòng cuối cùng)
    current = df.iloc[-1].to_dict()
    
    return jsonify({
        "current": current,
        "history": latest_data
    })

@app.route('/<path:path>')
def send_static(path):
    """Phục vụ các file tĩnh như css, js"""
    return send_from_directory('dashboard', path)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("SMART IRRIGATION SERVER IS STARTING...")
    print(f"Mở trình duyệt và truy cập: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=True)
