FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install required system packages
# - ttf-dejavu → Unicode font support for FPDF
# - build-essential → for compiling some Python wheels
RUN apt-get update && apt-get install -y \
    ttf-dejavu \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app to container
COPY . .

# Cloud Run provides PORT env variable, defaulting Streamlit to 8080
ENV PORT=8080

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
