FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# requirements.txt khai báo torch+cpu (extra-index) để tránh bản CUDA ~GB
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY kb ./kb
RUN mkdir -p /app/artifacts /app/chroma_data

ENV PYTHONUNBUFFERED=1
EXPOSE 8010

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
