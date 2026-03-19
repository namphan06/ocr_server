# OCR Service - Tích hợp vào Flutter App

## 📋 Yêu cầu

### Python packages:
```bash
pip install pytesseract pillow opencv-python pdf2image
```

### Cài đặt Tesseract OCR:
- Đã cài tại: `C:\Users\THINKBOOK\AppData\Local\Programs\Tesseract-OCR`
- Đã tải Vietnamese language pack

### Cài đặt Poppler (để đọc PDF):
- Đã tải trong folder: `poppler-25.12.0`

---

## 🚀 Cách sử dụng

### 1. Chạy từ command line:

```bash
# Cơ bản
python ocr_service.py "path/to/file.pdf"

# Với ngôn ngữ tiếng Việt
python ocr_service.py "path/to/file.pdf" --lang vie

# Xuất kết quả ra file JSON
python ocr_service.py "path/to/file.pdf" --output result.json

# Hiển thị đẹp
python ocr_service.py "path/to/file.pdf" --pretty
```

### 2. Kết quả JSON:

```json
{
  "success": true,
  "full_text": "toàn bộ text...",
  "lines": ["dòng 1", "dòng 2", ...],
  "emails": ["email@example.com"],
  "phones": ["0969294861"],
  "links": ["https://github.com/..."],
  "key_value_pairs": {...},
  "file_path": "...",
  "file_name": "...",
  "file_type": "pdf",
  "language": "eng"
}
```

---

## 🔗 Tích hợp vào Flutter App

### Cách 1: Gọi trực tiếp Python script

**Trong Flutter (Dart):**
```dart
import 'dart:convert';
import 'dart:io';

Future<Map<String, dynamic>> extractTextFromFile(String filePath) async {
  // Gọi Python script
  final result = await Process.run(
    'python',
    [
      'ocr_service.py',
      filePath,
      '--lang', 'eng',
      '--pretty',
    ],
    workingDirectory: 'C:/Namphan/TEST/TEST-ĐATN/TS1',
  );
  
  if (result.exitCode == 0) {
    return jsonDecode(result.stdout as String);
  } else {
    throw Exception('OCR failed: ${result.stderr}');
  }
}

// Sử dụng
void processCV() async {
  try {
    final ocrResult = await extractTextFromFile('path/to/cv.pdf');
    
    if (ocrResult['success'] == true) {
      print('Text: ${ocrResult['full_text']}');
      print('Emails: ${ocrResult['emails']}');
      print('Phones: ${ocrResult['phones']}');
      print('Links: ${ocrResult['links']}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
```

### Cách 2: Chạy như local API server (khuyến nghị)

**Tạo file `ocr_server.py`:**
```python
from flask import Flask, request, jsonify
from ocr_service import process_file
import tempfile
import os

app = Flask(__name__)

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    language = request.form.get('lang', 'eng')
    
    # Lưu file tạm
    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(temp_path)
    
    # Xử lý OCR
    result = process_file(temp_path, language)
    
    # Xóa file tạm
    os.remove(temp_path)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
```

**Trong Flutter:**
```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> uploadAndExtract(File file) async {
  var uri = Uri.parse('http://localhost:5000/api/ocr');
  var request = http.MultipartRequest('POST', uri);
  
  request.files.add(await http.MultipartFile.fromPath('file', file.path));
  request.fields['lang'] = 'eng';
  
  var response = await request.send();
  var responseData = await response.stream.bytesToString();
  
  return jsonDecode(responseData);
}
```

---

## 📦 Các hàm API có thể gọi

### Từ Python:
```python
from ocr_service import process_file, extract_structured_data

# Xử lý file bất kỳ
result = process_file('cv.pdf', language='eng')

# Chỉ trích xuất dữ liệu có cấu trúc
data = extract_structured_data('cv.pdf', language='eng')
```

### Từ Flutter:
```dart
// Gọi qua Process.run (cách 1)
// Hoặc gọi qua HTTP API (cách 2)
```

---

## 📁 Cấu trúc folder dự án:

```
C:\Namphan\TEST\TEST-ĐATN\TS1\
├── ocr_service.py          # API chính
├── ocr_server.py           # Local server (optional)
├── poppler-25.12.0/        # Poppler để đọc PDF
├── tesseract-ocr/          # Tesseract OCR
└── flutter_app/            # Flutter project
    └── lib/
        └── services/
            └── ocr_service.dart  # Flutter service
```

---

## ⚡ Tối ưu performance:

1. **Giảm DPI** khi convert PDF (hiện tại 200 DPI)
2. **Giảm scale** khi preprocess (hiện tại 2x)
3. **Cache kết quả** để không OCR lại cùng file
4. **Chạy background** trong Flutter để không block UI

---

## 🐛 Xử lý lỗi:

```dart
try {
  final result = await extractTextFromFile(file.path);
  
  if (result['success'] == false) {
    print('OCR Error: ${result['error']}');
  }
} catch (e) {
  print('Exception: $e');
}
```

---

## ✅ Test nhanh:

```bash
# Test với file CV
python ocr_service.py "Phan Vũ Hoài Nam - CV.pdf" --lang eng --pretty

# Test với tiếng Việt
python ocr_service.py "Phan Vũ Hoài Nam - CV.pdf" --lang vie --output result.json
```
