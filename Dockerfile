FROM python:3.9

WORKDIR /app

# Install netcat for the entrypoint healthcheck
RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

# Copy requirements from user_service directory
COPY user_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY user_service/app /app/app

# Copy shell scripts
COPY user_service/entrypoint.sh .
COPY user_service/migrations.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]