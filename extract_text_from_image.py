import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from pdf2image import convert_from_path
import os

# Cấu hình đường dẫn Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\THINKBOOK\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Cấu hình đường dẫn Poppler (trong folder dự án)
current_dir = os.path.dirname(os.path.abspath(__file__))
poppler_path = os.path.join(current_dir, 'poppler-25.12.0', 'Library', 'bin')
os.environ['PATH'] = poppler_path + ';' + os.environ['PATH']


def extract_text_from_file(file_path, language='vie', preprocess=True):
    """
    Trích xuất TẤT CẢ text từ file (ảnh hoặc PDF)
    
    Args:
        file_path: đường dẫn file (ảnh hoặc PDF)
        language: ngôn ngữ OCR ('eng', 'vie', 'eng+vie')
        preprocess: có tiền xử lý ảnh không
    
    Returns:
        text: toàn bộ text trích xuất được
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # Xử lý PDF
    if ext == '.pdf':
        return extract_text_from_pdf(file_path, language, preprocess)
    
    # Xử lý ảnh
    try:
        img = Image.open(file_path)
        
        # Tiền xử lý ảnh để tăng độ chính xác
        if preprocess:
            img = preprocess_image(img)
        
        config = '--psm 3 --oem 3'  # PSM 3: tự động phân trang, OEM 3: default engine
        text = pytesseract.image_to_string(img, lang='eng', config=config)
        
        return text.strip()
    
    except FileNotFoundError:
        print(f"Khong tim thay file: {file_path}")
        return None
    except Exception as e:
        print(f"Loi: {str(e)}")
        return None


def extract_text_from_pdf(pdf_path, language='vie', preprocess=True):
    """
    Trích xuất text từ file PDF (chuyển sang ảnh rồi OCR)
    """
    try:
        # Chuyển PDF sang list các trang (ảnh) - DPI 200 để cân bằng tốc độ và chất lượng
        pages = convert_from_path(pdf_path, dpi=200)
        
        all_text = []
        for i, page in enumerate(pages, 1):
            if preprocess:
                page = preprocess_image(page, scale=2)  # Phóng to 2x
            
            # PSM 3: tự động phân trang, OEM 3: default engine
            text = pytesseract.image_to_string(page, lang='eng', config='--psm 3 --oem 3')
            all_text.append(f"=== Trang {i} ===\n{text}")
        
        return '\n\n'.join(all_text).strip()
    
    except Exception as e:
        print(f"Lỗi PDF: {str(e)}")
        return None


def preprocess_image(img, scale=2):
    """
    Tiền xử lý ảnh để cải thiện độ chính xác OCR
    - Phóng to ảnh (scale)
    - Chuyển grayscale
    - Thresholding
    - Khử nhiễu
    """
    img_cv = np.array(img)
    
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_cv
    
    # Phóng to ảnh để cải thiện OCR
    h, w = gray.shape
    gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
    
    # Thresholding với Otsu
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Khử nhiễu
    denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
    
    # Morphology để làm sạch ký tự
    kernel = np.ones((1,1), np.uint8)
    denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
    
    return Image.fromarray(denoised)


def extract_all_text_with_confidence(file_path, language='vie'):
    """
    Trích xuất text kèm độ tin cậy cho từng từ
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            # Xử lý PDF - chỉ trả về text, không có chi tiết confidence
            text = extract_text_from_pdf(file_path, language, preprocess=True)
            if text:
                words = text.split()
                return [{'text': w, 'confidence': 0, 'level': 4, 'line_num': 0, 'word_num': i} 
                        for i, w in enumerate(words)]
            return None
        
        # Xử lý ảnh
        img = Image.open(file_path)
        img = preprocess_image(img)
        
        data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
        
        results = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:
                results.append({
                    'text': data['text'][i].strip(),
                    'confidence': int(data['conf'][i]),
                    'level': data['level'][i],
                    'line_num': data['line_num'][i],
                    'word_num': data['word_num'][i]
                })
        
        return results
    
    except Exception as e:
        print(f"Loi: {str(e)}")
        return None


def extract_key_value_pairs(file_path, language='vie'):
    """
    Tự động phát hiện các cặp key-value từ text trong file
    Nhận diện các trường dựa trên pattern "label: value" hoặc "label = value"
    """
    text = extract_text_from_file(file_path, language)
    
    if not text:
        return None
    
    key_value_pairs = {}
    if not text:
        return {'full_text': '', 'lines': [], 'key_value_pairs': {}}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Pattern 1: "Key: Value"
        match = re.match(r'^([^:=]+):\s*(.+)$', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            key_value_pairs[key] = value
            continue
        
        # Pattern 2: "Key = Value"
        match = re.match(r'^([^=]+)=\s*(.+)$', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            key_value_pairs[key] = value
            continue
        
        # Pattern 3: "Key - Value"
        match = re.match(r'^([^-]+)-\s*(.+)$', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            key_value_pairs[key] = value
    
    return {
        'full_text': text,
        'lines': [l.strip() for l in lines if l.strip()],
        'key_value_pairs': key_value_pairs
    }


def extract_all_fields(file_path, language='vie', detailed=True):
    """
    Trích xuất TẤT CẢ thông tin từ file (ảnh hoặc PDF)
    
    Returns:
        dict chứa:
        - full_text: toàn bộ text
        - lines: danh sách dòng
        - words: danh sách từ (nếu detailed=True)
        - confidence: độ tin cậy trung bình
        - structured_data: các field tự động phát hiện
    """
    result = {
        'full_text': '',
        'lines': [],
        'words': [],
        'average_confidence': 0,
        'structured_data': {}
    }
    
    # Lấy toàn bộ text
    text = extract_text_from_file(file_path, language)
    if text:
        result['full_text'] = text
        result['lines'] = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Lấy chi tiết từng từ với confidence
    if detailed:
        word_data = extract_all_text_with_confidence(file_path, language)
        if word_data:
            result['words'] = word_data
            
            # Tính confidence trung bình
            confidences = [w['confidence'] for w in word_data]
            result['average_confidence'] = sum(confidences) / len(confidences) if confidences else 0
    
    # Phát hiện key-value pairs
    kv_data = extract_key_value_pairs(file_path, language)
    if kv_data:
        result['structured_data'] = kv_data['key_value_pairs']
    
    return result


if __name__ == "__main__":
    import sys
    import os
    
    # Set console encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    
    # Nhận đường dẫn từ command line argument hoặc input
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Nhap duong dan file (anh hoac PDF): ").strip()
    
    if not file_path:
        print("Ban chua nhap duong dan file!")
        exit(1)
    
    if not os.path.isfile(file_path):
        print(f"File khong ton tai: {file_path}")
        exit(1)
    
    # Check file ảnh hoặc PDF
    valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.pdf']
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in valid_extensions:
        print(f"File khong phai anh hoac PDF hop le! Extension: {ext}")
        exit(1)
    
    # Lấy TẤT CẢ text và thông tin
    result = extract_all_fields(file_path, language='vie', detailed=True)
    
    if result is None:
        print("Khong the doc file!")
        exit(1)
    
    # Ghi kết quả ra file
    with open('ocr_result.txt', 'w', encoding='utf-8') as f:
        f.write("="*50 + "\n")
        f.write("TOAN BO TEXT TRICH XUAT\n")
        f.write("="*50 + "\n")
        f.write(result['full_text'] + "\n\n")
        
        f.write("="*50 + "\n")
        f.write("TUNG DONG\n")
        f.write("="*50 + "\n")
        for i, line in enumerate(result['lines'], 1):
            f.write(f"{i}. {line}\n")
        
        f.write("\n" + "="*50 + "\n")
        f.write("DO TIN CAY TRUNG BINH\n")
        f.write("="*50 + "\n")
        f.write(f"{result['average_confidence']:.2f}%\n\n")
        
        f.write("="*50 + "\n")
        f.write("CAC FIELD TU DONG PHAT HIEN\n")
        f.write("="*50 + "\n")
        if result['structured_data']:
            for key, value in result['structured_data'].items():
                f.write(f"{key}: {value}\n")
        else:
            f.write("Khong phat hien key-value pairs\n")
    
    print(f"Da ghi ket qua vao file: ocr_result.txt")
    print(f"So dong text: {len(result['lines'])}")
    print(f"Do tin cay TB: {result['average_confidence']:.2f}%")
    print(f"So field phat hien: {len(result['structured_data'])}")
