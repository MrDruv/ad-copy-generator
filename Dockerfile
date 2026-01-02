FROM python:3.11-slim

# Install ONLY the bare essentials for PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    weasyprint \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
