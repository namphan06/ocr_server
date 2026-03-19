# Sử dụng Python image mỏng (slim) để tối ưu dung lượng
FROM python:3.9-slim

# Cài đặt các gói hệ thống cần thiết:
# - tesseract-ocr: Công cụ OCR chính
# - tesseract-ocr-vie: Dữ liệu ngôn ngữ Tiếng Việt cho Tesseract
# - tesseract-ocr-eng: Dữ liệu ngôn ngữ Tiếng Anh cho Tesseract
# - poppler-utils: Công cụ để xử lý file PDF (convert sang ảnh)
# - libgl1-mesa-glx & libglib2.0-0: Cần thiết cho OpenCV (opencv-python)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Tạo các thư mục cần thiết để tránh lỗi Permission
RUN mkdir -p uploads results && chmod 777 uploads results

# Render sẽ cung cấp biến môi trường PORT, chúng ta sử dụng nó trong ocr_server.py
# (Mã nguồn ocr_server.py đã được cập nhật để đọc os.environ.get('PORT'))
EXPOSE 10000

# Lệnh khởi chạy server
CMD ["python", "ocr_server.py"]
