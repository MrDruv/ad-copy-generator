FROM python:3.11-slim

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    python3-pip python3-cffi python3-brotli libpango-1.0-0 \
    libharfbuzz0b libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libgdk-pixbuf2.0-0 \
    && apt-get clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Start with Gunicorn on the port Render provides
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
