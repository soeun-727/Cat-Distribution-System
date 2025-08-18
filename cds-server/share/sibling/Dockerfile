#~/HC/Cat-Distribution-System/cds-server/share/sibling/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m chall && chown -R chall:chall /app

EXPOSE 5000
USER chall

CMD ["python", "sibling.py"]

