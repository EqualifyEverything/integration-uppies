# Use alpine with Python pre-installed
FROM python:3.9-alpine

# Create and set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py and other necessary files (if any)
COPY main.py /app/

# Env Variables
ENV APP_PORT 8085

# Set up the proxy environment variables
ENV http_proxy http://glutun:8888
ENV https_proxy http://glutun:8888

# Logging Level
ENV LOG_LEVEL INFO

EXPOSE $APP_PORT

# Run the application
CMD ["python", "main.py"]
