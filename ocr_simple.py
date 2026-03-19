import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import os

# Cấu hình đường dẫn Tesseract (trong thư mục dự án)
current_dir = os.path.dirname(os.path.abspath(__file__))
pytesseract.pytesseract.tesseract_cmd = os.path.join(current_dir, 'tesseract.exe')


def extract_text_from_image(image_path, language='vie', preprocess=True):
    """
    Trích xuất TẤT CẢ text từ file ảnh
    
    Args:
        image_path: đường dẫn file ảnh
        language: ngôn ngữ OCR ('eng', 'vie', 'eng+vie')
        preprocess: có tiền xử lý ảnh không
    
    Returns:
        text: toàn bộ text trích xuất được
    """
    try:
        img = Image.open(image_path)
        
        if preprocess:
            img = preprocess_image(img)
        
        config = '--psm 6'
        text = pytesseract.image_to_string(img, lang=language, config=config)
        
        return text.strip()
    
    except FileNotFoundError:
        print(f"Khong tim thay file: {image_path}")
        return None
    except Exception as e:
        print(f"Loi: {str(e)}")
        return None


def preprocess_image(img):
    """
    Tiền xử lý ảnh để cải thiện độ chính xác OCR
    """
    img_cv = np.array(img)
    
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_cv
    
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
    
    return Image.fromarray(denoised)


def extract_all_text_with_confidence(image_path, language='vie'):
    """
    Trích xuất text kèm độ tin cậy cho từng từ
    """
    try:
        img = Image.open(image_path)
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


def extract_key_value_pairs(image_path, language='vie'):
    """
    Tự động phát hiện các cặp key-value từ text trong ảnh
    """
    text = extract_text_from_image(image_path, language)
    
    if not text:
        return {'full_text': '', 'lines': [], 'key_value_pairs': {}}
    
    key_value_pairs = {}
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        match = re.match(r'^([^:=]+):\s*(.+)$', line)
        if match:
            key_value_pairs[match.group(1).strip()] = match.group(2).strip()
            continue
        
        match = re.match(r'^([^=]+)=\s*(.+)$', line)
        if match:
            key_value_pairs[match.group(1).strip()] = match.group(2).strip()
            continue
        
        match = re.match(r'^([^-]+)-\s*(.+)$', line)
        if match:
            key_value_pairs[match.group(1).strip()] = match.group(2).strip()
    
    return {
        'full_text': text,
        'lines': [l.strip() for l in lines if l.strip()],
        'key_value_pairs': key_value_pairs
    }


def extract_all_fields(image_path, language='vie', detailed=True):
    """
    Trích xuất TẤT CẢ thông tin từ ảnh
    """
    result = {
        'full_text': '',
        'lines': [],
        'words': [],
        'average_confidence': 0,
        'structured_data': {}
    }
    
    text = extract_text_from_image(image_path, language)
    if text:
        result['full_text'] = text
        result['lines'] = [l.strip() for l in text.split('\n') if l.strip()]
    
    if detailed:
        word_data = extract_all_text_with_confidence(image_path, language)
        if word_data:
            result['words'] = word_data
            confidences = [w['confidence'] for w in word_data]
            result['average_confidence'] = sum(confidences) / len(confidences) if confidences else 0
    
    kv_data = extract_key_value_pairs(image_path, language)
    if kv_data:
        result['structured_data'] = kv_data['key_value_pairs']
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Nhap duong dan file anh: ").strip()
    
    if not image_path or not os.path.isfile(image_path):
        print("File khong ton tai!")
        exit(1)
    
    result = extract_all_fields(image_path, language='vie', detailed=True)
    
    if not result or not result['full_text']:
        print("Khong the doc file anh!")
        exit(1)
    
    print("\n" + "="*50)
    print("TOAN BO TEXT TRICH XUAT")
    print("="*50)
    print(result['full_text'])
    
    print("\n" + "="*50)
    print("CÁC FIELD Tự ĐỘNG PHÁT HIỆN")
    print("="*50)
    if result['structured_data']:
        for key, value in result['structured_data'].items():
            print(f"{key}: {value}")
    else:
        print("Khong phat hien key-value pairs")
