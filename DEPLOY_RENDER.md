# 🚀 Hướng dẫn Deploy OCR Server lên Render.com

## ✅ Files đã tạo:

```
C:\Namphan\TEST\TEST-ĐATN\TS1\
├── requirements.txt    # Python dependencies
├── Procfile           # Render config
├── .gitignore         # Git ignore rules
├── ocr_server.py      # Flask server
└── ocr_service.py     # OCR logic
```

---

## 📋 Bước 1: Push code lên GitHub

### 1.1. Tạo repository mới trên GitHub

```
1. Vào https://github.com
2. Click "+" → "New repository"
3. Đặt tên: "ocr-server" (hoặc tên khác)
4. Chọn "Public" hoặc "Private"
5. Click "Create repository"
```

### 1.2. Push code từ local lên GitHub

Mở PowerShell trong folder dự án:

```powershell
cd C:\Namphan\TEST\TEST-ĐATN\TS1

# Khởi tạo git (nếu chưa có)
git init

# Thêm tất cả files
git add .

# Commit
git commit -m "OCR Server ready for deployment"

# Thêm remote repository (thay <your-username> và <repo-name>)
git remote add origin https://github.com/<your-username>/<repo-name>.git

# Push lên GitHub
git push -u origin main
```

**Nếu bị lỗi branch main/master:**

```powershell
# Đổi branch thành main
git branch -M main

# Push lại
git push -u origin main
```

---

## 📋 Bước 2: Deploy lên Render.com

### 2.1. Tạo tài khoản Render

```
1. Vào https://render.com
2. Click "Get Started for Free"
3. Sign up với GitHub account (khuyến nghị) hoặc email
```

### 2.2. Tạo Web Service

```
1. Dashboard → Click "New +" → "Web Service"
2. "Connect a repository"
3. Chọn repository bạn vừa push
4. Render sẽ tự động detect Python project
```

### 2.3. Cấu hình Web Service

**Fill các thông tin:**

| Field | Giá trị |
|-------|---------|
| **Name** | `ocr-server` (hoặc tên bạn muốn) |
| **Region** | Singapore (gần VN nhất) |
| **Branch** | `main` |
| **Root Directory** | Để trống |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python ocr_server.py` |
| **Instance Type** | `Free` |

**Click "Advanced" và thêm Environment Variables:**

```
PYTHON_VERSION=3.9.0
```

### 2.4. Deploy

```
1. Click "Create Web Service"
2. Đợi 5-10 phút để build và deploy
3. Khi thấy "Your service is live" là thành công!
```

---

## 📋 Bước 3: Lấy API URL

Sau khi deploy xong, bạn sẽ có URL dạng:

```
https://ocr-server-abc123.onrender.com
```

**Test API:**

```
1. Vào: https://<your-url>.onrender.com/api/health
2. Nếu thấy: {"status": "ok", "message": "OCR Server is running"}
3. ✅ Thành công!
```

**Test OCR endpoint:**

```bash
# Dùng PowerShell
curl -X POST https://<your-url>.onrender.com/api/ocr `
  -F "file=@Phan Vũ Hoài Nam - CV.pdf" `
  -F "lang=eng"
```

---

## 📋 Bước 4: Tích hợp vào Flutter App

### 4.1. Cập nhật API URL trong Flutter

```dart
// lib/services/ocr_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class OcrService {
  // Thay bằng URL thật của bạn
  static const String apiUrl = 'https://ocr-server-abc123.onrender.com/api/ocr';
  
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
  
  static Future<Map<String, dynamic>> extractFromImage(File imageFile) async {
    return await extractFromPdf(imageFile); // Same API
  }
}
```

### 4.2. Sử dụng trong Flutter UI

```dart
// lib/screens/cv_upload_screen.dart
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import '../services/ocr_service.dart';

class CvUploadScreen extends StatefulWidget {
  @override
  State<CvUploadScreen> createState() => _CvUploadScreenState();
}

class _CvUploadScreenState extends State<CvUploadScreen> {
  bool _isLoading = false;
  String _resultText = '';
  
  Future<void> _uploadAndProcess() async {
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
        _isLoading = false;
        if (ocrResult['success'] == true) {
          _resultText = ocrResult['full_text'];
        } else {
          _resultText = 'Error: ${ocrResult['error']}';
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _resultText = 'Exception: $e';
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload CV')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            ElevatedButton.icon(
              onPressed: _uploadAndProcess,
              icon: Icon(Icons.upload_file),
              label: Text('Chọn file CV'),
            ),
            SizedBox(height: 20),
            if (_isLoading)
              CircularProgressIndicator()
            else if (_resultText.isNotEmpty)
              Expanded(
                child: SingleChildScrollView(
                  child: Text(_resultText),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📋 Bước 5: Build APK

```bash
# Trong folder Flutter project
flutter build apk --release

# APK sẽ nằm ở: build/app/outputs/flutter-apk/app-release.apk
```

**Test trên device thật:**

1. Cài APK vào điện thoại
2. Mở app, upload CV
3. App sẽ gọi API lên Render server
4. Nhận kết quả và hiển thị

---

## ⚠️ Lưu ý quan trọng

### Render Free Tier có giới hạn:

- **750 hours/month** (đủ cho 1 server chạy 24/7 trong tháng)
- **Spin down** sau 15 phút không có request
- **Cold start** mất 30-50s khi có request đầu tiên

**Giải pháp:**

```dart
// Flutter: Thêm timeout và retry
import 'package:dio/dio.dart';

class OcrService {
  static final Dio _dio = Dio();
  
  static Future<Map<String, dynamic>> extractFromPdf(File file) async {
    try {
      var formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(file.path, filename: 'cv.pdf'),
        'lang': 'eng',
      });
      
      // Tăng timeout
      _dio.options.connectTimeout = Duration(seconds: 60);
      _dio.options.receiveTimeout = Duration(seconds: 60);
      
      var response = await _dio.post(
        'https://your-url.onrender.com/api/ocr',
        data: formData,
      );
      
      return response.data;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout) {
        // Retry nếu bị timeout do cold start
        await Future.delayed(Duration(seconds: 5));
        return await extractFromPdf(file); // Retry
      }
      rethrow;
    }
  }
}
```

---

## 🐛 Debug & Troubleshooting

### Lỗi thường gặp:

**1. Build failed trên Render:**

```
→ Kiểm tra logs trong Render dashboard
→ Đảm bảo requirements.txt đúng format
→ Check Python version compatibility
```

**2. API timeout:**

```
→ Do cold start (Render free tier)
→ Thêm retry logic trong Flutter
→ Hoặc upgrade lên paid tier ($7/month)
```

**3. File not found:**

```
→ Check file path trong Flutter
→ Đảm bảo file tồn tại trước khi upload
```

**4. CORS error:**

```
→ Flask-CORS đã được cài đặt trong ocr_server.py
→ Check logs xem server có start đúng không
```

---

## ✅ Test checklist

Trước khi build APK, test kỹ:

- [ ] Server deploy thành công trên Render
- [ ] GET `/api/health` trả về `{"status": "ok"}`
- [ ] POST `/api/ocr` với file test hoạt động
- [ ] Flutter app gọi API thành công
- [ ] Xử lý loading state
- [ ] Xử lý error state
- [ ] Timeout handling
- [ ] Retry logic

---

## 🎯 Production tips

### Nâng cao performance:

1. **Upgrade Render tier** ($7/month):
   - Không bị spin down
   - Không có cold start
   - Response nhanh hơn

2. **Thêm caching:**
   ```python
   # Lưu kết quả trong Redis
   # Nếu cùng file hash, trả về cache
   ```

3. **Batch processing:**
   ```python
   # Xử lý nhiều file cùng lúc
   POST /api/batch
   ```

4. **Rate limiting:**
   ```python
   # Giới hạn requests per minute
   from flask_limiter import Limiter
   ```

---

## 📞 Hỗ trợ

Nếu gặp khó khăn:

1. Check Render logs: Dashboard → Logs tab
2. Test API bằng Postman/curl trước
3. Check Flutter network permissions:
   ```xml
   <!-- Android: android/app/src/main/AndroidManifest.xml -->
   <uses-permission android:name="android.permission.INTERNET" />
   ```

---

**✅ Done!** Server đã chạy trên Render, Flutter app có thể gọi API!
