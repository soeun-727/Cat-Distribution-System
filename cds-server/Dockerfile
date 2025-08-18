#~/HC/Cat-Distribution-System/cds-server/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 프로젝트 파일 복사
COPY ./share /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 권한 분리
RUN useradd -m chall && chown -R chall:chall /app

RUN apt install -y xinetd


EXPOSE 5000
USER chall

CMD ["python", "app.py"]

