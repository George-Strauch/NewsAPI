# Python + Alpine base
FROM python:3.11-alpine

# Workdir
WORKDIR /app

# Copy project into image
COPY News/ /app/News/
COPY src/ /app/src/

RUN mkdir -p /opt/news
COPY .env /opt/news/


RUN pip install -r /app/News/requirements.txt \
    && pip install --no-cache-dir -e /app/News

# Keep src importable
ENV PYTHONPATH=/app/src

# Optional: persist host data at /opt/news
VOLUME ["/opt/news/"]

# Entrypoint
ENTRYPOINT ["python", "src/main.py"]
