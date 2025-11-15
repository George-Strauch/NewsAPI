# Python + Alpine base
FROM python:3.11-alpine

# Workdir
WORKDIR /app

# Copy project into image
COPY News/ /app/News/
COPY NewsFE/ /app/NewsFE/
COPY src/ /app/src/
COPY api_reqs.txt /app/api_reqs.txt

RUN mkdir -p /opt/news_api
COPY .env /opt/news/

RUN pip install -r /app/News/requirements.txt \
    && pip install -r /app/api_reqs.txt \
    && pip install --no-cache-dir -e /app/News

# Keep src importable
ENV PYTHONPATH=/app/src

# Optional: persist host data at /opt/news
VOLUME ["/opt/news_api/"]

# Entrypoint: bind to all interfaces and a fixed port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
