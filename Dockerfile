FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed later for OCR or fonts)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port Streamlit runs on
ENV PORT=8080

EXPOSE 8080

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
