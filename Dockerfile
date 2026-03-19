FROM python:3.9-slim-bullseye

# Cài đặt dependencies cần thiết cho Tesseract, Poppler, và OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tessdata

# Set working directory
WORKDIR /app

# Copy requirements và install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ocr_service.py .
COPY ocr_server.py .

# Tạo thư mục uploads và results
RUN mkdir -p uploads results

# Expose port
EXPOSE 5000

# Run server
CMD ["python", "ocr_server.py"]
