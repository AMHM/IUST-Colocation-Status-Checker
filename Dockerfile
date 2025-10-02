# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy script into container
COPY IUST-Colocation-Status-Publisher.py /app/

# Install required packages
RUN pip install --no-cache-dir paho-mqtt ntplib jdatetime pytz

# Expose HTTP server port
EXPOSE 8000

# Run the script
CMD ["python", "IUST-Colocation-Status-Publisher.py"]

