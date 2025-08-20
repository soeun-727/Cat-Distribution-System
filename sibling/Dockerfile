#~/HC/Cat-Distribution-System/sibling/Dockerfile
# Sibling Flask 서버 Dockerfile
FROM python:3.11-slim

# 빌드에 필요한 모든 종속성 설치
# `build-essential` 패키지는 gcc, g++, make 등 기본적인 빌드 도구를 포함합니다.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libevent-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sibling

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY sibling.py .
COPY templates ./templates

CMD ["python", "sibling.py"]
