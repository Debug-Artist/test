FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-10000}"]
