FROM python:3.12-slim
COPY app /app
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=5 CMD curl -f http://localhost:5000/health || exit 1
CMD ["python", "app.py"]
