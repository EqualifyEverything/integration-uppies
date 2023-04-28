# Use alpine with Python pre-installed
FROM python:3.9-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src /app/src

# Env Variables
ENV APP_PORT 8085

# Set up the proxy environment variables
ENV PROXY_HTTP gluetun:8888
ENV PROXY_HTTPS gluetun:8888

# Rabbit Info
ENV RABBIT_USERNAME=worker_uppies
ENV RABBIT_PASSWORD=pass_the_uppies_please
# ENV RABBIT_HOST
ENV RABBIT_VHOST=gova11y
ENV RABBIT_QUEUE_IN=am_i_up
ENV RABBIT_QUEUE_OUT=i_am_up
ENV RABBIT_QUEUE_ERROR=i_am_down

# Logging Level
ENV LOG_LEVEL INFO

EXPOSE $APP_PORT

# Run the application
CMD ["python", "src/main.py"]
