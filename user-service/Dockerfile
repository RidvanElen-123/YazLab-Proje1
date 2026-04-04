FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# İçeriği komple alıyoruz
COPY . .

# Eğer main.py dosyasını src klasörü içine koyacaksan komut bu şekilde kalmalı:
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]