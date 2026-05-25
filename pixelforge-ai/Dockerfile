FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p static/outputs static/cache static/exports

EXPOSE 7860
ENV PORT=7860

CMD ["python", "app.py"]
