# 🚀 Production OCR Solution cho Flutter App

## ❌ Vấn đề với đường dẫn cứng

Đường dẫn này **chỉ chạy được trên máy development**:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\THINKBOOK\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
```

Khi build APK và chạy trên điện thoại thật sẽ **KHÔNG hoạt động** vì:
1. Điện thoại không có Tesseract OCR
2. Đường dẫn Windows không tồn tại trên Android/iOS
3. Python không chạy native trên mobile

---

## ✅ 3 Giải pháp Production

### **Giải pháp 1: Cloud OCR API (KHUYẾN NGHỊ)**

**Kiến trúc:**
```
Flutter App → HTTP Request → Cloud Server (Python + Tesseract) → JSON Response
```

**Ưu điểm:**
- ✅ Chạy được trên mọi thiết bị (Android, iOS, Web)
- ✅ Không cần cài Tesseract trên mobile
- ✅ Dễ maintain và update
- ✅ Xử lý nhanh, mạnh hơn

**Cách làm:**

1. **Deploy Python OCR Server lên cloud:**
   - Google Cloud Run
   - AWS Lambda
   - Heroku
   - Render.com (free tier)

2. **Flutter gọi API:**
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class CloudOcrService {
  static const String apiUrl = 'https://your-ocr-api.com/api/ocr';
  
  static Future<Map<String, dynamic>> extractText(File file) async {
    var uri = Uri.parse(apiUrl);
    var request = http.MultipartRequest('POST', uri);
    
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    request.fields['lang'] = 'eng';
    
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    
    return jsonDecode(responseData);
  }
}
```

3. **Deploy server:**
```bash
# Deploy lên Render.com (free)
# Tạo file requirements.txt
echo "flask
flask-cors
pytesseract
pillow
opencv-python
pdf2image" > requirements.txt

# Push lên GitHub, connect với Render
```

---

### **Giải pháp 2: Bundle Tesseract trong App (chỉ Android)**

Sử dụng package `tesseract_ocr` hoặc `google_mlkit_text_recognition`:

```dart
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

class MlKitOcrService {
  static final TextRecognizer _textRecognizer = TextRecognizer();
  
  static Future<String> extractText(File imageFile) async {
    final inputImage = InputImage.fromFile(imageFile);
    final recognizedText = await _textRecognizer.processImage(inputImage);
    
    return recognizedText.text;
  }
  
  static void dispose() {
    _textRecognizer.close();
  }
}
```

**Ưu điểm:**
- ✅ Chạy offline
- ✅ Không cần server
- ✅ Nhanh, không độ trễ network

**Nhược điểm:**
- ❌ Chỉ nhận ảnh, không đọc được PDF trực tiếp
- ❌ Cần convert PDF → ảnh trước
- ❌ Accuracy thấp hơn Tesseract

---

### **Giải pháp 3: Hybrid (Tốt nhất cho production)**

Kết hợp cả 2:
- **Online**: Gọi Cloud OCR API cho kết quả chính xác nhất
- **Offline**: Dùng ML Kit cho trường hợp không có mạng

```dart
class HybridOcrService {
  static const String cloudApiUrl = 'https://your-api.com/ocr';
  final TextRecognizer _mlKitRecognizer = TextRecognizer();
  
  Future<Map<String, dynamic>> extractText(
    File file, {
    bool preferOnline = true,
  }) async {
    if (preferOnline && await _isOnline()) {
      // Thử gọi cloud API trước
      try {
        return await CloudOcrService.extractText(file);
      } catch (e) {
        // Fallback về ML Kit
        return await _extractWithMlKit(file);
      }
    } else {
      // Offline mode
      return await _extractWithMlKit(file);
    }
  }
  
  Future<Map<String, dynamic>> _extractWithMlKit(File file) async {
    final inputImage = InputImage.fromFile(file);
    final recognizedText = await _mlKitRecognizer.processImage(inputImage);
    
    return {
      'success': true,
      'full_text': recognizedText.text,
      'lines': recognizedText.lines.map((l) => l.text).toList(),
      'emails': _extractEmails(recognizedText.text),
      'phones': _extractPhones(recognizedText.text),
    };
  }
  
  Future<bool> _isOnline() async {
    try {
      final result = await InternetAddress.lookup('google.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException {
      return false;
    }
  }
  
  List<String> _extractEmails(String text) {
    // Regex extract emails
    return [];
  }
  
  List<String> _extractPhones(String text) {
    // Regex extract phones
    return [];
  }
}
```

---

## 📦 Flutter Package Dependencies

**pubspec.yaml:**
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # HTTP calling
  http: ^1.1.0
  
  # File handling
  file_picker: ^6.1.1
  path_provider: ^2.1.1
  
  # ML Kit (offline OCR)
  google_mlkit_text_recognition: ^0.11.0
  
  # PDF to image (nếu cần đọc PDF)
  syncfusion_flutter_pdf: ^24.1.41
  flutter_pdfview: ^1.3.2
  
  # Utility
  dio: ^5.4.0
  connectivity_plus: ^5.0.2
```

---

## 🎯 Khuyến nghị cho dự án của bạn

Với CV extraction app, tôi khuyến nghị **Giải pháp 1 (Cloud OCR API)** vì:

1. **PDF support tốt** - Tesseract xử lý PDF tốt hơn ML Kit
2. **Accuracy cao** - Đặc biệt với tiếng Việt
3. **Dễ maintain** - Chỉ cần update 1 chỗ (server)
4. **Nhẹ app** - Không bundle thư viện nặng

---

## 📝 Các bước triển khai

### Bước 1: Deploy OCR Server

```bash
# 1. Tạo requirements.txt
cd C:\Namphan\TEST\TEST-ĐATN\TS1
echo flask > requirements.txt
echo flask-cors >> requirements.txt
echo pytesseract >> requirements.txt
echo pillow >> requirements.txt
echo opencv-python >> requirements.txt
echo pdf2image >> requirements.txt

# 2. Push lên GitHub
git init
git add .
git commit -m "OCR Server"
git push origin main

# 3. Deploy lên Render.com
# - Tạo account tại https://render.com
# - New Web Service
# - Connect GitHub repo
# - Build command: pip install -r requirements.txt
# - Start command: python ocr_server.py
```

### Bước 2: Tích hợp vào Flutter

```dart
// lib/services/ocr_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class OcrService {
  // Đổi thành URL server thật khi deploy
  static const String apiUrl = 'http://localhost:5000/api/ocr';
  
  static Future<Map<String, dynamic>> extractFromPdf(File pdfFile) async {
    var uri = Uri.parse(apiUrl);
    var request = http.MultipartRequest('POST', uri);
    
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      pdfFile.path,
    ));
    request.fields['lang'] = 'eng'; // hoặc 'vie'
    
    var response = await request.send();
    
    if (response.statusCode == 200) {
      var responseData = await response.stream.bytesToString();
      return jsonDecode(responseData);
    } else {
      throw Exception('OCR failed: ${response.statusCode}');
    }
  }
}
```

### Bước 3: Sử dụng trong App

```dart
// lib/screens/cv_upload_screen.dart
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../services/ocr_service.dart';

class CvUploadScreen extends StatefulWidget {
  @override
  State<CvUploadScreen> createState() => _CvUploadScreenState();
}

class _CvUploadScreenState extends State<CvUploadScreen> {
  bool _isLoading = false;
  Map<String, dynamic>? _ocrResult;
  
  Future<void> _pickAndProcessCV() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'png', 'jpg', 'jpeg'],
    );
    
    if (result == null) return;
    
    setState(() => _isLoading = true);
    
    try {
      final file = File(result.files.single.path!);
      final ocrResult = await OcrService.extractFromPdf(file);
      
      setState(() {
        _ocrResult = ocrResult;
        _isLoading = false;
      });
      
      // Xử lý kết quả
      if (ocrResult['success'] == true) {
        print('Name: ${_extractName(ocrResult)}');
        print('Email: ${ocrResult['emails']}');
        print('Phone: ${ocrResult['phones']}');
      }
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
  
  String _extractName(Map<String, dynamic> result) {
    // Logic trích xuất tên từ first line
    return result['lines']?.first ?? 'Unknown';
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload CV')),
      body: Column(
        children: [
          ElevatedButton(
            onPressed: _pickAndProcessCV,
            child: Text('Chọn file CV'),
          ),
          if (_isLoading)
            CircularProgressIndicator()
          else if (_ocrResult != null)
            Expanded(
              child: Text(_ocrResult!['full_text']),
            ),
        ],
      ),
    );
  }
}
```

---

## 🔧 Testing

### Test local server:
```bash
# Terminal 1: Chạy server
cd C:\Namphan\TEST\TEST-ĐATN\TS1
python ocr_server.py

# Terminal 2: Test API
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@Phan Vũ Hoài Nam - CV.pdf" \
  -F "lang=eng"
```

### Test Flutter app:
```bash
# Chạy app với local server
flutter run

# Build release APK
flutter build apk --release
```

---

## 📊 So sánh các giải pháp

| Tiêu chí | Cloud API | ML Kit | Hybrid |
|----------|-----------|--------|--------|
| Accuracy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐ (network) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Offline | ❌ | ✅ | ✅ |
| PDF support | ✅ | ❌ | ✅ |
| Setup complexity | Trung bình | Dễ | Phức tạp |
| Production ready | ✅ | ✅ | ✅✅✅ |

---

## 🎯 Kết luận

**Khuyến nghị:** Dùng **Cloud OCR API** cho production, vì:
- Accuracy cao nhất (đặc biệt với CV có nhiều định dạng)
- Xử lý được PDF tốt
- Dễ maintain và scale
- Flutter app nhẹ, không bundle thư viện nặng

**Code đã sẵn sàng để deploy!**
