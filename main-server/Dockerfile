FROM python:3.12-slim
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
COPY server.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "server.py"]