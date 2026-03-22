FROM python:3.10-slim

WORKDIR /srv

# Минимальные зависимости для работы с картинками
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Flask, PyMuPDF, OpenCV и EasyOCR
RUN pip install --no-cache-dir flask pymupdf opencv-python-headless easyocr

COPY ml.py /srv/

EXPOSE 7777

ENTRYPOINT ["python", "ml.py"]
