"""
OCR Server - REST API cho Flutter App
Chạy như local service hoặc deploy lên server
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ocr_service import process_file
import tempfile
import os
import uuid

app = Flask(__name__)
CORS(app)  # Cho phép Flutter gọi API

# Thư mục lưu trữ kết quả
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
RESULT_FOLDER = os.path.join(os.path.dirname(__file__), 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """
    API nhận file từ Flutter, xử lý OCR và trả kết quả JSON
    
    Request:
        - file: File ảnh hoặc PDF
        - lang: Ngôn ngữ (eng/vie), mặc định là eng
    
    Response:
        - success: true/false
        - full_text: Toàn bộ text
        - lines: Danh sách dòng
        - emails: Danh sách email tìm thấy
        - phones: Danh sách số điện thoại
        - links: Danh sách link
        - key_value_pairs: Các cặp key-value
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    language = request.form.get('lang', 'eng')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Tạo tên file duy nhất
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_filename = f"{file_id}{ext}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    
    # Lưu file
    file.save(temp_path)
    
    try:
        # Xử lý OCR
        result = process_file(temp_path, language)
        
        # Lưu kết quả (optional)
        result_path = os.path.join(RESULT_FOLDER, f"{file_id}.json")
        import json
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Xóa file tạm
        os.remove(temp_path)
        
        return jsonify(result)
    
    except Exception as e:
        # Xóa file tạm nếu có lỗi
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Kiểm tra server đang chạy"""
    return jsonify({'status': 'ok', 'message': 'OCR Server is running'})


@app.route('/api/batch', methods=['POST'])
def batch_ocr():
    """
    Xử lý nhiều file cùng lúc
    Request: multiple files
    Response: array of results
    """
    files = request.files.getlist('files')
    language = request.form.get('lang', 'eng')
    
    results = []
    
    for file in files:
        if file and file.filename:
            file_id = str(uuid.uuid4())
            ext = os.path.splitext(file.filename)[1]
            temp_path = os.path.join(UPLOAD_FOLDER, f"{file_id}{ext}")
            
            file.save(temp_path)
            
            try:
                result = process_file(temp_path, language)
                result['file_name'] = file.filename
                results.append(result)
                os.remove(temp_path)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'file_name': file.filename
                })
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    return jsonify({'results': results})


if __name__ == '__main__':
    print("="*50)
    print("OCR SERVER")
    print("="*50)
    print("Starting server...")
    print("API endpoint: http://localhost:5000/api/ocr")
    print("Health check: http://localhost:5000/api/health")
    print("="*50)
    
    # Production: host='0.0.0.0' để nghe từ mọi network interface
    # Development: host='localhost' chỉ nghe từ máy local
    app.run(
        host='0.0.0.0',  # Đổi thành 'localhost' cho development
        port=5000,
        debug=True,
        threaded=True
    )
