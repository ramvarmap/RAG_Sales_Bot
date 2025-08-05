# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    libaio1 \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create Oracle directory
RUN mkdir -p /opt/oracle/instantclient

# Install Oracle Instant Client (using a more reliable method)
RUN wget -O /tmp/instantclient-basiclite.zip \
    https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip \
    && unzip /tmp/instantclient-basiclite.zip -d /opt/oracle/ \
    && mv /opt/oracle/instantclient_* /opt/oracle/instantclient \
    && rm /tmp/instantclient-basiclite.zip

# Set Oracle environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV PATH=/opt/oracle/instantclient:$PATH

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p gcp_secrets

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Set environment variables for Streamlit in Cloud Run
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["streamlit", "run", "streamlit_app_modular.py", "--server.port=8080", "--server.address=0.0.0.0"] 