FROM python:3.12-slim
WORKDIR /ai
COPY ai/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ai ./ai
EXPOSE 8000
CMD ["uvicorn", "ai.server:app", "--host", "0.0.0.0", "--port", "8000"]
