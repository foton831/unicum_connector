FROM python:3.12-slim
COPY app /app
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
