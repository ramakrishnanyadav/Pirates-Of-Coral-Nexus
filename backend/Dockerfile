FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://withcoral.com/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/init_coral.sh
CMD ["/bin/bash", "-c", "./scripts/init_coral.sh && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
