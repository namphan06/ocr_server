FROM python:3.9-slim

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập biến môi trường cho Tesseract trên Linux
# (Trên Render/Debian, dữ liệu nằm ở /usr/share/tesseract-ocr/5/tessdata hoặc /usr/share/tesseract-ocr/tessdata)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Một số hệ thống Linux tìm ở /usr/share/tessdata, ta tạo symlink để an toàn
RUN ln -s /usr/share/tesseract-ocr/5/tessdata /usr/share/tessdata || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads results && chmod 777 uploads results

EXPOSE 10000
CMD ["python", "ocr_server.py"]