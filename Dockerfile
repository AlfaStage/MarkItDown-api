FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (PDF, Office, Imagens e OCR)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libtesseract-dev \
    pandoc \
    antiword \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
