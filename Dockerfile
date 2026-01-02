FROM python:3.11-slim

# Install system dependencies for WeasyPrint
# Note: we use --no-install-recommends to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    shared-mime-info \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start with Gunicorn on the port Render provides
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
