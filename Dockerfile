#~/HC/Cat-Distribution-System/Dockerfile
# Main Flask 서버 Dockerfile
# 베이스 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY . .

# instance 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/instance && chmod 777 /app/instance

# 환경변수 설정 (선택, SECRET_KEY 외부에서 전달 가능)
ENV FLASK_ENV=production
ENV SECRET_KEY=supersecretkey  # 실제 배포 시 안전하게 관리

# 포트 오픈
EXPOSE 5000

# 서버 실행
CMD ["python", "app.py"]
