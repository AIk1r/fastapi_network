FROM python:3.10.2

WORKDIR /pythonProject2

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
