FROM python:3.10-slim

# 1. No system dependencies needed for just Flask + Storage
WORKDIR /app

COPY . .

# 2. Install only Flask and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# 3. Start the server
# Note: Ensure app:app matches your filename (app.py) and flask instance name (app)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "4", "--timeout", "120", "app:app"]
