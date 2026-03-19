"""
OCR Service API
Trích xuất text từ ảnh/PDF để tích hợp vào Flutter App
"""

import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import os
import sys
import json

# Cấu hình đường dẫn Tesseract
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\THINKBOOK\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
else:  # Linux (Render)
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

# Cấu hình đường dẫn Poppler
if os.name == 'nt':  # Windows
    current_dir = os.path.dirname(os.path.abspath(__file__))
    poppler_path = os.path.join(current_dir, 'poppler-25.12.0', 'Library', 'bin')
    os.environ['PATH'] = poppler_path + ';' + os.environ['PATH']
else:  # Linux (Render)
    # Trên Render (Linux), Poppler được cài qua system package
    pass


def preprocess_image(img, scale=2):
    """Tiền xử lý ảnh để cải thiện OCR"""
    img_cv = np.array(img)
    
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_cv
    
    # Phóng to ảnh
    h, w = gray.shape
    gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
    
    # Thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Khử nhiễu
    denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
    
    # Morphology
    kernel = np.ones((1,1), np.uint8)
    denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
    
    return Image.fromarray(denoised)


def extract_text_from_pdf(pdf_path, language='eng', preprocess=True):
    """Trích xuất text từ PDF"""
    try:
        pages = convert_from_path(pdf_path, dpi=200)
        
        all_text = []
        for i, page in enumerate(pages, 1):
            if preprocess:
                page = preprocess_image(page, scale=2)
            
            text = pytesseract.image_to_string(page, lang=language, config='--psm 3 --oem 3')
            all_text.append({
                'page': i,
                'text': text.strip()
            })
        
        return {
            'success': True,
            'pages': all_text,
            'full_text': '\n\n'.join([p['text'] for p in all_text])
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def extract_text_from_image(image_path, language='eng', preprocess=True):
    """Trích xuất text từ ảnh"""
    try:
        img = Image.open(image_path)
        
        if preprocess:
            img = preprocess_image(img, scale=2)
        
        text = pytesseract.image_to_string(img, lang=language, config='--psm 3 --oem 3')
        
        return {
            'success': True,
            'text': text.strip(),
            'lines': text.strip().split('\n')
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def extract_structured_data(file_path, language='eng'):
    """
    Trích xuất dữ liệu có cấu trúc từ file
    Tự động phát hiện các field: email, phone, links, key-value pairs
    """
    import re
    
    ext = os.path.splitext(file_path)[1].lower()
    
    # Xử lý theo loại file
    if ext == '.pdf':
        result = extract_text_from_pdf(file_path, language)
    else:
        result = extract_text_from_image(file_path, language)
    
    if not result.get('success'):
        return result
    
    text = result.get('full_text', result.get('text', ''))
    
    # Phát hiện các pattern
    data = {
        'success': True,
        'full_text': text,
        'lines': [l.strip() for l in text.split('\n') if l.strip()],
        'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
        'phones': re.findall(r'\b\d{9,10}\b', text),
        'links': re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text),
        'key_value_pairs': {}
    }
    
    # Phát hiện key-value pairs
    for line in data['lines']:
        # Pattern: "Key: Value"
        match = re.match(r'^([^:=]+):\s*(.+)$', line)
        if match:
            data['key_value_pairs'][match.group(1).strip()] = match.group(2).strip()
        
        # Pattern: "Key - Value"
        match = re.match(r'^([^-]+)-\s*(.+)$', line)
        if match:
            data['key_value_pairs'][match.group(1).strip()] = match.group(2).strip()
    
    return data


def process_file(file_path, language='eng', output_json=None):
    """
    Xử lý file và trả về kết quả JSON
    
    Args:
        file_path: đường dẫn file (ảnh hoặc PDF)
        language: 'eng' hoặc 'vie'
        output_json: đường dẫn file JSON để lưu kết quả (optional)
    
    Returns:
        dict chứa kết quả OCR
    """
    if not os.path.isfile(file_path):
        return {'success': False, 'error': 'File not found'}
    
    ext = os.path.splitext(file_path)[1].lower()
    valid_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.pdf']
    
    if ext not in valid_exts:
        return {'success': False, 'error': f'Invalid file type: {ext}'}
    
    # Trích xuất dữ liệu
    result = extract_structured_data(file_path, language)
    
    # Thêm metadata
    result['file_path'] = file_path
    result['file_name'] = os.path.basename(file_path)
    result['file_type'] = ext[1:]
    result['language'] = language
    
    # Lưu vào file JSON nếu được yêu cầu
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR Service - Extract text from images/PDF')
    parser.add_argument('file', help='Path to file')
    parser.add_argument('--lang', default='eng', help='Language (eng or vie)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty output')
    
    args = parser.parse_args()
    
    result = process_file(args.file, args.lang, args.output)
    
    if args.output:
        print(f"Saved to: {args.output}")
    else:
        # Write to stdout as UTF-8
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None).encode('utf-8').decode('utf-8'))
