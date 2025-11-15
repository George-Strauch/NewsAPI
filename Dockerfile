# Python + Alpine base
FROM python:3.11-alpine

# Workdir
WORKDIR /app

# Copy project into image
COPY News/ /app/News/
COPY NewsFE/ /app/NewsFE/
COPY src/ /app/src/
COPY api_reqs.txt /app/api_reqs.txt

# Runtime data dir
RUN mkdir -p /opt/news_api

# Copy environment file baked into the image
COPY .env /opt/news/

RUN pip install -r /app/News/requirements.txt \
    && pip install -r /app/api_reqs.txt \
    && pip install --no-cache-dir -e /app/News

# Keep src importable
ENV PYTHONPATH=/app/src

# Optional: persist host data at /opt/news_api
VOLUME ["/opt/news_api/"]

# Document container port (helps tooling; not strictly required)
EXPOSE 8000

# Entrypoint: bind to all interfaces and a fixed port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
