FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY beta_bot ./beta_bot
COPY run_once.py .
CMD ["python", "run_once.py"]
