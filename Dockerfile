FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip list

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]