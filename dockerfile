FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

COPY . .

RUN mkdir -p /app/data

RUN which uvicorn && uvicorn --version

CMD ["uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000"]