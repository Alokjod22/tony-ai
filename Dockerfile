FROM python:3.11-slim

WORKDIR /app

# Install system audio and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak \
    ffmpeg \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
