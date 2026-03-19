import 'dart:convert';
import 'dart:io';

/// Service gọi Python OCR script để trích xuất text từ ảnh/PDF
class OcrService {
  static const String _pythonScriptPath = 'C:/Namphan/TEST/TEST-ĐATN/TS1/ocr_service.py';
  
  /// Trích xuất text từ file
  /// 
  /// [filePath] - đường dẫn file (ảnh hoặc PDF)
  /// [language] - ngôn ngữ: 'eng' (English) hoặc 'vie' (Vietnamese)
  /// 
  /// Returns: Map chứa kết quả OCR
  static Future<Map<String, dynamic>> extractText({
    required String filePath,
    String language = 'eng',
  }) async {
    try {
      // Kiểm tra file tồn tại
      if (!await File(filePath).exists()) {
        return {
          'success': false,
          'error': 'File not found: $filePath',
        };
      }
      
      // Gọi Python script
      final result = await Process.run(
        'python',
        [
          _pythonScriptPath,
          filePath,
          '--lang', language,
        ],
      );
      
      if (result.exitCode == 0) {
        return jsonDecode(result.stdout as String);
      } else {
        return {
          'success': false,
          'error': result.stderr,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Trích xuất và lưu kết quả ra file JSON
  static Future<Map<String, dynamic>> extractAndSave({
    required String filePath,
    required String outputJsonPath,
    String language = 'eng',
  }) async {
    try {
      final result = await Process.run(
        'python',
        [
          _pythonScriptPath,
          filePath,
          '--lang', language,
          '--output', outputJsonPath,
        ],
      );
      
      if (result.exitCode == 0) {
        // Đọc file JSON đã lưu
        final jsonFile = File(outputJsonPath);
        final content = await jsonFile.readAsString(encoding: utf8);
        return jsonDecode(content);
      } else {
        return {
          'success': false,
          'error': result.stderr,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Upload file lên server OCR (nếu dùng API server)
  /// Cần chạy: python ocr_server.py trước
  static Future<Map<String, dynamic>> uploadToServer({
    required File file,
    String language = 'eng',
    String serverUrl = 'http://localhost:5000/api/ocr',
  }) async {
    // Implement khi dùng Flask server
    // Xem hướng dẫn trong README_OCR_SERVICE.md
    throw UnimplementedError('Chưa implement');
  }
}

// Ví dụ sử dụng
void main() async {
  // Cách 1: Trích xuất trực tiếp
  final result = await OcrService.extractText(
    filePath: 'C:/Namphan/TEST/TEST-ĐATN/TS1/Phan Vũ Hoài Nam - CV.pdf',
    language: 'eng',
  );
  
  if (result['success'] == true) {
    print('✅ Thành công!');
    print('Full text: ${result['full_text']}');
    print('Emails: ${result['emails']}');
    print('Phones: ${result['phones']}');
    print('Links: ${result['links']}');
    print('Lines: ${result['lines'].length} dòng');
  } else {
    print('❌ Lỗi: ${result['error']}');
  }
  
  // Cách 2: Trích xuất và lưu JSON
  final result2 = await OcrService.extractAndSave(
    filePath: 'cv.pdf',
    outputJsonPath: 'cv_ocr_result.json',
    language: 'eng',
  );
  
  print('Kết quả lưu tại: cv_ocr_result.json');
}
