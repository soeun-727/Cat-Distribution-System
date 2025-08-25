#~/HC/Cat-Distribution-System/Dockerfile
# Main Flask 서버 Dockerfile
FROM python:3.11-slim

# 빌드에 필요한 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libevent-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask-cors

# 앱 소스 복사
COPY . .
# instance 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/instance && chmod 777 /app/instance

# 환경변수 설정 (SECRET_KEY는 docker-compose.yml에서 설정)
ENV FLASK_ENV=production

# 포트 오픈
EXPOSE 727

# 서버 실행
CMD ["python", "app.py"]
