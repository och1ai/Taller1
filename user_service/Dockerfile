FROM python:3.9

WORKDIR /app

# Install netcat for the entrypoint healthcheck
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
COPY entrypoint.sh .
COPY migrations.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
