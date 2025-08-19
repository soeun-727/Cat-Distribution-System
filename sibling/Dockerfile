#~/HC/Cat-Distribution-System/sibling/Dockerfile
# Sibling Flask 서버 Dockerfile
FROM python:3.11-slim

WORKDIR /sibling

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sibling.py .
COPY templates ./templates

CMD ["python", "sibling.py"]
