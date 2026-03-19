FROM python:3.9-slim

# Cài đặt các gói hệ thống cần thiết
# Thay thế libgl1-mesa-glx bằng libgl1 (tương đương nhưng mới hơn)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập biến môi trường cho Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Tạo symlink để Tesseract linh hoạt hơn trong việc tìm dữ liệu
RUN mkdir -p /usr/share/tessdata && \
    ln -s /usr/share/tesseract-ocr/5/tessdata/* /usr/share/tessdata/ || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads results && chmod 777 uploads results

EXPOSE 10000
CMD ["python", "ocr_server.py"]